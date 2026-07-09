import { useCallback, useEffect, useState } from 'react';
import { api } from '../api';
import Flash from '../components/Flash';
import { cacheReceipt } from '../session';

export default function IntegratorPage() {
  const [status, setStatus] = useState(null);
  const [flash, setFlash] = useState(null);
  const [syncing, setSyncing] = useState(false);

  const loadStatus = useCallback(async () => {
    const { ok, data } = await api.integratorStatus();
    if (ok) {
      setStatus(data);
      return;
    }
    setFlash({
      kind: 'err',
      text: `BLOCKED_WITH_REASON: ${data.error || 'integrator status unavailable'}`,
    });
  }, []);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  async function runSync() {
    setSyncing(true);
    setFlash({ kind: 'ok', text: 'Running repo-local sync…' });
    const { ok, data } = await api.integratorSync();
    setSyncing(false);
    if (!ok || data.status === 'ERROR') {
      setFlash({
        kind: 'err',
        text: `BLOCKED_WITH_REASON: ${data.message || 'Sync failed'}`,
      });
      return;
    }
    setStatus(data.summary || data);
    if (data.receipt) cacheReceipt(data.receipt, data);
    setFlash({ kind: 'ok', text: 'Repo-local sync complete. Cloud writes scope-gated.' });
  }

  const cloud = status?.cloud_mirror || {};
  const homeUnconfigured =
    !status?.home_mirror || status.home_mirror === 'unconfigured' || status.home_mirror === 'stale';
  const cloudUnconfigured = !cloud.status || cloud.status === 'unconfigured';

  return (
    <div className="card">
      <div className="toolbar">
        <div>
          <strong>NOOS Integrator Sync</strong>
          <p className="muted">POST /api/integrator/sync — repo-local sync. Cloud writes scope-gated per NOOS Copilot.</p>
        </div>
        <div className="btn-row">
          <button type="button" className="action secondary" onClick={loadStatus}>
            Refresh status
          </button>
          <button type="button" className="action" onClick={runSync} disabled={syncing}>
            Run local sync
          </button>
        </div>
      </div>
      {flash && <Flash kind={flash.kind}>{flash.text}</Flash>}

      {status && (
        <>
          <div className="grid-3">
            <MirrorCard
              title="Repo-local"
              value={status.repo_local || 'unknown'}
              detail={`age: ${status.repo_local_age_hours ?? 'n/a'}h`}
            />
            <MirrorCard
              title="Home mirror"
              value={status.home_mirror || 'unconfigured'}
              detail={status.home_mirror_path || 'path unconfigured'}
              blocked={homeUnconfigured}
            />
            <MirrorCard
              title="Cloud mirror (read-only)"
              value={cloud.status || 'unconfigured'}
              detail={cloud.path || 'path unconfigured'}
              blocked={cloudUnconfigured}
            />
          </div>
          {(homeUnconfigured || cloudUnconfigured) && (
            <Flash kind="warn">
              BLOCKED_WITH_REASON:{' '}
              {[
                homeUnconfigured && 'home mirror unconfigured or stale',
                cloudUnconfigured && 'cloud mirror unconfigured (read-only)',
              ]
                .filter(Boolean)
                .join(' · ')}
            </Flash>
          )}
          <div className="gate-banner">
            cloud_write_scope: <strong>{status.cloud_write_scope || 'gated'}</strong>
            {' · '}
            unrestricted: <strong>{String(status.cloud_write_unrestricted_allowed ?? false)}</strong>
            <br />
            {status.gate_note ||
              status.cloud_write_scope_gate?.rule ||
              'Cloud writes are scope-gated. Before full PASS, NOOS Copilot may publish receipts, status, drift reports, and prepare draft branches/PRs. Fleet rollout, ACTIVE promotion, direct main write, and policy/law mutation remain blocked.'}
          </div>
          <pre>{JSON.stringify(status, null, 2)}</pre>
        </>
      )}
    </div>
  );
}

function MirrorCard({ title, value, detail, blocked }) {
  return (
    <div className={`mirror-card${blocked ? ' blocked' : ''}`}>
      <div className="title">{title}</div>
      <div className="value">{value}</div>
      <div className="muted">{detail}</div>
    </div>
  );
}
