/**
 * Canonical backend routes only (HANDOFF_BACKEND_BUILDER_v1 contract).
 * No client-side policy logic.
 */
async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

export const api = {
  dashboard: () => request('/api/dashboard'),
  registryLoad: () => request('/api/registry/load'),
  registrySaveDraft: (workflows) =>
    request('/api/registry/save-draft', {
      method: 'POST',
      body: JSON.stringify({ workflows }),
    }),
  attestationSave: (body) =>
    request('/api/attestation/save', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  policyCheck: () =>
    request('/api/policy/check', { method: 'POST', body: '{}' }),
  integratorStatus: () => request('/api/integrator/status'),
  integratorSync: () =>
    request('/api/integrator/sync', { method: 'POST', body: '{}' }),
  receiptsList: () => request('/api/receipts/list'),
  prPrepare: () => request('/api/pr/prepare'),
  lockCandidateSubmit: () =>
    request('/api/lock-candidate/submit', { method: 'POST', body: '{}' }),
};
