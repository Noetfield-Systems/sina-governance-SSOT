import { useCallback, useEffect, useState } from 'react';
import { api } from '../api';
import Flash from '../components/Flash';
import { cacheReceipt } from '../session';

export default function PrPrepPage() {
  const [plan, setPlan] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [flash, setFlash] = useState(null);
  const [output, setOutput] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    const [planRes, dashRes] = await Promise.all([
      api.prPrepare(),
      api.dashboard(),
    ]);
    if (planRes.ok) setPlan(planRes.data);
    if (dashRes.ok) setDashboard(dashRes.data);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function submitLock() {
    if (!dashboard?.ready_for_lock_candidate) return;
    setSubmitting(true);
    setFlash({ kind: 'ok', text: 'Submitting to backend…' });
    const { ok, status: httpStatus, data } = await api.lockCandidateSubmit();
    setSubmitting(false);
    if (httpStatus === 409 || data.status === 'BLOCKED') {
      setFlash({ kind: 'err', text: 'Backend rejected — not ready' });
      setOutput(formatBlockers(data));
      if (data.receipt) cacheReceipt(data.receipt, data);
      load();
      return;
    }
    if (data.status === 'LOCK_CANDIDATE_READY') {
      setFlash({ kind: 'ok', text: 'Backend returned LOCK_CANDIDATE_READY' });
    } else {
      setFlash({ kind: 'err', text: data.status || 'Unexpected response' });
    }
    setOutput(JSON.stringify(data, null, 2));
    if (data.receipt) cacheReceipt(data.receipt, data);
    load();
  }

  const ready = dashboard?.ready_for_lock_candidate === true;

  return (
    <div className="card">
      <div className="toolbar">
        <div>
          <strong>PR Prep / Git Status</strong>
          <p className="muted">
            GET /api/pr/prepare + /api/dashboard — plan only until backend confirms ready.
          </p>
        </div>
        <button type="button" className="action secondary" onClick={load}>
          Refresh
        </button>
      </div>

      {plan && (
        <>
          <Flash kind="warn">
            {plan.note || 'Plan only — no push, no main merge, no fake success.'}
          </Flash>
          <p>
            <strong>Plan status:</strong> {plan.status || 'PLAN_ONLY'}
          </p>
          <p>
            <strong>Suggested branch:</strong>{' '}
            <code>{plan.suggested_branch}</code>
          </p>
          <p>
            <strong>Suggested commit:</strong>{' '}
            <code>{plan.suggested_commit}</code>
          </p>
        </>
      )}

      <div className="section-label">Git status</div>
      <pre>{JSON.stringify(plan?.git || dashboard?.git || {}, null, 2)}</pre>

      <div className="section-label">Lock readiness (from /api/dashboard)</div>
      {dashboard && (
        <div className="blocker-list">
          <Flash kind={ready ? 'ok' : 'warn'}>
            {ready
              ? 'ready_for_lock_candidate: true'
              : 'ready_for_lock_candidate: false — PR not ready'}
          </Flash>
          <p>
            PASS: {dashboard.pass_count}/{dashboard.registry_entries} · FAIL:{' '}
            {dashboard.fail_count} · BLOCKED: {dashboard.blocked_count} · TODO:{' '}
            {dashboard.todo_count}
          </p>
          {!ready && (
            <p className="muted">
              Submit Lock Candidate disabled until backend confirms all workflows PASS.
              Blocking detail returned on 409 from /api/lock-candidate/submit.
            </p>
          )}
        </div>
      )}

      <button
        type="button"
        className="action"
        onClick={submitLock}
        disabled={!ready || submitting}
      >
        Submit Lock Candidate
      </button>

      {flash && <Flash kind={flash.kind}>{flash.text}</Flash>}
      {output && <pre>{output}</pre>}
    </div>
  );
}

function formatBlockers(data) {
  const lines = [data.message];
  if (data.errors?.length) {
    data.errors.forEach((e) =>
      lines.push(typeof e === 'string' ? e : JSON.stringify(e)),
    );
  }
  return lines.filter(Boolean).join('\n');
}
