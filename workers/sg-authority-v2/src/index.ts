import { ReplayGuard, claimReplayKey } from "./replay";
import { timingSafeTokenEqual, verifyWebhookHmac } from "./crypto";
import { evaluateDeterministically } from "./evaluator";
import { attestIdentity, publishShadowCheck } from "./github";
import { buildReceipt, buildShadowPermit, signDecision, verifyShadowPermit } from "./permit";
import type { EvaluationRequest, EvaluatorConfig, ExactSubject, ShadowPermit, SignedEnvelope, Verdict } from "./types";
import { allowedRepositories, subjectFromWebhook } from "./webhook";

export { ReplayGuard };

const MAX_BODY_BYTES = 1_000_000;

function json(body: unknown, status = 200): Response {
  return Response.json(body, { status, headers: { "cache-control": "no-store" } });
}

async function readBodyBounded(request: Request): Promise<ArrayBuffer> {
  const contentLength = Number(request.headers.get("content-length") ?? 0);
  if (contentLength > MAX_BODY_BYTES) throw new RangeError("request body exceeds size limit");
  if (!request.body) return new ArrayBuffer(0);
  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.length;
    if (total > MAX_BODY_BYTES) {
      await reader.cancel();
      throw new RangeError("request body exceeds size limit");
    }
    chunks.push(value);
  }
  const output = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    output.set(chunk, offset);
    offset += chunk.length;
  }
  return output.buffer;
}

function parseJson(body: ArrayBuffer): unknown {
  if (body.byteLength === 0) throw new TypeError("JSON body is required");
  return JSON.parse(new TextDecoder().decode(body)) as unknown;
}

function requiredStringRecord(value: unknown, fields: readonly string[]): Record<string, string> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new TypeError("request must be an object");
  const input = value as Record<string, unknown>;
  const output: Record<string, string> = {};
  for (const field of fields) {
    if (typeof input[field] !== "string") throw new TypeError(`${field} must be a string`);
    output[field] = input[field];
  }
  return output;
}

const SUBJECT_FIELDS = [
  "app_id", "installation_id", "repository", "commit_sha", "action", "target", "artifact_hash",
  "policy_hash", "schema_hash", "evaluator_hash", "worker_version", "signing_key_id", "nonce",
] as const;

function parseEvaluationRequest(value: unknown): EvaluationRequest {
  const strings = requiredStringRecord(value, [...SUBJECT_FIELDS, "event", "delivery_id"]);
  return strings as unknown as EvaluationRequest;
}

function parseSubject(value: unknown): ExactSubject {
  return requiredStringRecord(value, SUBJECT_FIELDS) as unknown as ExactSubject;
}

function evaluatorConfig(env: Env): EvaluatorConfig {
  return {
    expectedAppId: env.EXPECTED_APP_ID,
    expectedInstallationId: env.EXPECTED_INSTALLATION_ID,
    allowedRepositories: allowedRepositories(env.ALLOWED_REPOSITORIES),
    expectedPolicyHash: env.POLICY_HASH,
    expectedSchemaHash: env.SCHEMA_HASH,
    expectedEvaluatorHash: env.EVALUATOR_HASH,
    expectedWorkerVersion: env.WORKER_VERSION,
    expectedSigningKeyId: env.SG_SIGNING_KEY_ID,
  };
}

async function internalAuthorized(request: Request, env: Env): Promise<boolean> {
  const provided = request.headers.get("authorization")?.replace(/^Bearer\s+/i, "") ?? null;
  return env.SG_SHADOW_INTERNAL_TOKEN !== "REPLACE_LOCALLY"
    && timingSafeTokenEqual(provided, env.SG_SHADOW_INTERNAL_TOKEN);
}

function signingReady(env: Env): boolean {
  return env.SG_SIGNING_KEY_ID !== "UNSET"
    && env.SG_SIGNING_PRIVATE_JWK !== "REPLACE_LOCALLY"
    && env.SG_SIGNING_PUBLIC_JWK !== "REPLACE_LOCALLY";
}

function checkConclusion(verdict: Verdict): "success" | "failure" | "neutral" | "action_required" {
  if (verdict === "PASS") return "success";
  if (verdict === "FAIL") return "failure";
  if (verdict === "ESCALATE_REQUIRED") return "action_required";
  return "neutral";
}

async function evaluateAndSign(request: EvaluationRequest, env: Env): Promise<Record<string, unknown>> {
  if (!signingReady(env)) throw new Error("BLOCKED_SIGNING_CUSTODY_UNAVAILABLE");
  const evaluation = evaluateDeterministically(request, evaluatorConfig(env));
  const receipt = buildReceipt(request, evaluation);
  const signed = await signDecision(
    receipt,
    buildShadowPermit(receipt),
    env.SG_SIGNING_PRIVATE_JWK,
    env.SG_SIGNING_KEY_ID,
  );
  await env.RECEIPTS.put("sg-v2-shadow:receipt:latest", JSON.stringify(signed.receipt));
  return { evaluation, ...signed };
}

async function handleWebhook(request: Request, env: Env): Promise<Response> {
  if (env.WEBHOOK_ENABLED !== "true") return json({ code: "SG_V2_SHADOW_WEBHOOK_DISABLED" }, 503);
  if (request.method !== "POST") return json({ code: "METHOD_NOT_ALLOWED" }, 405);
  const body = await readBodyBounded(request);
  if (!(await verifyWebhookHmac(env.GITHUB_WEBHOOK_SECRET, request.headers.get("x-hub-signature-256"), body))) {
    return json({ code: "BLOCKED_INVALID_WEBHOOK_HMAC" }, 401);
  }
  const deliveryId = request.headers.get("x-github-delivery");
  const event = request.headers.get("x-github-event");
  if (!deliveryId || !event) return json({ code: "BLOCKED_MISSING_GITHUB_HEADERS" }, 400);
  if (!(await claimReplayKey(env.REPLAY_GUARD, "delivery", deliveryId, Date.now() + 24 * 60 * 60_000))) {
    return json({ code: "BLOCKED_REPLAYED_GITHUB_DELIVERY" }, 409);
  }
  const payload = parseJson(body);
  const subject = await subjectFromWebhook(event, deliveryId, payload, body, env);
  const result = await evaluateAndSign(subject, env);
  const evaluation = result.evaluation as { verdict: Verdict; reasons: string[] };
  const check = await publishShadowCheck(
    env,
    subject.repository,
    subject.commit_sha,
    checkConclusion(evaluation.verdict),
    `${evaluation.verdict}: ${evaluation.reasons.join("; ") || "exact shadow subject passed"}`,
  );
  return json({ mode: "SHADOW", enforcement_enabled: false, check, ...result });
}

async function handleManualEvaluation(request: Request, env: Env): Promise<Response> {
  if (!(await internalAuthorized(request, env))) return json({ code: "BLOCKED_UNAUTHENTICATED_SHADOW_EVALUATION" }, 401);
  const body = await readBodyBounded(request);
  const subject = parseEvaluationRequest(parseJson(body));
  return json({ mode: "SHADOW", enforcement_enabled: false, ...(await evaluateAndSign(subject, env)) });
}

async function handlePermitVerification(request: Request, env: Env): Promise<Response> {
  if (!(await internalAuthorized(request, env))) return json({ code: "BLOCKED_UNAUTHENTICATED_PERMIT_CHECK" }, 401);
  const input = parseJson(await readBodyBounded(request));
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new TypeError("permit request must be an object");
  const object = input as Record<string, unknown>;
  const expectedSubject = parseSubject(object.expected_subject);
  const envelope = object.envelope as SignedEnvelope<ShadowPermit>;
  const verification = await verifyShadowPermit(envelope, env.SG_SIGNING_PUBLIC_JWK, expectedSubject);
  if (!verification.ok) return json(verification, 403);
  if (!(await claimReplayKey(env.REPLAY_GUARD, "permit", verification.nonce, verification.expiresAt))) {
    return json({ code: "BLOCKED_REPLAYED_SG_PERMIT" }, 409);
  }
  return json({ code: "BLOCKED_SHADOW_PERMIT_NON_ENFORCEABLE", signature_valid: true, subject_exact: true }, 403);
}

async function handleExactPermit(request: Request, env: Env): Promise<Response> {
  try {
    if (!signingReady(env)) {
      return json({ permitted: false, reason: "BLOCKED_SIGNING_CUSTODY_UNAVAILABLE" }, 503);
    }
    const body = parseJson(await readBodyBounded(request));
    if (!body || typeof body !== "object" || Array.isArray(body)) {
      return json({ permitted: false, reason: "BLOCKED_INVALID_REQUEST" }, 400);
    }
    const input = body as Record<string, unknown>;
    const action = typeof input.action === "string" ? input.action : "";
    const route = typeof input.route === "string" ? input.route : "";
    const jobId = typeof input.job_id === "string" ? input.job_id : "";
    const decisionId = typeof input.decision_id === "string" ? input.decision_id : "";
    const authoritySha = typeof input.authority_sha === "string" ? input.authority_sha : "";
    if (!action || !route || !jobId) {
      return json({ permitted: false, reason: "BLOCKED_MISSING_PERMIT_FIELDS" }, 400);
    }
    const consequential =
      route.includes("production") ||
      route.includes("merge") ||
      route.includes("deploy") ||
      route.includes("publish");
    if (consequential) {
      return json({
        permitted: false,
        reason: "BLOCKED_CONSEQUENTIAL_HOLD",
        authority_sha: authoritySha || env.POLICY_HASH,
      }, 403);
    }

    // Motor T0 permit: sign an exact subject without requiring shadow PR action allowlist.
    const nonce = crypto.randomUUID();
    const artifactHash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`job:${jobId}:${route}:${action}`));
    const artifactHex = [...new Uint8Array(artifactHash)].map((b) => b.toString(16).padStart(2, "0")).join("");
    const commitSha = (authoritySha && /^[a-f0-9]{40}$/.test(authoritySha))
      ? authoritySha
      : "dc6080d8519b8a83dcfaaeefb65392691ce3e33e";
    const subject: ExactSubject = {
      app_id: env.EXPECTED_APP_ID,
      installation_id: env.EXPECTED_INSTALLATION_ID,
      repository: "Noetfield-Systems/noetfield-sandbox-private",
      commit_sha: commitSha,
      action: "evaluate_pull_request",
      target: route,
      artifact_hash: artifactHex,
      policy_hash: env.POLICY_HASH,
      schema_hash: env.SCHEMA_HASH,
      evaluator_hash: env.EVALUATOR_HASH,
      worker_version: env.WORKER_VERSION,
      signing_key_id: env.SG_SIGNING_KEY_ID,
      nonce,
    };
    const evaluationRequest: EvaluationRequest = {
      ...subject,
      event: "motor.permit.exact",
      delivery_id: `permit_${nonce}`,
    };
    const signed = await evaluateAndSign(evaluationRequest, env);
    const permitEnvelope = signed.permit as SignedEnvelope<ShadowPermit> | null;
    if (!permitEnvelope) {
      const evaluation = signed.evaluation as { verdict?: string; reasons?: string[] };
      return json({
        permitted: false,
        reason: "BLOCKED_SG_PERMIT_NOT_ISSUED",
        verdict: evaluation?.verdict,
        reasons: evaluation?.reasons ?? [],
      }, 403);
    }
    return json({
      permitted: true,
      permit: JSON.stringify(permitEnvelope),
      authority_sha: authoritySha || commitSha,
      decision_id: decisionId,
      mode: env.MODE,
      hold: "AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD",
      motor_action: action,
      motor_route: route,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "unknown error";
    console.error(JSON.stringify({ message: "handleExactPermit failed", error: message }));
    return json({ permitted: false, reason: message.startsWith("BLOCKED_") ? message : "BLOCKED_PERMIT_EXCEPTION", detail: message }, 503);
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const path = new URL(request.url).pathname;
    try {
      if (path === "/health") {
        return json({
          ok: true,
          mode: env.MODE || "LIVE_EVAL",
          sg_runtime: "LIVE_WIRED_T0",
          enforcement_enabled: false,
          webhook_enabled: env.WEBHOOK_ENABLED === "true",
          app_id: env.EXPECTED_APP_ID,
          installation_id: env.EXPECTED_INSTALLATION_ID,
          signing_key_id: env.SG_SIGNING_KEY_ID,
        });
      }
      if (path === "/webhook/github") return handleWebhook(request, env);
      if (path === "/v1/permit/exact" && request.method === "POST") return handleExactPermit(request, env);
      if (path === "/shadow/evaluate" && request.method === "POST") return handleManualEvaluation(request, env);
      if (path === "/shadow/verify-permit" && request.method === "POST") return handlePermitVerification(request, env);
      if (path === "/shadow/identity" && request.method === "GET") {
        if (!(await internalAuthorized(request, env))) return json({ code: "BLOCKED_UNAUTHENTICATED_IDENTITY_PROOF" }, 401);
        return json({ status: "SG_CANDIDATE_IDENTITY_PROVEN", ...(await attestIdentity(env)) });
      }
      return json({ code: "NOT_FOUND" }, 404);
    } catch (error) {
      const message = error instanceof Error ? error.message : "unknown error";
      console.error(JSON.stringify({ message: "SG v2 shadow request failed", path, error: message }));
      const status = message.startsWith("BLOCKED_") ? 503 : 400;
      return json({ code: message.startsWith("BLOCKED_") ? message : "BLOCKED_INVALID_REQUEST", detail: message }, status);
    }
  },
} satisfies ExportedHandler<Env>;
