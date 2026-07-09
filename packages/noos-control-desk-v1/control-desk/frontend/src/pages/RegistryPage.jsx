import { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import Badge from '../components/Badge';
import Flash from '../components/Flash';
import { cacheReceipt, getAttestationCache } from '../session';

const EMPTY_FILTER = { repo: '', wfClass: '', owner: '', verdict: '' };

export default function RegistryPage() {
  const [workflows, setWorkflows] = useState([]);
  const [attestations, setAttestations] = useState({});
  const [filters, setFilters] = useState(EMPTY_FILTER);
  const [flash, setFlash] = useState(null);

  const load = useCallback(async () => {
    const reg = await api.registryLoad();
    if (reg.ok) setWorkflows(reg.data.workflows || []);
    setAttestations(getAttestationCache());
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const repos = useMemo(
    () => [...new Set(workflows.map((w) => w.repo))].sort(),
    [workflows],
  );
  const classes = useMemo(
    () => [...new Set(workflows.map((w) => w.class))].sort(),
    [workflows],
  );
  const owners = useMemo(
    () => [...new Set(workflows.map((w) => w.owner))].sort(),
    [workflows],
  );

  const filtered = useMemo(() => {
    return workflows.filter((wf) => {
      const att = attestations[wf.workflow_id];
      const verdict = att?.policy_verdict || 'TODO';
      if (filters.repo && wf.repo !== filters.repo) return false;
      if (filters.wfClass && wf.class !== filters.wfClass) return false;
      if (filters.owner && wf.owner !== filters.owner) return false;
      if (filters.verdict && verdict !== filters.verdict) return false;
      return true;
    });
  }, [workflows, attestations, filters]);

  async function saveDraft() {
    setFlash({ kind: 'ok', text: 'Saving draft…' });
    const { ok, data } = await api.registrySaveDraft(workflows);
    if (!ok) {
      setFlash({ kind: 'err', text: data.error || 'Save failed' });
      return;
    }
    setFlash({
      kind: 'ok',
      text: `Draft saved → ${data.path} (${data.entries} entries). Incomplete audits OK.`,
    });
    if (data.receipt) cacheReceipt(data.receipt, data);
  }

  return (
    <div className="card">
      <div className="toolbar">
        <div>
          <strong>Workflow Registry</strong>
          <p className="muted">
            Live registry · Save Draft writes{' '}
            <code>.noos/workflow_registry_draft.json</code> only.
          </p>
        </div>
        <div className="btn-row">
          <button type="button" className="action secondary" onClick={load}>
            Refresh
          </button>
          <button type="button" className="action" onClick={saveDraft}>
            Save Draft
          </button>
        </div>
      </div>
      {flash && <Flash kind={flash.kind}>{flash.text}</Flash>}

      <div className="filter-row">
        <FilterSelect
          label="repo"
          value={filters.repo}
          options={repos}
          onChange={(v) => setFilters((f) => ({ ...f, repo: v }))}
        />
        <FilterSelect
          label="class"
          value={filters.wfClass}
          options={classes}
          onChange={(v) => setFilters((f) => ({ ...f, wfClass: v }))}
        />
        <FilterSelect
          label="owner"
          value={filters.owner}
          options={owners}
          onChange={(v) => setFilters((f) => ({ ...f, owner: v }))}
        />
        <FilterSelect
          label="verdict"
          value={filters.verdict}
          options={['PASS', 'FAIL', 'BLOCKED', 'TODO']}
          onChange={(v) => setFilters((f) => ({ ...f, verdict: v }))}
        />
        <button type="button" className="small" onClick={() => setFilters(EMPTY_FILTER)}>
          Clear
        </button>
      </div>

      <p className="muted">
        Showing {filtered.length} of {workflows.length} workflows
      </p>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>workflow_id</th>
              <th>repo</th>
              <th>class</th>
              <th>owner</th>
              <th>trigger</th>
              <th>model_policy</th>
              <th>last_audited</th>
              <th>verdict</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((wf) => {
              const att = attestations[wf.workflow_id];
              return (
                <tr key={wf.workflow_id}>
                  <td>{wf.workflow_id}</td>
                  <td>{wf.repo}</td>
                  <td>{wf.class}</td>
                  <td>{wf.owner}</td>
                  <td>{wf.trigger}</td>
                  <td>{wf.model_policy}</td>
                  <td>{wf.last_audited}</td>
                  <td>
                    <Badge verdict={att?.policy_verdict} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function FilterSelect({ label, value, options, onChange }) {
  return (
    <label className="filter-field">
      <span>{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">all</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}
