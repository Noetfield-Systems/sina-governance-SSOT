import { useCallback, useEffect, useState } from 'react';
import { api } from '../api';
import { getReceipt, getReceiptCache } from '../session';

export default function ReceiptsPage() {
  const [files, setFiles] = useState([]);
  const [selected, setSelected] = useState(null);

  const load = useCallback(async () => {
    const { ok, data } = await api.receiptsList();
    if (ok) setFiles((data.receipts || []).slice().reverse());
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  function select(name) {
    setSelected(name);
  }

  const cached = selected ? getReceipt(selected) : null;
  const meta = cached || inferFromName(selected);

  return (
    <div className="card">
      <div className="toolbar">
        <strong>Receipts</strong>
        <button type="button" className="action secondary" onClick={load}>
          Refresh
        </button>
      </div>
      <div className="split">
        <div>
          <table className="receipt-table">
            <thead>
              <tr>
                <th>path</th>
                <th>action</th>
                <th>result</th>
              </tr>
            </thead>
            <tbody>
              {files.length === 0 && (
                <tr>
                  <td colSpan={3} className="muted">
                    none yet
                  </td>
                </tr>
              )}
              {files.map((f) => {
                const row = getReceipt(f) || inferFromName(f);
                return (
                  <tr
                    key={f}
                    className={selected === f ? 'selected' : ''}
                    onClick={() => select(f)}
                  >
                    <td>{f}</td>
                    <td>{row?.action || '—'}</td>
                    <td>{formatResult(row)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div>
          {selected ? (
            <>
              <p className="muted">
                <strong>timestamp:</strong> {meta?.timestamp || 'unknown'}
                <br />
                <strong>action:</strong> {meta?.action || inferAction(selected)}
                <br />
                <strong>result:</strong> {formatResult(meta)}
                <br />
                <strong>path:</strong> receipts/{selected}
              </p>
              <pre>
                {cached
                  ? JSON.stringify(cached, null, 2)
                  : `Receipt on disk: receipts/${selected}\n\nFull JSON available after actions in this session cache it.`}
              </pre>
            </>
          ) : (
            <pre>Select a receipt to view details.</pre>
          )}
        </div>
      </div>
      <p className="muted" style={{ marginTop: 8 }}>
        Cached this session: {Object.keys(getReceiptCache()).length} receipt(s)
      </p>
    </div>
  );
}

function inferFromName(name) {
  if (!name) return null;
  return {
    path: `receipts/${name}`,
    action: inferAction(name),
    timestamp: null,
    policy_pass: name.includes('lock_candidate_ready') || name.includes('validation') && name.includes('PASS'),
  };
}

function inferAction(name) {
  if (name.startsWith('draft_save_')) return 'attestation_draft';
  if (name.startsWith('validation_')) return 'policy_check';
  if (name.startsWith('sync_')) return 'integrator_sync';
  if (name.startsWith('lock_candidate')) return 'lock_candidate';
  if (name.startsWith('registry_draft')) return 'registry_save_draft';
  return 'unknown';
}

function formatResult(row) {
  if (!row) return '—';
  if (row.status) return row.status;
  if (row.policy_verdict) return row.policy_verdict;
  if (typeof row.policy_pass === 'boolean') return row.policy_pass ? 'PASS' : 'FAIL';
  return '—';
}
