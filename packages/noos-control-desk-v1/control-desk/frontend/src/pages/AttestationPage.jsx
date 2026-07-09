import { useCallback, useEffect, useState } from 'react';
import { api } from '../api';
import Badge from '../components/Badge';
import Flash from '../components/Flash';
import { cacheAttestation, cacheReceipt, getAttestationCache } from '../session';

const EMPTY_FORM = {
  observed_model: '',
  observed_effort: '',
  observed_trigger: '',
  observed_mode: '',
  evidence_note: '',
  desired_model: 'gpt-5-mini',
  desired_effort: 'low',
  desired_trigger: 'manual',
  last_audited: '',
};

export default function AttestationPage() {
  const [rows, setRows] = useState([]);
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [result, setResult] = useState(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    const reg = await api.registryLoad();
    const workflows = reg.ok ? reg.data.workflows || [] : [];
    const attestations = getAttestationCache();
    setRows(
      workflows.map((wf) => ({
        ...wf,
        att: attestations[wf.workflow_id] || null,
      })),
    );
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  function openModal(wf) {
    setModal(wf);
    setResult(null);
    setForm({
      ...EMPTY_FORM,
      last_audited: new Date().toISOString().slice(0, 10),
    });
  }

  function closeModal() {
    setModal(null);
    setResult(null);
  }

  function updateField(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function saveAttestation() {
    if (!modal) return;
    setSaving(true);
    setResult(null);
    const body = { workflow_id: modal.workflow_id, ...form };
    const { ok, data } = await api.attestationSave(body);
    setSaving(false);
    if (!ok && data.error) {
      setResult({ error: data.error });
      return;
    }
    setResult({
      policy_verdict: data.policy_verdict,
      verdict_reasons: data.verdict_reasons || [],
    });
    cacheAttestation(modal.workflow_id, {
      ...data,
      last_audited: form.last_audited,
    });
    if (data.receipt) cacheReceipt(data.receipt, data);
    setTimeout(() => {
      closeModal();
      load();
    }, 1400);
  }

  return (
    <>
      <div className="card">
        <div className="toolbar">
          <div>
            <strong>Copilot UI Attestation</strong>
            <p className="muted">
              Record observed automation state as evidence. Bad values (gpt-5.4, Auto,
              High, hourly) are allowed — server computes{' '}
              <code>policy_verdict</code>.
            </p>
          </div>
          <button type="button" className="action secondary" onClick={load}>
            Refresh
          </button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>workflow_id</th>
                <th>repo</th>
                <th>owner</th>
                <th>verdict</th>
                <th>last_audited</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.workflow_id}>
                  <td>{row.workflow_id}</td>
                  <td>{row.repo}</td>
                  <td>{row.owner}</td>
                  <td>
                    <Badge verdict={row.att?.policy_verdict} />
                  </td>
                  <td>{row.att?.last_audited || row.last_audited}</td>
                  <td>
                    <button
                      type="button"
                      className="small"
                      onClick={() => openModal(row)}
                    >
                      Attest
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {modal && (
        <div className="modal-backdrop open">
          <div className="modal">
            <h3>UI Attestation — {modal.workflow_id}</h3>
            <p className="muted">
              Enter exactly what you observe. Invalid state is recorded, not hidden.
            </p>

            <div className="section-label">Observed evidence (free text)</div>
            <div className="field-row">
              <Field label="observed_model (e.g. gpt-5.4, Auto)">
                <input
                  value={form.observed_model}
                  onChange={(e) => updateField('observed_model', e.target.value)}
                  placeholder="gpt-5.4"
                />
              </Field>
              <Field label="observed_effort">
                <input
                  value={form.observed_effort}
                  onChange={(e) => updateField('observed_effort', e.target.value)}
                  placeholder="low / high / unknown"
                />
              </Field>
            </div>
            <div className="field-row">
              <Field label="observed_trigger">
                <input
                  value={form.observed_trigger}
                  onChange={(e) => updateField('observed_trigger', e.target.value)}
                  placeholder="manual / hourly"
                />
              </Field>
              <Field label="observed_mode">
                <input
                  value={form.observed_mode}
                  onChange={(e) => updateField('observed_mode', e.target.value)}
                  placeholder="autopilot / plan"
                />
              </Field>
            </div>
            <Field label="evidence_note">
              <textarea
                rows={2}
                value={form.evidence_note}
                onChange={(e) => updateField('evidence_note', e.target.value)}
                placeholder="Optional exception note for medium effort"
              />
            </Field>

            <div className="section-label">Desired policy (controlled)</div>
            <div className="field-row">
              <Field label="desired_model">
                <select
                  value={form.desired_model}
                  onChange={(e) => updateField('desired_model', e.target.value)}
                >
                  <option value="gpt-5-mini">gpt-5-mini</option>
                </select>
              </Field>
              <Field label="desired_effort">
                <select
                  value={form.desired_effort}
                  onChange={(e) => updateField('desired_effort', e.target.value)}
                >
                  <option value="low">low</option>
                </select>
              </Field>
              <Field label="desired_trigger">
                <select
                  value={form.desired_trigger}
                  onChange={(e) => updateField('desired_trigger', e.target.value)}
                >
                  <option value="manual">manual</option>
                </select>
              </Field>
            </div>
            <Field label="last_audited (YYYY-MM-DD)">
              <input
                value={form.last_audited}
                onChange={(e) => updateField('last_audited', e.target.value)}
              />
            </Field>

            {result && !result.error && (
              <Flash kind={result.policy_verdict === 'PASS' ? 'ok' : 'err'}>
                Server verdict: <Badge verdict={result.policy_verdict} />
                <br />
                {(result.verdict_reasons || []).join(' · ')}
              </Flash>
            )}
            {result?.error && <Flash kind="err">{result.error}</Flash>}

            <div className="row">
              <button type="button" className="action secondary" onClick={closeModal}>
                Cancel
              </button>
              <button
                type="button"
                className="action"
                onClick={saveAttestation}
                disabled={saving}
              >
                Save Draft Attestation
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function Field({ label, children }) {
  return (
    <div className="field">
      <label>{label}</label>
      {children}
    </div>
  );
}
