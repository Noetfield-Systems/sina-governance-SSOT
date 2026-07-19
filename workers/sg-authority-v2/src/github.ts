import { base64UrlEncode, canonicalJson, toBytes } from "./canonical";

const GITHUB_API = "https://api.github.com";
const MAX_GITHUB_RESPONSE_BYTES = 1_000_000;
const EXPECTED_PERMISSIONS: Record<string, string> = {
  actions: "read",
  checks: "write",
  contents: "read",
  metadata: "read",
  pull_requests: "read",
  statuses: "write",
};

type FetchLike = typeof fetch;

function base64ToBytes(input: string): Uint8Array<ArrayBuffer> {
  const normalized = input.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "="));
  const output = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) output[index] = binary.charCodeAt(index);
  return output as Uint8Array<ArrayBuffer>;
}

function encodeDerLength(length: number): Uint8Array {
  if (length < 0x80) return new Uint8Array([length]);
  const bytes: number[] = [];
  for (let value = length; value > 0; value >>= 8) bytes.unshift(value & 0xff);
  return new Uint8Array([0x80 | bytes.length, ...bytes]);
}

function concatBytes(...chunks: Uint8Array[]): Uint8Array {
  const output = new Uint8Array(chunks.reduce((size, chunk) => size + chunk.length, 0));
  let offset = 0;
  for (const chunk of chunks) {
    output.set(chunk, offset);
    offset += chunk.length;
  }
  return output;
}

function der(tag: number, value: Uint8Array): Uint8Array {
  const length = encodeDerLength(value.length);
  return concatBytes(new Uint8Array([tag]), length, value);
}

function pemToPkcs8(pem: string): Uint8Array<ArrayBuffer> {
  if (!pem.includes("PRIVATE KEY")) throw new TypeError("GitHub App private key PEM is missing");
  const isPkcs1 = pem.includes("BEGIN RSA PRIVATE KEY");
  const body = pem.replace(/-----BEGIN [^-]+-----/g, "").replace(/-----END [^-]+-----/g, "").replace(/\s+/g, "");
  const bytes = base64ToBytes(body);
  if (!isPkcs1) return bytes;
  const version = der(0x02, new Uint8Array([0]));
  const oid = new Uint8Array([0x06, 0x09, 0x2a, 0x86, 0x48, 0x86, 0xf7, 0x0d, 0x01, 0x01, 0x01]);
  const algorithm = der(0x30, concatBytes(oid, new Uint8Array([0x05, 0x00])));
  return der(0x30, concatBytes(version, algorithm, der(0x04, bytes))) as Uint8Array<ArrayBuffer>;
}

export async function createAppJwt(appId: string, privateKeyPem: string, nowSeconds = Math.floor(Date.now() / 1000)): Promise<string> {
  if (!/^[0-9]+$/.test(appId)) throw new TypeError("configured GitHub App ID is not numeric");
  const header = base64UrlEncode(toBytes(JSON.stringify({ alg: "RS256", typ: "JWT" })));
  const payload = base64UrlEncode(toBytes(JSON.stringify({ iat: nowSeconds - 60, exp: nowSeconds + 540, iss: appId })));
  const signingInput = `${header}.${payload}`;
  const key = await crypto.subtle.importKey(
    "pkcs8",
    pemToPkcs8(privateKeyPem),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, toBytes(signingInput));
  return `${signingInput}.${base64UrlEncode(signature)}`;
}

async function readJsonBounded(response: Response): Promise<Record<string, unknown>> {
  const contentLength = Number(response.headers.get("content-length") ?? 0);
  if (contentLength > MAX_GITHUB_RESPONSE_BYTES) throw new RangeError("GitHub API response exceeds size limit");
  if (!response.body) return {};
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.length;
    if (total > MAX_GITHUB_RESPONSE_BYTES) {
      await reader.cancel();
      throw new RangeError("GitHub API response exceeds size limit");
    }
    chunks.push(value);
  }
  const bytes = concatBytes(...chunks);
  const text = new TextDecoder().decode(bytes);
  if (!response.ok) throw new Error(`GitHub API request failed: HTTP ${response.status}: ${text.slice(0, 500)}`);
  return text ? (JSON.parse(text) as Record<string, unknown>) : {};
}

export async function githubJson(
  path: string,
  token: string,
  init: RequestInit = {},
  fetchImpl: FetchLike = fetch,
): Promise<Record<string, unknown>> {
  if (!token) throw new TypeError("authenticated GitHub token is required; public fallback is forbidden");
  const response = await fetchImpl(`${GITHUB_API}${path}`, {
    ...init,
    headers: {
      ...init.headers,
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "User-Agent": "noetfield-sg-authority-v2-shadow",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json",
    },
  });
  return readJsonBounded(response);
}

async function installationToken(env: Env, appJwt: string, fetchImpl: FetchLike): Promise<string> {
  const response = await githubJson(
    `/app/installations/${env.EXPECTED_INSTALLATION_ID}/access_tokens`,
    appJwt,
    { method: "POST", body: "{}" },
    fetchImpl,
  );
  if (typeof response.token !== "string" || !response.token) throw new Error("installation token response omitted token");
  return response.token;
}

export interface IdentityAttestation {
  app_id: string;
  app_slug: string;
  owner: string;
  installation_id: string;
  repositories: string[];
  exact_identity: true;
  public_fallback_used: false;
}

export async function attestIdentity(env: Env, fetchImpl: FetchLike = fetch): Promise<IdentityAttestation> {
  const jwt = await createAppJwt(env.EXPECTED_APP_ID, env.GITHUB_APP_PRIVATE_KEY);
  const app = await githubJson("/app", jwt, {}, fetchImpl);
  const owner = app.owner && typeof app.owner === "object" && !Array.isArray(app.owner)
    ? (app.owner as Record<string, unknown>).login
    : undefined;
  if (String(app.id) !== env.EXPECTED_APP_ID || app.slug !== env.EXPECTED_APP_SLUG || owner !== env.EXPECTED_ORG) {
    throw new Error("GET /app identity did not match exact candidate SG metadata");
  }
  if (canonicalJson(app.permissions) !== canonicalJson(EXPECTED_PERMISSIONS)) {
    throw new Error("GET /app permissions did not match the exact least-privilege SG permission set");
  }

  const installation = await githubJson(`/orgs/${env.EXPECTED_ORG}/installation`, jwt, {}, fetchImpl);
  if (String(installation.id) !== env.EXPECTED_INSTALLATION_ID) {
    throw new Error("organization installation ID did not match exact candidate installation");
  }
  const token = await installationToken(env, jwt, fetchImpl);
  const membership = await githubJson("/installation/repositories?per_page=100", token, {}, fetchImpl);
  if (!Array.isArray(membership.repositories)) throw new Error("installation repositories response is invalid");
  const repositories = membership.repositories.map((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item) || typeof (item as Record<string, unknown>).full_name !== "string") {
      throw new Error("installation repository entry is invalid");
    }
    return (item as Record<string, unknown>).full_name as string;
  });
  const allowed = JSON.parse(env.ALLOWED_REPOSITORIES) as unknown;
  if (
    !Array.isArray(allowed)
    || allowed.length !== 2
    || !allowed.every((repo) => typeof repo === "string")
    || !allowed.includes("Noetfield-Systems/sina-governance-SSOT")
    || new Set(allowed).size !== 2
    || JSON.stringify([...allowed].sort()) !== JSON.stringify([...repositories].sort())
  ) {
    throw new Error("installation membership must be exactly SG plus one approved non-production canary");
  }
  return {
    app_id: env.EXPECTED_APP_ID,
    app_slug: env.EXPECTED_APP_SLUG,
    owner: env.EXPECTED_ORG,
    installation_id: env.EXPECTED_INSTALLATION_ID,
    repositories: repositories.sort(),
    exact_identity: true,
    public_fallback_used: false,
  };
}

export async function publishShadowCheck(
  env: Env,
  repository: string,
  headSha: string,
  conclusion: "success" | "failure" | "neutral" | "action_required",
  summary: string,
  fetchImpl: FetchLike = fetch,
): Promise<{ published: boolean; reason?: string; check_run_id?: string }> {
  if (env.CHECK_RUN_PUBLISH_ENABLED !== "true") return { published: false, reason: "shadow check publishing disabled" };
  const allowed = JSON.parse(env.ALLOWED_REPOSITORIES) as unknown;
  if (!Array.isArray(allowed) || !allowed.includes(repository)) {
    throw new Error("Check Run repository is not in the exact installed repository allowlist");
  }
  if (!/^[a-f0-9]{40}$/.test(headSha)) throw new Error("Check Run head SHA is not exact lowercase 40-hex");
  const jwt = await createAppJwt(env.EXPECTED_APP_ID, env.GITHUB_APP_PRIVATE_KEY);
  const token = await installationToken(env, jwt, fetchImpl);
  const check = await githubJson(`/repos/${repository}/check-runs`, token, {
    method: "POST",
    body: JSON.stringify({
      name: env.EXPECTED_CHECK_NAME,
      head_sha: headSha,
      status: "completed",
      conclusion,
      output: { title: "SG v2 shadow evaluation", summary },
    }),
  }, fetchImpl);
  if (
    !check.app
    || typeof check.app !== "object"
    || Array.isArray(check.app)
    || String((check.app as Record<string, unknown>).id) !== env.EXPECTED_APP_ID
  ) {
    throw new Error("created Check Run source App did not match the exact candidate SG App");
  }
  return { published: true, check_run_id: String(check.id) };
}
