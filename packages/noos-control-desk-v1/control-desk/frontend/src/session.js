/** Session display cache — server responses only, no client policy logic. */

const receiptCache = {};
let lastPolicyCheck = null;
const ATTEST_KEY = 'noos_attestation_cache_v1';

export function cacheReceipt(path, payload) {
  if (!path) return;
  const name = path.split('/').pop();
  receiptCache[name] = {
    path: path.startsWith('receipts/') ? path : `receipts/${name}`,
    ...payload,
  };
}

export function getReceiptCache() {
  return receiptCache;
}

export function getReceipt(name) {
  return receiptCache[name] || null;
}

export function setLastPolicyCheck(result) {
  lastPolicyCheck = result;
  try {
    sessionStorage.setItem('noos_policy_check_v1', JSON.stringify(result));
  } catch {
    /* ignore */
  }
}

export function getLastPolicyCheck() {
  if (lastPolicyCheck) return lastPolicyCheck;
  try {
    const raw = sessionStorage.getItem('noos_policy_check_v1');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/** Cache server attestation save response (verdict from backend only). */
export function cacheAttestation(workflowId, serverResponse) {
  const all = getAttestationCache();
  all[workflowId] = {
    policy_verdict: serverResponse.policy_verdict,
    verdict_reasons: serverResponse.verdict_reasons || [],
    last_audited: serverResponse.last_audited,
    updated_at: new Date().toISOString(),
  };
  try {
    sessionStorage.setItem(ATTEST_KEY, JSON.stringify(all));
  } catch {
    /* ignore */
  }
}

export function getAttestationCache() {
  try {
    return JSON.parse(sessionStorage.getItem(ATTEST_KEY) || '{}');
  } catch {
    return {};
  }
}
