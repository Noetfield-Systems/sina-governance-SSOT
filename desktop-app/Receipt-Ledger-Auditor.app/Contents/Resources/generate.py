#!/usr/bin/env python3
"""Runs scripts/audit_receipt_ledger_v1.py fresh (read-only, no --write-receipt)
and renders a live HTML dashboard."""
import html
import json
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
  details summary { cursor:pointer; font-weight:600; color:#444; padding:6px 0; }
  pre.raw { background:#0f1115; color:#d7dbe0; padding:14px 16px; border-radius:8px; font-size:12.5px; overflow-x:auto; white-space:pre-wrap; }
  .empty { color:#5a9; font-size:13px; padding: 6px 0; }
  .cluster { border-left:3px solid #b3261e; background:#fff7f7; padding:10px 14px; border-radius:6px; margin-bottom:10px; }
  .foot { color:#999; font-size:11.5px; margin-top:30px; text-align:center; }
</style>
"""


def e(s):
    return html.escape(str(s))


def run_audit():
    try:
        proc = subprocess.run(
            ["python3", "scripts/audit_receipt_ledger_v1.py", "--json"],
            cwd=str(REPO), capture_output=True, text=True, timeout=60,
        )
        return json.loads(proc.stdout), None
    except Exception as ex:  # noqa: BLE001
        return None, str(ex)


def main():
    data, err = run_audit()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    if err or data is None:
        body = f'<div class="card"><h2>Error</h2><pre class="raw">{e(err)}</pre></div>'
        ok = False
    else:
        ok = data.get("ok", False)
        clusters = data.get("clusters", [])
        malformed = data.get("malformed", [])
        missing_ts = data.get("missing_timestamp", [])
        families = data.get("receipt_families_informational", {})

        stats_html = (
            '<div class="stat-row">'
            f'<div class="stat"><div class="num">{data.get("receipts_scanned",0)}</div><div class="label">Receipts scanned</div></div>'
            f'<div class="stat"><div class="num">{len(clusters)}</div><div class="label">Cross-motor clusters</div></div>'
            f'<div class="stat"><div class="num">{data.get("malformed_count",0)}</div><div class="label">Malformed</div></div>'
            f'<div class="stat"><div class="num">{data.get("missing_timestamp_count",0)}</div><div class="label">No timestamp</div></div>'
            "</div>"
        )

        if clusters:
            cluster_html = ""
            for c in clusters:
                files = "".join(f"<li class='mono'>{e(f)}</li>" for f in c.get("files", []))
                cluster_html += (
                    f'<div class="cluster"><b>{e(c.get("window_start"))} &rarr; {e(c.get("window_end"))}</b>'
                    f'<ul>{files}</ul><div style="color:#a33;font-size:12.5px">{e(c.get("note",""))}</div></div>'
                )
        else:
            cluster_html = '<div class="empty">No cross-motor clusters found &mdash; no receipts of different types landed within the collision window.</div>'

        if malformed:
            mal_html = "<table><thead><tr><th>File</th><th>Error</th></tr></thead><tbody>" + "".join(
                f'<tr><td class="mono">{e(m["file"])}</td><td>{e(m["error"])}</td></tr>' for m in malformed
            ) + "</tbody></table>"
        else:
            mal_html = '<div class="empty">None.</div>'

        if missing_ts:
            mt_html = "<ul>" + "".join(f'<li class="mono">{e(m["file"])}</li>' for m in missing_ts) + "</ul>"
        else:
            mt_html = '<div class="empty">Every scanned receipt has a resolvable date.</div>'

        fam_rows = "".join(
            f'<tr><td class="mono">{e(k)}</td><td>{len(v)}</td></tr>' for k, v in sorted(families.items(), key=lambda kv: -len(kv[1]))
        )
        fam_html = (
            "<table><thead><tr><th>Receipt family</th><th>Count</th></tr></thead><tbody>" + fam_rows + "</tbody></table>"
            if families else '<div class="empty">No recurring receipt families.</div>'
        )

        body = f"""
        <div class="card"><h2>Summary</h2>{stats_html}</div>
        <div class="card"><h2>Cross-motor clusters ({len(clusters)}) &mdash; look at these first</h2>{cluster_html}</div>
        <div class="card"><h2>Malformed receipts ({len(malformed)})</h2>{mal_html}</div>
        <div class="card"><details><summary>Missing timestamp ({len(missing_ts)})</summary>{mt_html}</details></div>
        <div class="card"><details><summary>Receipt families &mdash; informational, not a finding ({len(families)})</summary>{fam_html}</details></div>
        """

    html_out = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Receipt Ledger Auditor</title>{STYLE}</head>
<body><div class="wrap">
  <div class="hdr"><h1>Receipt Ledger Auditor</h1>
    <span class="badge {'ok' if ok else 'bad'}">{'CLEAN' if ok else 'FINDINGS'}</span></div>
  <div class="meta">sina-governance-SSOT &middot; live run at {e(now)} &middot; wraps scripts/audit_receipt_ledger_v1.py (read-only view)</div>
  {body}
  <div class="foot">Regenerate: reopen this app. Write an audit receipt of its own: python3 scripts/audit_receipt_ledger_v1.py --write-receipt</div>
</div></body></html>"""

    out_path = Path("/tmp/receipt-ledger-auditor-report.html")
    out_path.write_text(html_out, encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
