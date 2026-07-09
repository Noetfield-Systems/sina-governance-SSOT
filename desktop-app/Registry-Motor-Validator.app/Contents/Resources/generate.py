#!/usr/bin/env python3
"""Runs validate_parallel_automation_governance_v1.py and
audit_automation_surface_v1.py fresh and renders a live HTML dashboard.
Note: audit_automation_surface_v1.py writes its own receipt by design every
time it runs (that isn't this app's choice) -- see the skill for why."""
import html
import subprocess
from datetime import datetime, timezone
from pathlib import Path

def _resolve_repo() -> Path:
    """Locate the governance repo root without a hardcoded machine path (DX-3).
    Order: SG_REPO_ROOT env -> git toplevel from this file -> walk up for a
    data/+scripts/ marker -> legacy default (last-resort, preserves capability)."""
    import os, subprocess
    env = os.environ.get("SG_REPO_ROOT")
    if env and Path(env).is_dir():
        return Path(env)
    here = Path(__file__).resolve()
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=here.parent,
            text=True, capture_output=True, check=True).stdout.strip()
        if top and (Path(top) / "data").is_dir() and (Path(top) / "scripts").is_dir():
            return Path(top)
    except Exception:
        pass
    for parent in here.parents:
        if (parent / "data").is_dir() and (parent / "scripts").is_dir():
            return parent
    return Path("/Users/sinakazemnezhad/Desktop/Noetfield-Systems/sina-governance-SSOT")


REPO = _resolve_repo()

STYLE = """
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body { margin:0; padding:0; background:#f4f5f7; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; color:#1d2129; }
  .wrap { max-width: 980px; margin: 0 auto; padding: 28px 24px 60px; }
  .hdr { display:flex; align-items:center; justify-content:space-between; margin-bottom: 6px; }
  .hdr h1 { font-size: 20px; margin: 0; }
  .badge { display:inline-block; padding: 5px 14px; border-radius: 999px; font-weight:600; font-size:13px; }
  .badge.ok { background:#e3f8ea; color:#177245; }
  .badge.bad { background:#fdeaea; color:#b3261e; }
  .meta { color:#666; font-size:12.5px; margin-bottom:22px; }
  .card { background:#fff; border:1px solid #e6e7eb; border-radius:10px; padding:18px 20px; margin-bottom:18px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }
  .card h2 { display:flex; align-items:center; gap:10px; font-size:14px; margin:0 0 12px; text-transform:uppercase; letter-spacing:.04em; color:#555; }
  pre.raw { background:#0f1115; color:#d7dbe0; padding:14px 16px; border-radius:8px; font-size:12.5px; overflow-x:auto; white-space:pre-wrap; }
  .foot { color:#999; font-size:11.5px; margin-top:30px; text-align:center; }
  .mini-badge { font-size:11px; padding:2px 9px; border-radius:999px; font-weight:700; }
  .mini-badge.ok { background:#e3f8ea; color:#177245; }
  .mini-badge.bad { background:#fdeaea; color:#b3261e; }
</style>
"""


def e(s):
    return html.escape(str(s))


def run(cmd):
    try:
        proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=60)
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except Exception as ex:  # noqa: BLE001
        return 1, str(ex)


def main():
    rc1, out1 = run(["python3", "scripts/validate_parallel_automation_governance_v1.py"])
    rc2, out2 = run(["python3", "scripts/audit_automation_surface_v1.py"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    ok = rc1 == 0 and rc2 == 0

    def badge(rc):
        return f'<span class="mini-badge {"ok" if rc == 0 else "bad"}">{"PASS" if rc == 0 else "FAIL"}</span>'

    body = f"""
    <div class="card"><h2>validate_parallel_automation_governance_v1.py {badge(rc1)}</h2>
      <pre class="raw">{e(out1)}</pre></div>
    <div class="card"><h2>audit_automation_surface_v1.py {badge(rc2)}</h2>
      <pre class="raw">{e(out2)}</pre></div>
    """

    html_out = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Registry / Motor Validator</title>{STYLE}</head>
<body><div class="wrap">
  <div class="hdr"><h1>Registry / Motor Validator</h1>
    <span class="badge {'ok' if ok else 'bad'}">{'ALL PASS' if ok else 'FAILURES'}</span></div>
  <div class="meta">sina-governance-SSOT &middot; live run at {e(now)} &middot; enforces L1 (one writer per task cell) and L4 (registry is routing truth)</div>
  {body}
  <div class="foot">Note: audit_automation_surface_v1.py writes its own receipt to receipts/ every run &mdash; that's the underlying script's own design, not something this dashboard adds.</div>
</div></body></html>"""

    out_path = Path("/tmp/registry-motor-validator-report.html")
    out_path.write_text(html_out, encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
