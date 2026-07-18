import { env, exports } from "cloudflare:workers";
import { describe, expect, it } from "vitest";
import { toBytes } from "../src/canonical";
import { signEnvelope, verifyWebhookHmac } from "../src/crypto";
import { evaluateDeterministically } from "../src/evaluator";
import { attestIdentity, githubJson, publishShadowCheck } from "../src/github";
import { buildReceipt, buildShadowPermit, signDecision, verifyShadowPermit } from "../src/permit";
import { claimReplayKey } from "../src/replay";
import type { EvaluationRequest, EvaluatorConfig, ExactSubject, ShadowPermit, SignedEnvelope } from "../src/types";
import { subjectFromWebhook } from "../src/webhook";

const HASH = "a".repeat(64);
const SHA = "b".repeat(40);
const CONFIG: EvaluatorConfig = {
  expectedAppId: "9000001",
  expectedInstallationId: "9000002",
  allowedRepositories: new Set(["Noetfield-Systems/sina-governance-SSOT", "Noetfield-Systems/sg-canary"]),
  expectedPolicyHash: HASH,
  expectedSchemaHash: HASH,
  expectedEvaluatorHash: HASH,
  expectedWorkerVersion: "sg-v2-shadow-v0.1.0",
  expectedSigningKeyId: "sg-shadow-test-key",
};

function request(overrides: Partial<EvaluationRequest> = {}): EvaluationRequest {
  return {
    app_id: "9000001",
    installation_id: "9000002",
    repository: "Noetfield-Systems/sina-governance-SSOT",
    commit_sha: SHA,
    action: "evaluate_pull_request",
    target: "Noetfield SG / P0 Authority",
    artifact_hash: HASH,
    policy_hash: HASH,
    schema_hash: HASH,
    evaluator_hash: HASH,
    worker_version: "sg-v2-shadow-v0.1.0",
    signing_key_id: "sg-shadow-test-key",
    nonce: "delivery:1234567890abcdef",
    event: "pull_request",
    delivery_id: "delivery:1234567890abcdef",
    ...overrides,
  };
}

function exactSubject(overrides: Partial<EvaluationRequest> = {}): ExactSubject {
  const value = request(overrides);
  return {
    app_id: value.app_id,
    installation_id: value.installation_id,
    repository: value.repository,
    commit_sha: value.commit_sha,
    action: value.action,
    target: value.target,
    artifact_hash: value.artifact_hash,
    policy_hash: value.policy_hash,
    schema_hash: value.schema_hash,
    evaluator_hash: value.evaluator_hash,
    worker_version: value.worker_version,
    signing_key_id: value.signing_key_id,
    nonce: value.nonce,
  };
}

async function ecdsaJwks(): Promise<{ privateJwk: string; publicJwk: string }> {
  const pair = await crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
  if (!("privateKey" in pair)) throw new TypeError("ECDSA key generation did not return a key pair");
  return {
    privateJwk: JSON.stringify(await crypto.subtle.exportKey("jwk", pair.privateKey)),
    publicJwk: JSON.stringify(await crypto.subtle.exportKey("jwk", pair.publicKey)),
  };
}

async function rsaPem(): Promise<string> {
  const pair = await crypto.subtle.generateKey(
    { name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
    true,
    ["sign", "verify"],
  );
  if (!("privateKey" in pair)) throw new TypeError("RSA key generation did not return a key pair");
  const exported = await crypto.subtle.exportKey("pkcs8", pair.privateKey);
  if (!(exported instanceof ArrayBuffer)) throw new TypeError("PKCS8 export did not return bytes");
  const bytes = new Uint8Array(exported);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  const body = btoa(binary).match(/.{1,64}/g)?.join("\n") ?? "";
  return `-----BEGIN PRIVATE KEY-----\n${body}\n-----END PRIVATE KEY-----`;
}

function response(body: unknown, status = 200): Response {
  const text = JSON.stringify(body);
  return new Response(text, { status, headers: { "content-type": "application/json", "content-length": String(toBytes(text).length) } });
}

describe("GitHub webhook authentication", () => {
  it("matches GitHub's published HMAC-SHA256 vector and rejects tampering", async () => {
    const body = toBytes("Hello, World!");
    const signature = "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17";
    expect(await verifyWebhookHmac("It's a Secret to Everybody", signature, body.buffer)).toBe(true);
    expect(await verifyWebhookHmac("It's a Secret to Everybody", signature, toBytes("tampered").buffer)).toBe(false);
    expect(await verifyWebhookHmac("It's a Secret to Everybody", null, body.buffer)).toBe(false);
  });
});

describe("deterministic P0 evaluation", () => {
  it("passes only an exact non-mutating subject", () => {
    expect(evaluateDeterministically(request(), CONFIG)).toMatchObject({ verdict: "PASS", reasons: [] });
  });

  it.each([
    ["legacy App", { app_id: "4179901" }],
    ["Motor spoof", { app_id: "4275961" }],
    ["wrong installation", { installation_id: "1" }],
    ["uninstalled repository", { repository: "public/uninstalled" }],
    ["self approval", { action: "commission_sg", target: "noetfield-sg-authority" }],
    ["production deploy", { action: "deploy" }],
  ])("blocks %s", (_name, overrides) => {
    expect(evaluateDeterministically(request(overrides), CONFIG).verdict).toBe("BLOCKED");
  });

  it("fails wrong SHA and evidence pins", () => {
    const result = evaluateDeterministically(request({ commit_sha: "bad", artifact_hash: "bad" }), CONFIG);
    expect(result.verdict).toBe("FAIL");
    expect(result.reasons.join(" ")).toContain("commit_sha");
  });
});

describe("merge_group exact subject", () => {
  it("uses merge_group.head_sha rather than a pull request SHA", async () => {
    const payload = {
      repository: { full_name: "Noetfield-Systems/sina-governance-SSOT" },
      installation: { id: 9000002 },
      merge_group: { head_sha: SHA },
      pull_request: { head: { sha: "c".repeat(40) } },
    };
    const workerEnv = {
      EXPECTED_APP_ID: "9000001",
      EXPECTED_CHECK_NAME: "Noetfield SG / P0 Authority",
      POLICY_HASH: HASH,
      SCHEMA_HASH: HASH,
      EVALUATOR_HASH: HASH,
      WORKER_VERSION: "sg-v2-shadow-v0.1.0",
      SG_SIGNING_KEY_ID: "sg-shadow-test-key",
    } satisfies Pick<Env, "EXPECTED_APP_ID" | "EXPECTED_CHECK_NAME" | "POLICY_HASH" | "SCHEMA_HASH" | "EVALUATOR_HASH" | "WORKER_VERSION" | "SG_SIGNING_KEY_ID">;
    const body = toBytes(JSON.stringify(payload)).buffer;
    const subject = await subjectFromWebhook("merge_group", "delivery:merge-group-0001", payload, body, workerEnv as Env);
    expect(subject.commit_sha).toBe(SHA);
    expect(subject.action).toBe("evaluate_merge_group");
  });
});

describe("signed exact-subject shadow permit", () => {
  it("verifies signature and exact subject but remains non-enforceable", async () => {
    const keys = await ecdsaJwks();
    const evaluation = evaluateDeterministically(request(), CONFIG);
    const receipt = buildReceipt(request(), evaluation, new Date(Date.now() - 1_000));
    const permit = buildShadowPermit(receipt);
    expect(permit).not.toBeNull();
    const signed = await signDecision(receipt, permit, keys.privateJwk, "sg-shadow-test-key");
    const verified = await verifyShadowPermit(signed.permit!, keys.publicJwk, exactSubject());
    expect(verified).toMatchObject({ ok: true, code: "VALID_SHADOW_PERMIT" });
    expect(signed.permit!.payload).toMatchObject({ mode: "SHADOW", enforceable: false, authorization: "NONE" });
  });

  it("rejects signature tamper, wrong subject, and expiry", async () => {
    const keys = await ecdsaJwks();
    const now = new Date(Date.now() - 10 * 60_000);
    const receipt = buildReceipt(request(), evaluateDeterministically(request(), CONFIG), now);
    const permit = buildShadowPermit(receipt)!;
    const envelope = await signEnvelope(permit, keys.privateJwk, "sg-shadow-test-key");
    const wrongSubject: ExactSubject = exactSubject({ commit_sha: "c".repeat(40) });
    expect(await verifyShadowPermit(envelope, keys.publicJwk, wrongSubject)).toMatchObject({ code: "BLOCKED_SUBJECT_MISMATCH" });
    expect(await verifyShadowPermit(envelope, keys.publicJwk, exactSubject())).toMatchObject({ code: "BLOCKED_EXPIRED_SG_PERMIT" });
    const tampered: SignedEnvelope<ShadowPermit> = { ...envelope, payload: { ...envelope.payload, authorization: "NONE", subject: wrongSubject } };
    expect(await verifyShadowPermit(tampered, keys.publicJwk, wrongSubject)).toMatchObject({ code: "BLOCKED_INVALID_SG_PERMIT" });
    const wrongKeyId = { ...envelope, signature: { ...envelope.signature, key_id: "wrong-key" } };
    expect(await verifyShadowPermit(wrongKeyId, keys.publicJwk, exactSubject())).toMatchObject({ code: "BLOCKED_INVALID_SG_PERMIT" });
  });
});

describe("strong replay rejection", () => {
  it("atomically rejects a repeated GitHub delivery", async () => {
    const key = `delivery:${crypto.randomUUID()}`;
    const expiry = Date.now() + 60_000;
    expect(await claimReplayKey(env.REPLAY_GUARD, "delivery", key, expiry)).toBe(true);
    expect(await claimReplayKey(env.REPLAY_GUARD, "delivery", key, expiry)).toBe(false);
  });

  it("atomically rejects a repeated permit nonce", async () => {
    const key = `permit:${crypto.randomUUID()}`;
    const expiry = Date.now() + 60_000;
    expect(await claimReplayKey(env.REPLAY_GUARD, "permit", key, expiry)).toBe(true);
    expect(await claimReplayKey(env.REPLAY_GUARD, "permit", key, expiry)).toBe(false);
  });
});

describe("authenticated GitHub identity and expected-source check", () => {
  it("never falls back to unauthenticated GitHub access", async () => {
    let calls = 0;
    const fakeFetch: typeof fetch = async () => { calls += 1; return response({}); };
    await expect(githubJson("/app", "", {}, fakeFetch)).rejects.toThrow("public fallback is forbidden");
    expect(calls).toBe(0);
  });

  it("proves exact App, organization installation, and repository membership", async () => {
    const calls: Array<{ url: string; authorization: string | null }> = [];
    const fakeFetch: typeof fetch = async (input, init) => {
      const url = String(input);
      const authorization = new Headers(init?.headers).get("authorization");
      calls.push({ url, authorization });
      if (url.endsWith("/app")) return response({
        id: 9000001,
        slug: "noetfield-sg-authority",
        owner: { login: "Noetfield-Systems" },
        permissions: {
          actions: "read",
          checks: "write",
          contents: "read",
          metadata: "read",
          pull_requests: "read",
          statuses: "write",
        },
      });
      if (url.endsWith("/orgs/Noetfield-Systems/installation")) return response({ id: 9000002 });
      if (url.endsWith("/app/installations/9000002/access_tokens")) return response({ token: "installation-token" });
      return response({ repositories: [
        { full_name: "Noetfield-Systems/sina-governance-SSOT" },
        { full_name: "Noetfield-Systems/sg-canary" },
      ] });
    };
    const identityEnv = {
      EXPECTED_APP_ID: "9000001",
      EXPECTED_INSTALLATION_ID: "9000002",
      EXPECTED_APP_SLUG: "noetfield-sg-authority",
      EXPECTED_ORG: "Noetfield-Systems",
      ALLOWED_REPOSITORIES: JSON.stringify(["Noetfield-Systems/sina-governance-SSOT", "Noetfield-Systems/sg-canary"]),
      GITHUB_APP_PRIVATE_KEY: await rsaPem(),
    } as Env;
    const proof = await attestIdentity(identityEnv, fakeFetch);
    expect(proof).toMatchObject({ exact_identity: true, public_fallback_used: false, app_id: "9000001", installation_id: "9000002" });
    expect(calls).toHaveLength(4);
    expect(calls.every((call) => call.authorization?.startsWith("Bearer "))).toBe(true);
  });

  it("uses the exact expected Check Run name and stays disabled by default", async () => {
    let calls = 0;
    const fakeFetch: typeof fetch = async () => { calls += 1; return response({}); };
    const result = await publishShadowCheck(env, "Noetfield-Systems/sina-governance-SSOT", SHA, "success", "PASS", fakeFetch);
    expect(result).toEqual({ published: false, reason: "shadow check publishing disabled" });
    expect(calls).toBe(0);
    expect(env.EXPECTED_CHECK_NAME).toBe("Noetfield SG / P0 Authority");
  });

  it("accepts a published Check Run only from the exact candidate App", async () => {
    const bodies: string[] = [];
    const fakeFetch: typeof fetch = async (input, init) => {
      const url = String(input);
      if (url.endsWith("/access_tokens")) return response({ token: "installation-token" });
      bodies.push(String(init?.body));
      return response({ id: 123, app: { id: 9000001 } });
    };
    const checkEnv = {
      CHECK_RUN_PUBLISH_ENABLED: "true",
      EXPECTED_APP_ID: "9000001",
      EXPECTED_INSTALLATION_ID: "9000002",
      EXPECTED_CHECK_NAME: "Noetfield SG / P0 Authority",
      ALLOWED_REPOSITORIES: JSON.stringify(["Noetfield-Systems/sina-governance-SSOT"]),
      GITHUB_APP_PRIVATE_KEY: await rsaPem(),
    } as Env;
    const result = await publishShadowCheck(
      checkEnv,
      "Noetfield-Systems/sina-governance-SSOT",
      SHA,
      "success",
      "PASS",
      fakeFetch,
    );
    expect(result).toEqual({ published: true, check_run_id: "123" });
    expect(JSON.parse(bodies[0]!)).toMatchObject({
      name: "Noetfield SG / P0 Authority",
      head_sha: SHA,
      conclusion: "success",
    });
  });
});

describe("non-commissioned Worker surface", () => {
  it("reports shadow-only health and keeps webhook disabled", async () => {
    const health = await exports.default.fetch("https://shadow.test/health");
    expect(await health.json()).toMatchObject({ mode: "SHADOW", sg_runtime: "NOT_COMMISSIONED", enforcement_enabled: false });
    const webhook = await exports.default.fetch("https://shadow.test/webhook/github", { method: "POST", body: "{}" });
    expect(webhook.status).toBe(503);
    expect(await webhook.json()).toMatchObject({ code: "SG_V2_SHADOW_WEBHOOK_DISABLED" });
  });
});
