import { useState } from 'react';
import { api } from '../api';
import Flash from '../components/Flash';
import { cacheReceipt, setLastPolicyCheck } from '../session';

export default function PolicyPage() {
  const [flash, setFlash] = useState(null);
  const [violations, setViolations] = useState([]);
  const [report, setReport] = useState(null);
  const [receiptPath, setReceiptPath] = useState('');
  const [running, setRunning] = useState(false);

  async function runCheck() {
    setRunning(true);
    setFlash({ kind: 'ok', text: 'Running checker…' });
    const { ok, data } = await api.policyCheck();
    setRunning(false);
    if (!ok || data.status === 'ERROR') {
      setFlash({ kind: 'err', text: data.message || 'Policy check failed' });
      setReport(data);
      setViolations([]);
      setReceiptPath('');
      return;
    }
    const r = data.report || {};
    const active = r.violations_active || [];
    setViolations(active);
    setReport(r);
    setReceiptPath(data.receipt || '');
    setLastPolicyCheck({ report: r, receipt: data.receipt });
    if (data.receipt) cacheReceipt(data.receipt, data);
    setFlash({
      kind: r.status === 'PASS' ? 'ok' : 'err',
      text: `${r.status}: ${r.violations_found || 0} found, ${active.length} active`,
    });
  }

  return (
    <div className="card">
      <div className="toolbar">
        <div>
          <strong>Policy Validator</strong>
          <p className="muted">
            POST /api/policy/check — aggregated errors only, never first-error-only.
          </p>
        </div>
        <button type="button" className="action" onClick={runCheck} disabled={running}>
          Run policy check
        </button>
      </div>
      {flash && <Flash kind={flash.kind}>{flash.text}</Flash>}
      {receiptPath && (
        <p className="muted">
          Receipt: <code>{receiptPath}</code>
        </p>
      )}
      <ul className="violation-list">
        {violations.length === 0 && report && (
          <li className="violation-none">No active violations</li>
        )}
        {violations.map((v, i) => (
          <li key={i}>{typeof v === 'string' ? v : JSON.stringify(v)}</li>
        ))}
      </ul>
      <pre>{report ? JSON.stringify(report, null, 2) : 'Not run yet this session.'}</pre>
    </div>
  );
}
