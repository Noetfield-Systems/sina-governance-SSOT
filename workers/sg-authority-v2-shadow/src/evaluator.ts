import type { EvaluationRequest, EvaluationResult, EvaluatorConfig, Verdict } from "./types";

const SHA256 = /^[a-f0-9]{64}$/;
const COMMIT_SHA = /^[a-f0-9]{40}$/;
const NONCE = /^[A-Za-z0-9._:-]{16,200}$/;
const ALLOWED_SHADOW_ACTIONS = new Set(["evaluate_pull_request", "evaluate_merge_group"]);
const MUTATION_ACTIONS = new Set(["merge", "deploy", "promote", "rollback", "mutate_secret", "mutate_authority"]);
const DENIED_APP_IDS = new Set(["4179901", "4275961"]);

function invalidExactSubject(request: EvaluationRequest): string[] {
  const reasons: string[] = [];
  if (!COMMIT_SHA.test(request.commit_sha)) reasons.push("commit_sha must be exact lowercase 40-hex");
  for (const field of ["artifact_hash", "policy_hash", "schema_hash", "evaluator_hash"] as const) {
    if (!SHA256.test(request[field])) reasons.push(`${field} must be exact lowercase SHA-256`);
  }
  if (!NONCE.test(request.nonce)) reasons.push("nonce format is invalid");
  if (!request.delivery_id) reasons.push("delivery_id is required");
  if (!request.target) reasons.push("target is required");
  return reasons;
}

export function evaluateDeterministically(
  request: EvaluationRequest,
  config: EvaluatorConfig,
): EvaluationResult {
  const reasons: string[] = [];
  let verdict: Verdict = "PASS";

  if (DENIED_APP_IDS.has(request.app_id)) {
    reasons.push(`App ID ${request.app_id} is forbidden as SG authority`);
    verdict = "BLOCKED";
  }
  if (config.expectedAppId === "UNSET" || config.expectedInstallationId === "UNSET") {
    reasons.push("candidate SG identity is not configured or proven");
    verdict = "BLOCKED";
  }
  if (request.app_id !== config.expectedAppId) {
    reasons.push("App ID does not match the configured candidate SG identity");
    verdict = "BLOCKED";
  }
  if (request.installation_id !== config.expectedInstallationId) {
    reasons.push("installation ID does not match the configured candidate installation");
    verdict = "BLOCKED";
  }
  if (!config.allowedRepositories.has(request.repository)) {
    reasons.push("repository is not an explicitly installed candidate repository");
    verdict = "BLOCKED";
  }
  if (request.action === "commission_sg" || request.target === "noetfield-sg-authority") {
    reasons.push("candidate SG may not approve or commission itself");
    verdict = "BLOCKED";
  }
  if (MUTATION_ACTIONS.has(request.action)) {
    reasons.push("production mutation is forbidden while SG runtime is not commissioned");
    verdict = "BLOCKED";
  }
  if (!ALLOWED_SHADOW_ACTIONS.has(request.action)) {
    reasons.push("action is outside the non-mutating SG v2 shadow allowlist");
    verdict = verdict === "BLOCKED" ? verdict : "ESCALATE_REQUIRED";
  }

  const exactFailures = invalidExactSubject(request);
  if (exactFailures.length > 0) {
    reasons.push(...exactFailures);
    if (verdict === "PASS") verdict = "FAIL";
  }

  const expectedPins: Array<[string, string, string]> = [
    ["policy_hash", request.policy_hash, config.expectedPolicyHash],
    ["schema_hash", request.schema_hash, config.expectedSchemaHash],
    ["evaluator_hash", request.evaluator_hash, config.expectedEvaluatorHash],
    ["worker_version", request.worker_version, config.expectedWorkerVersion],
    ["signing_key_id", request.signing_key_id, config.expectedSigningKeyId],
  ];
  for (const [field, actual, expected] of expectedPins) {
    if (actual !== expected) {
      reasons.push(`${field} does not match the configured exact pin`);
      if (verdict === "PASS") verdict = "FAIL";
    }
  }

  if (verdict === "PASS" && reasons.length > 0) verdict = "FAIL";
  return { verdict, reasons, subject: request };
}
