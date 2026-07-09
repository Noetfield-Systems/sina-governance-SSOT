import { useCallback, useEffect, useState } from 'react';
import { api } from '../api';
import Flash from '../components/Flash';
import { getLastPolicyCheck } from '../session';

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [integrator, setIntegrator] = useState(null);
  const [error, setError] = useState('');
  const policyCheck = getLastPolicyCheck();

  const load = useCallback(async () => {
    setError('');
    const [dash, integ] = await Promise.all([
      api.dashboard(),
      api.integratorStatus(),
    ]);
    if (!dash.ok) {
      setError('Failed to load dashboard');
      return;
    }
    setData(dash.data);
    if (integ.ok) setIntegrator(integ.data);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (error) return <Flash kind="err">{error}</Flash>;
  if (!data) return <p className="muted">Loading dashboard…</p>;

  const policyStatus = policyCheck?.report?.status || 'NOT_RUN_THIS_SESSION';
  const policyKind =
    policyStatus === 'PASS' ? 'ok' : policyStatus === 'NOT_RUN_THIS_SESSION' ? 'warn' : 'err';

  return (
    <>
      <div className="grid">
        <Stat num={data.registry_entries} label="Total workflows" />
        <Stat num={data.pass_count} label="PASS" color="var(--green)" />
        <Stat num={data.fail_count} label="FAIL" color="var(--red)" />
        <Stat num={data.blocked_count} label="BLOCKED" color="var(--orange)" />
        <Stat num={data.todo_count} label="TODO" color="var(--yellow)" />
      </div>

      <div className="card">
        <strong>Last policy check</strong>
        <Flash kind={policyKind}>
          {policyStatus}
          {policyCheck?.receipt ? ` · receipt: ${policyCheck.receipt}` : ''}
          {policyCheck?.report?.violations_active?.length
            ? ` · ${policyCheck.report.violations_active.length} active violation(s)`
            : ''}
        </Flash>
      </div>

      {integrator && (
        <div className="card">
          <strong>Integrator status</strong>
          <p className="muted">
            repo_local: {integrator.repo_local || 'unknown'} · home_mirror:{' '}
            {integrator.home_mirror || 'unconfigured'} · cloud:{' '}
            {integrator.cloud_mirror?.status || 'unconfigured'}
          </p>
          <p className="muted">
            cloud_write_scope: <strong>{integrator.cloud_write_scope || 'gated'}</strong>
            {' · '}
            unrestricted: <strong>{String(integrator.cloud_write_unrestricted_allowed ?? false)}</strong>
          </p>
          {integrator.error && (
            <Flash kind="err">BLOCKED_WITH_REASON: {integrator.error}</Flash>
          )}
        </div>
      )}

      <div className="card">
        <Flash kind={data.ready_for_lock_candidate ? 'ok' : 'warn'}>
          Lock readiness:{' '}
          {data.ready_for_lock_candidate ? 'backend ready' : 'not ready — incomplete or failing audits'}
        </Flash>
      </div>

      <div className="card">
        <strong>Git status</strong>
        <pre>{JSON.stringify(data.git, null, 2)}</pre>
      </div>
    </>
  );
}

function Stat({ num, label, color }) {
  return (
    <div className="stat">
      <div className="num" style={color ? { color } : undefined}>
        {num}
      </div>
      <div className="label">{label}</div>
    </div>
  );
}
