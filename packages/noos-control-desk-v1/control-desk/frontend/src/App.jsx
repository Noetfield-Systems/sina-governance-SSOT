import { useState } from 'react';
import DashboardPage from './pages/DashboardPage';
import RegistryPage from './pages/RegistryPage';
import AttestationPage from './pages/AttestationPage';
import PolicyPage from './pages/PolicyPage';
import IntegratorPage from './pages/IntegratorPage';
import ReceiptsPage from './pages/ReceiptsPage';
import PrPrepPage from './pages/PrPrepPage';

const TABS = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'registry', label: 'Workflow Registry' },
  { id: 'attestation', label: 'Copilot Attestation' },
  { id: 'policy', label: 'Policy Validator' },
  { id: 'integrator', label: 'Integrator Sync' },
  { id: 'receipts', label: 'Receipts' },
  { id: 'prprep', label: 'PR Prep' },
];

export default function App() {
  const [tab, setTab] = useState('dashboard');

  return (
    <>
      <header>
        <h1>NOOS CONTROL DESK</h1>
        <span className="sub">Phase 1 · localhost</span>
      </header>
      <nav>
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            className={tab === t.id ? 'active' : ''}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <main>
        {tab === 'dashboard' && <DashboardPage />}
        {tab === 'registry' && <RegistryPage />}
        {tab === 'attestation' && <AttestationPage />}
        {tab === 'policy' && <PolicyPage />}
        {tab === 'integrator' && <IntegratorPage />}
        {tab === 'receipts' && <ReceiptsPage />}
        {tab === 'prprep' && <PrPrepPage />}
      </main>
    </>
  );
}
