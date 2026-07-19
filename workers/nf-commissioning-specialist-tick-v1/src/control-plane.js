const MAX_BODY_BYTES = 8_192;
const REQUEST_ID_PATTERN = /^[A-Za-z0-9._:-]{8,128}$/;

export class RequestError extends Error {
  constructor(status, code, message) {
    super(message);
    this.name = "RequestError";
    this.status = status;
    this.code = code;
  }
}

export async function readJobRequest(request, jobs) {
  const declaredLength = Number(request.headers.get("content-length") || "0");
  if (declaredLength > MAX_BODY_BYTES) {
    throw new RequestError(413, "request_too_large", "request body exceeds 8192 bytes");
  }
  const contentType = request.headers.get("content-type") || "";
  if (!contentType.toLowerCase().includes("application/json")) {
    throw new RequestError(415, "json_required", "Content-Type must be application/json");
  }

  const text = await request.text();
  if (new TextEncoder().encode(text).byteLength > MAX_BODY_BYTES) {
    throw new RequestError(413, "request_too_large", "request body exceeds 8192 bytes");
  }

  let body;
  try {
    body = JSON.parse(text);
  } catch {
    throw new RequestError(400, "invalid_json", "request body is not valid JSON");
  }
  if (body === null || Array.isArray(body) || typeof body !== "object") {
    throw new RequestError(400, "invalid_request", "request body must be a JSON object");
  }

  const jobId = typeof body.job_id === "string" ? body.job_id.trim() : "";
  const requestId = typeof body.request_id === "string" ? body.request_id.trim() : "";
  const rerunReason =
    typeof body.rerun_reason === "string" ? body.rerun_reason.trim() : "";

  if (!jobId) {
    throw new RequestError(400, "job_id_required", "job_id is required");
  }
  const job = jobs.find((candidate) => candidate.id === jobId);
  if (!job) {
    throw new RequestError(404, "unknown_job_id", `unknown commissioning job_id: ${jobId}`);
  }
  if (job.machine_safe !== true) {
    throw new RequestError(409, "job_not_machine_safe", `${jobId} is not machine-safe`);
  }
  if (!REQUEST_ID_PATTERN.test(requestId)) {
    throw new RequestError(
      400,
      "invalid_request_id",
      "request_id must be 8-128 letters, digits, dots, underscores, colons, or hyphens",
    );
  }
  if (rerunReason && (rerunReason.length < 12 || rerunReason.length > 500)) {
    throw new RequestError(
      400,
      "invalid_rerun_reason",
      "rerun_reason must be 12-500 characters when provided",
    );
  }

  return { job, jobId, requestId, rerunReason: rerunReason || null };
}

export async function authorized(request, configuredSecret) {
  const secret = String(configuredSecret || "").trim();
  if (!secret) return { ok: false, unavailable: true };

  const authorization = request.headers.get("authorization") || "";
  const match = authorization.match(/^Bearer[ ]+(.+)$/i);
  const presented = match ? match[1].trim() : "";
  if (!presented) return { ok: false, unavailable: false };

  const encoder = new TextEncoder();
  const [expectedDigest, presentedDigest] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(secret)),
    crypto.subtle.digest("SHA-256", encoder.encode(presented)),
  ]);
  if (typeof crypto.subtle.timingSafeEqual === "function") {
    return {
      ok: crypto.subtle.timingSafeEqual(expectedDigest, presentedDigest),
      unavailable: false,
    };
  }

  const expected = new Uint8Array(expectedDigest);
  const actual = new Uint8Array(presentedDigest);
  let mismatch = 0;
  for (let i = 0; i < expected.length; i += 1) mismatch |= expected[i] ^ actual[i];
  return { ok: mismatch === 0, unavailable: false };
}

export async function workflowInstanceId(requestId) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(requestId));
  const hex = [...new Uint8Array(digest)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
  return `commission-${hex.slice(0, 48)}`;
}
