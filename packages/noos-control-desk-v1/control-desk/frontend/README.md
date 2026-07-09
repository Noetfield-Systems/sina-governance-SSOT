# NOOS Control Desk — Frontend (Phase 1, Step 3)

React + Vite SPA built into `control-desk/static/` for **http://localhost:17877**.

## Run

```bash
# Terminal 1 — backend
cd packages/noos-control-desk-v1
python3 control-desk/app.py --port 17877 --repo-root .

# Terminal 2 — rebuild frontend after edits
cd control-desk/frontend
npm install
npm run build
```

Open **http://localhost:17877**

Dev mode with HMR (proxied API):

```bash
npm run dev   # http://localhost:5173
```

## Smoke test

```bash
python3 control-desk/frontend/scripts/smoke_test.py
```

Receipt: `receipts/frontend_step3_smoke_v1.json`

## Seven tiles

Dashboard · Workflow Registry · Copilot Attestation · Policy Validator · Integrator Sync · Receipts · PR Prep

Policy verdict is server-side only. Observed fields are free-text evidence. No cloud propagation, Electron, or Selenium.
