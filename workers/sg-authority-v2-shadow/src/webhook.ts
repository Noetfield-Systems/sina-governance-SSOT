import { sha256Hex } from "./canonical";
import type { EvaluationRequest } from "./types";

function record(value: unknown, field: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new TypeError(`${field} must be an object`);
  return value as Record<string, unknown>;
}

function requiredString(value: unknown, field: string): string {
  if (typeof value !== "string" || !value) throw new TypeError(`${field} must be a non-empty string`);
  return value;
}

export function allowedRepositories(raw: string): ReadonlySet<string> {
  const parsed = JSON.parse(raw) as unknown;
  if (!Array.isArray(parsed) || parsed.length === 0 || !parsed.every((item) => typeof item === "string")) {
    throw new TypeError("ALLOWED_REPOSITORIES must be a non-empty JSON string array");
  }
  return new Set(parsed);
}

export async function subjectFromWebhook(
  event: string,
  deliveryId: string,
  payload: unknown,
  body: ArrayBuffer,
  env: Env,
): Promise<EvaluationRequest> {
  if (event !== "pull_request" && event !== "merge_group") {
    throw new TypeError(`unsupported GitHub event: ${event}`);
  }
  const root = record(payload, "payload");
  const repository = requiredString(record(root.repository, "repository").full_name, "repository.full_name");
  const installationId = String(record(root.installation, "installation").id ?? "");
  if (!/^[0-9]+$/.test(installationId)) throw new TypeError("installation.id must be numeric");

  let commitSha: string;
  if (event === "merge_group") {
    commitSha = requiredString(record(root.merge_group, "merge_group").head_sha, "merge_group.head_sha");
  } else {
    const pullRequest = record(root.pull_request, "pull_request");
    commitSha = requiredString(record(pullRequest.head, "pull_request.head").sha, "pull_request.head.sha");
  }

  return {
    app_id: env.EXPECTED_APP_ID,
    installation_id: installationId,
    repository,
    commit_sha: commitSha,
    action: `evaluate_${event}`,
    target: env.EXPECTED_CHECK_NAME,
    artifact_hash: await sha256Hex(body),
    policy_hash: env.POLICY_HASH,
    schema_hash: env.SCHEMA_HASH,
    evaluator_hash: env.EVALUATOR_HASH,
    worker_version: env.WORKER_VERSION,
    signing_key_id: env.SG_SIGNING_KEY_ID,
    nonce: deliveryId,
    event,
    delivery_id: deliveryId,
  };
}
