import { canonicalJson } from "./canonical";
import { signEnvelope, verifyEnvelope } from "./crypto";
import type {
  EvaluationRequest,
  EvaluationResult,
  ExactSubject,
  SGDecisionReceipt,
  ShadowPermit,
  SignedEnvelope,
} from "./types";

export function buildReceipt(
  request: EvaluationRequest,
  evaluation: EvaluationResult,
  now = new Date(),
): SGDecisionReceipt {
  const issuedAt = now.toISOString();
  const expiresAt = new Date(now.getTime() + 5 * 60_000).toISOString();
  return {
    ...evaluation.subject,
    receipt_type: "SG_DECISION",
    mode: "SHADOW",
    status: evaluation.verdict,
    result: evaluation.verdict,
    verdict: evaluation.verdict,
    pass_claimed: evaluation.verdict === "PASS",
    enforcement_enabled: false,
    event: request.event,
    delivery_id: request.delivery_id,
    check_name: "Noetfield SG / P0 Authority",
    issued_at: issuedAt,
    expires_at: expiresAt,
    reasons: evaluation.reasons,
  };
}

export function buildShadowPermit(receipt: SGDecisionReceipt): ShadowPermit | null {
  if (receipt.verdict !== "PASS") return null;
  const { event: _event, delivery_id: _delivery, check_name: _check, issued_at, expires_at,
    receipt_type: _receiptType, mode: _mode, status: _status, result: _result, verdict: _verdict,
    pass_claimed: _passClaimed, enforcement_enabled: _enforcement, reasons: _reasons, ...subject } = receipt;
  return {
    permit_type: "SG_EXACT_SUBJECT_PERMIT",
    mode: "SHADOW",
    enforceable: false,
    authorization: "NONE",
    verdict: "PASS",
    subject,
    issued_at,
    expires_at,
  };
}

export async function signDecision(
  receipt: SGDecisionReceipt,
  permit: ShadowPermit | null,
  privateJwk: string,
  keyId: string,
): Promise<{
  receipt: SignedEnvelope<SGDecisionReceipt>;
  permit: SignedEnvelope<ShadowPermit> | null;
}> {
  return {
    receipt: await signEnvelope(receipt, privateJwk, keyId),
    permit: permit ? await signEnvelope(permit, privateJwk, keyId) : null,
  };
}

export type PermitVerification =
  | { ok: false; code: "BLOCKED_INVALID_SG_PERMIT" | "BLOCKED_EXPIRED_SG_PERMIT" | "BLOCKED_SUBJECT_MISMATCH" }
  | { ok: true; code: "VALID_SHADOW_PERMIT"; nonce: string; expiresAt: number };

export async function verifyShadowPermit(
  envelope: SignedEnvelope<ShadowPermit>,
  publicJwk: string,
  expectedSubject: ExactSubject,
  now = Date.now(),
): Promise<PermitVerification> {
  if (!(await verifyEnvelope(envelope, publicJwk))) return { ok: false, code: "BLOCKED_INVALID_SG_PERMIT" };
  const permit = envelope.payload;
  if (
    permit.permit_type !== "SG_EXACT_SUBJECT_PERMIT"
    || permit.mode !== "SHADOW"
    || permit.enforceable !== false
    || permit.authorization !== "NONE"
    || permit.verdict !== "PASS"
    || envelope.signature.key_id !== permit.subject.signing_key_id
  ) return { ok: false, code: "BLOCKED_INVALID_SG_PERMIT" };
  if (canonicalJson(permit.subject) !== canonicalJson(expectedSubject)) {
    return { ok: false, code: "BLOCKED_SUBJECT_MISMATCH" };
  }
  const expiresAt = Date.parse(permit.expires_at);
  const issuedAt = Date.parse(permit.issued_at);
  if (!Number.isFinite(expiresAt) || !Number.isFinite(issuedAt) || issuedAt > now || expiresAt <= now || expiresAt - issuedAt > 15 * 60_000) {
    return { ok: false, code: "BLOCKED_EXPIRED_SG_PERMIT" };
  }
  return { ok: true, code: "VALID_SHADOW_PERMIT", nonce: permit.subject.nonce, expiresAt };
}
