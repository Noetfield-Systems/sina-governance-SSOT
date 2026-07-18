export type Verdict = "PASS" | "FAIL" | "BLOCKED" | "ESCALATE_REQUIRED";

export interface ExactSubject {
  app_id: string;
  installation_id: string;
  repository: string;
  commit_sha: string;
  action: string;
  target: string;
  artifact_hash: string;
  policy_hash: string;
  schema_hash: string;
  evaluator_hash: string;
  worker_version: string;
  signing_key_id: string;
  nonce: string;
}

export interface EvaluationRequest extends ExactSubject {
  event: string;
  delivery_id: string;
}

export interface EvaluationResult {
  verdict: Verdict;
  reasons: string[];
  subject: ExactSubject;
}

export interface EvaluatorConfig {
  expectedAppId: string;
  expectedInstallationId: string;
  allowedRepositories: ReadonlySet<string>;
  expectedPolicyHash: string;
  expectedSchemaHash: string;
  expectedEvaluatorHash: string;
  expectedWorkerVersion: string;
  expectedSigningKeyId: string;
}

export interface SignatureBlock {
  algorithm: "ECDSA_P256_SHA256";
  key_id: string;
  value: string;
}

export interface SignedEnvelope<T> {
  payload: T;
  signature: SignatureBlock;
}

export interface SGDecisionReceipt extends ExactSubject {
  receipt_type: "SG_DECISION";
  mode: "SHADOW";
  status: Verdict;
  result: Verdict;
  verdict: Verdict;
  pass_claimed: boolean;
  enforcement_enabled: false;
  event: string;
  delivery_id: string;
  check_name: "Noetfield SG / P0 Authority";
  issued_at: string;
  expires_at: string;
  reasons: string[];
}

export interface ShadowPermit {
  permit_type: "SG_EXACT_SUBJECT_PERMIT";
  mode: "SHADOW";
  enforceable: false;
  authorization: "NONE";
  verdict: "PASS";
  subject: ExactSubject;
  issued_at: string;
  expires_at: string;
}
