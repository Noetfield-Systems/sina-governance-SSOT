#!/usr/bin/env python3
"""Run one machine-autonomy cycle — validation, repair, receipt — no founder routing."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOPS = ROOT / "data/machine_autonomy_loops_v1.json"
RECEIPTS = ROOT / "receipts"
CANON_VERSION = "founder_canon_v1.0.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 90) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd or ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip()[-500:]
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def main() -> int:
    loops_doc = json.loads(LOOPS.read_text(encoding="utf-8"))
    ts = utc_now()
    receipt_id = f"machine-autonomy-cycle-{ts}"

    steps: list[dict] = []

    # L2 — machine validation (Mac-safe)
    for script in [
        "scripts/brain_loop_health_check_v1.sh",
    ]:
        code, tail = run(["bash", str(ROOT / script)])
        steps.append({"loop": "L2-MACHINE-VALID", "step": script, "ok": code == 0, "tail": tail})

    for script in [
        "scripts/validate_parallel_automation_governance_v1.py",
        "scripts/validate_governance_intelligence_v1.py",
        "scripts/audit_automation_drift_v1.py",
    ]:
        code, tail = run(["/usr/bin/python3", str(ROOT / script)])
        steps.append({"loop": "L2-MACHINE-VALID", "step": script, "ok": code == 0, "tail": tail})

    # L4 — self-repair if health/drift failed
    drift_failed = any(s["step"].endswith("audit_automation_drift_v1.py") and not s["ok"] for s in steps)
    health_failed = any("brain_loop_health" in s["step"] and not s["ok"] for s in steps)
    if drift_failed or health_failed:
        code, tail = run(["bash", str(ROOT / "scripts/repair_sourcea_worktree_v1.sh")])
        steps.append({"loop": "L4-SELF-REPAIR", "step": "repair_sourcea_worktree_v1.sh", "ok": code == 0, "tail": tail})
        if health_failed:
            code2, tail2 = run(["bash", str(ROOT / "scripts/brain_loop_health_check_v1.sh")])
            steps.append({"loop": "L4-SELF-REPAIR", "step": "revalidate health", "ok": code2 == 0, "tail": tail2})

    # L3/L5 — gate alignment (observe only; full verifier needs CF tokens)
    code, tail = run(["/usr/bin/python3", str(ROOT / "scripts/diagnose_gate_candidate_alignment_v1.py")])
    steps.append({"loop": "L5-OUTSIDE-AUDIT", "step": "diagnose_gate_candidate_alignment_v1", "ok": code == 0, "tail": tail})

    # L7 — ROI heartbeat
    code, tail = run(["/usr/bin/python3", str(ROOT / "scripts/write_roi_heartbeat_v1.py")])
    steps.append({"loop": "L7-RECEIPT-PROOF", "step": "write_roi_heartbeat_v1", "ok": code == 0, "tail": tail})

    # Founder canon + governance intelligence wiring
    code, tail = run(["/usr/bin/python3", str(ROOT / "scripts/validate_founder_canon_e2e_v1.py")])
    steps.append({"loop": "L2-MACHINE-VALID", "step": "validate_founder_canon_e2e_v1", "ok": code == 0, "tail": tail})

    code, tail = run(["/usr/bin/python3", str(ROOT / "scripts/governance_intelligence_engine_v1.py"), "audit", "--json", "--no-write-queue"])
    steps.append({"loop": "L2-MACHINE-VALID", "step": "governance_intelligence_engine_v1 audit", "ok": code == 0, "tail": tail})

    failed = [s for s in steps if not s["ok"]]
    cycle_ok = len(failed) == 0

    receipt = {
        "schema": "machine-autonomy-cycle-v1",
        "receipt_id": receipt_id,
        "recorded_at": ts,
        "canon_version": CANON_VERSION,
        "default_question": loops_doc.get("default_question"),
        "cycle_ok": cycle_ok,
        "steps": steps,
        "failed_count": len(failed),
        "founder_required": False,
        "escalation": "L6-DEEP-RESEARCH" if len(failed) >= 3 else ("L4-SELF-REPAIR" if failed else "none"),
        "note": "Hygiene failures do not route to founder — see ssot/MACHINE_AUTONOMY_LOOPS_v1.md",
    }

    RECEIPTS.mkdir(parents=True, exist_ok=True)
    out_path = RECEIPTS / f"{receipt_id}.json"
    out_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(f"machine_autonomy_cycle_v1: {'OK' if cycle_ok else 'DEGRADED'}")
    print(json.dumps({"receipt_id": receipt_id, "failed_count": len(failed), "path": str(out_path)}, indent=2))
    return 0 if cycle_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
