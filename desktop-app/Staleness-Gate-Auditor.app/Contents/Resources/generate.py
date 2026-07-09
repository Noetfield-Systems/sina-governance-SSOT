#!/usr/bin/env python3
"""Runs scripts/agent_read_staleness_engine_v1.py fresh and renders a live
HTML dashboard. Read-only: does not pass --write-receipt/--write-queue, so
opening this app never mutates the repo -- it's a look, not a gate run."""
import html
import json
import subprocess
import sys
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
  .card h2 { font-size:14px; margin:0 0 12px; text-transform:uppercase; letter-spacing:.04em; color:#555; }
  .stat-row { display:flex; gap:14px; flex-wrap:wrap; }
  .stat { flex:1; min-width:120px; background:#fafafa; border:1px solid #eee; border-radius:8px; padding:12px 14px; }
  .stat .num { font-size:22px; font-weight:700; }
  .stat .label { font-size:12px; color:#777; margin-top:2px; }
  table { width:100%; border-collapse: collapse; font-size:13px; }
  th, td { text-align:left; padding:7px 8px; border-bottom:1px solid #f0f0f0; vertical-align:top; }
  th { color:#888; font-weight:600; font-size:11.5px; text-transform:uppercase; letter-spacing:.03em; }
  tr:last-child td { border-bottom:none; }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:12.5px; }
  .sev-blocker { color:#b3261e; font-weight:700; }
  .sev-warn { color:#8a5b00; font-weight:700; }
  details summary { cursor:pointer; font-weight:600; color:#444; padding:6px 0; }
  pre.raw { background:#0f1115; color:#d7dbe0; padding:14px 16px; border-radius:8px; font-size:12.5px; overflow-x:auto; white-space:pre-wrap; }
  .empty { color:#5a9; font-size:13px; padding: 6px 0; }
  .note { background:#fff6e0; border:1px solid #f0e0b0; color:#7a5b00; border-radius:8px; padding:10px 14px; font-size:12.5px; margin-bottom:16px; }
  .foot { color:#999; font-size:11.5px; margin-top:30px; text-align:center; }
</style>
"""


def e(s):
    return html.escape(str(s))


def run_engine():
    try:
        proc = subprocess.run(
            ["python3", "scripts/agent_read_staleness_engine_v1.py", "--json", "--fail-on", "never"],
            cwd=str(REPO), capture_output=True, text=True, timeout=60,
        )
        return json.loads(proc.stdout), None
    except Exception as ex:  # noqa: BLE001
        return None, str(ex)


def rows_for(items, cols):
    if not items:
        return '<div class="empty">None.</div>'
    out = ["<table><thead><tr>"]
    for c in cols:
        out.append(f"<th>{e(c)}</th>")
    out.append("</tr></thead><tbody>")
    for it in items:
        out.append("<tr>")
        for c in cols:
            key = c.lower().replace(" ", "_")
            val = it.get(key, "")
            cls = "sev-blocker" if (key == "severity" and val == "BLOCKER") else ("sev-warn" if key == "severity" else "mono")
            out.append(f'<td class="{cls}">{e(val)}</td>')
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def main():
    data, err = run_engine()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    if err or data is None:
        body = f'<div class="card"><h2>Error</h2><pre class="raw">{e(err)}</pre></div>'
        ok = False
        stats_html = ""
    else:
        ok = data.get("ok", False)
        stats_html = (
            '<div class="stat-row">'
            f'<div class="stat"><div class="num">{data.get("alive_surfaces", 0)}</div><div class="label">Alive surfaces</div></div>'
            f'<div class="stat"><div class="num">{data.get("blocker_count", 0)}</div><div class="label">Blockers</div></div>'
            f'<div class="stat"><div class="num">{data.get("warn_count", 0)}</div><div class="label">Warnings</div></div>'
            "</div>"
        )
        blockers = data.get("blockers", [])
        warns = data.get("warns", [])
        alive = data.get("alive", [])

        cross_repo_note = ""
        if blockers and any(b.get("kind") == "missing_read_surface" for b in blockers):
            cross_repo_note = (
                '<div class="note">Some blockers below are <span class="mono">missing_read_surface</span> '
                "for docs in sibling venture repos (SourceA, TrustField-Technologies, noetfeld-OS). "
                "If this app is running somewhere those repos aren't checked out, these will show as "
                "false blockers &mdash; verify the paths actually exist on this machine before treating "
                "them as real staleness.</div>"
            )

        body = f"""
        <div class="card"><h2>Summary</h2>{stats_html}</div>
        {cross_repo_note}
        <div class="card"><h2>Blockers ({len(blockers)})</h2>
          {rows_for(blockers, ["Severity", "Kind", "Lane", "Path", "Role"])}
        </div>
        <div class="card"><h2>Warnings ({len(warns)})</h2>
          {rows_for(warns, ["Severity", "Kind", "Lane", "Path", "Role"])}
        </div>
        <div class="card"><details><summary>Alive docs ({len(alive)})</summary>
          {rows_for(alive, ["Lane", "Path", "Status", "Role", "Last_modified"])}
        </details></div>
        """

    html_out = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Staleness Gate Auditor</title>{STYLE}</head>
<body><div class="wrap">
  <div class="hdr"><h1>Staleness Gate Auditor</h1>
    <span class="badge {'ok' if ok else 'bad'}">{'CLEAN' if ok else 'BLOCKERS FOUND'}</span></div>
  <div class="meta">sina-governance-SSOT &middot; live run at {e(now)} &middot; wraps scripts/agent_read_staleness_engine_v1.py (read-only view, no receipt written)</div>
  {body}
  <div class="foot">Regenerate: reopen this app. Real gate run (writes receipt): scripts/verify_agent_read_staleness_v1.sh</div>
</div></body></html>"""

    out_path = Path("/tmp/staleness-gate-auditor-report.html")
    out_path.write_text(html_out, encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
