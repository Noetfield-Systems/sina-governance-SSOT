#!/usr/bin/env python3
"""Narrative intelligence — plain-language session story, founder intent, save locations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO_MAP = ROOT / "data/governance_repo_map_v1.json"

STATE_PLAIN = {
    "COMPLETED": "done — best version identified, no open gate",
    "PENDING_FOUNDER": "waiting on you — approve, reject, hold, or revise",
    "PENDING_THREAD": "almost done — blocked on a phase gate or a dependent patch in another thread",
    "IN_PROGRESS": "still moving — not the final word yet",
    "LEFT_ABANDONED": "left behind — only stale copies remain; work continued elsewhere",
}


def load_repo_map() -> dict:
    return json.loads(REPO_MAP.read_text(encoding="utf-8"))


def expand(path_str: str) -> Path:
    return Path(path_str).expanduser().resolve()


def repo_for_path(path: Path, repo_map: dict) -> dict:
    resolved = path.resolve()
    best: dict = {"repo_id": "unknown", "name": "Unknown", "authority_rank": 99, "role": "unmapped"}
    best_len = -1
    for repo in repo_map.get("repos", []):
        base = expand(repo.get("path", ""))
        if not base.exists():
            continue
        try:
            resolved.relative_to(base)
            if len(str(base)) > best_len:
                best = repo
                best_len = len(str(base))
        except ValueError:
            continue
    return best


def infer_founder_arcs(threads: list[dict], repo_map: dict) -> list[dict]:
    parts: list[str] = []
    for t in threads:
        parts.append(t.get("display_name", ""))
        parts.append(t.get("thread_id", ""))
        parts.extend(c.get("rationale", "") for c in t.get("change_timeline", []))
        parts.extend(p.get("text", "") for p in t.get("pending_items", []))
    blob = " ".join(p for p in parts if p).lower()

    arcs: list[dict] = []
    for pattern in repo_map.get("founder_arc_patterns", []):
        hits = [s for s in pattern.get("signals", []) if s.lower() in blob]
        if len(hits) >= 2:
            arcs.append(
                {
                    "arc_id": pattern.get("arc_id"),
                    "confidence": min(0.95, 0.5 + len(hits) * 0.1),
                    "matched_signals": hits,
                    "plain_summary": pattern.get("plain_summary"),
                }
            )
    return sorted(arcs, key=lambda a: -a.get("confidence", 0))


def guess_founder_why(thread: dict) -> str:
    timeline = thread.get("change_timeline", [])
    pending = thread.get("pending_items", [])
    state = thread.get("completion_state", "")
    role = (thread.get("final_carrier") or {}).get("role", "spec")
    name = thread.get("display_name", thread.get("thread_id", ""))

    if not timeline:
        if state == "COMPLETED":
            return f"You finished or parked **{name}** as a standalone piece — no edit trail in the file, but it reads complete enough to keep."
        return f"You started **{name}** but have not yet left a versioned edit trail the machine can read."

    good = [c for c in timeline if c.get("quality_verdict") == "good"]
    last = timeline[-1]
    reasons: list[str] = []

    if good:
        reasons.append(
            "The strongest edits were quality fixes: "
            + "; ".join(c["rationale"][:80] for c in good[:2])
        )
    reasons.append(f"Latest pass (v{last.get('version')}): {last.get('rationale', '')[:120]}")

    if role == "conflict_log":
        reasons.insert(0, "You were logging a rule conflict for founder ratification — not silently changing live law.")
    elif role == "proposal":
        reasons.insert(0, "You were proposing a new traceability/governance rule for later approval.")
    elif role == "spec" and "phase" in last.get("rationale", "").lower():
        reasons.insert(0, "You were sequencing phased work so automation cannot jump ahead of founder gates.")

    if pending:
        reasons.append("Still open: " + ", ".join(p["text"] for p in pending))

    return " ".join(reasons)


def build_save_location_index(threads: list[dict], repo_map: dict) -> list[dict]:
    rows: list[dict] = []
    for thread in threads:
        final = thread.get("final_carrier") or {}
        path_str = final.get("path")
        if not path_str:
            continue
        path = Path(path_str)
        repo = repo_for_path(path, repo_map)
        rows.append(
            {
                "thread_id": thread.get("thread_id"),
                "display_name": thread.get("display_name"),
                "most_complete_path": path_str,
                "repo_id": repo.get("repo_id"),
                "repo_name": repo.get("name"),
                "repo_path": repo.get("path"),
                "authority_rank": repo.get("authority_rank"),
                "completion_state": thread.get("completion_state"),
                "progress_pct": thread.get("progress_pct"),
                "completeness_score": final.get("completeness_score"),
                "should_promote_to": "data/governance_intake_staging_v1/" + thread.get("thread_id", "unknown") + "/"
                if repo.get("intake")
                else "already in " + repo.get("repo_id", "unknown"),
            }
        )
    return sorted(rows, key=lambda r: (-r.get("progress_pct", 0), -r.get("completeness_score", 0)))


def build_repo_structure_summary(repo_map: dict) -> list[dict]:
    rows = []
    for repo in repo_map.get("repos", []):
        base = expand(repo.get("path", ""))
        rows.append(
            {
                "repo_id": repo.get("repo_id"),
                "name": repo.get("name"),
                "path": str(base) if base.exists() else repo.get("path"),
                "exists": base.exists(),
                "authority_rank": repo.get("authority_rank"),
                "write_owner": repo.get("write_owner"),
                "role": repo.get("role"),
                "intake": bool(repo.get("intake")),
            }
        )
    return sorted(rows, key=lambda r: r.get("authority_rank", 99))


def paragraph_thread_story(thread: dict, repo_map: dict) -> str:
    final = thread.get("final_carrier") or {}
    path_str = final.get("path", "")
    repo = repo_for_path(Path(path_str), repo_map) if path_str else {}
    state_plain = STATE_PLAIN.get(thread.get("completion_state", ""), thread.get("completion_state", ""))
    why = guess_founder_why(thread)
    left_n = len(thread.get("left_abandoned", []))
    left_note = f" ({left_n} stale copies left on disk)" if left_n else ""
    loc = f"`{path_str}`" if path_str else "no final file"
    repo_note = repo.get("name", "unknown repo")

    return (
        f"**{thread.get('display_name')}** — {state_plain}{left_note}. "
        f"Best file today: {loc} in **{repo_note}** ({thread.get('progress_pct')}% progress). "
        f"{why}"
    )


def build_plain_story(
    thread_audit: dict,
    repo_map: dict,
    merge_plan: dict | None = None,
    intake_root: str | None = None,
) -> str:
    threads = thread_audit.get("threads", [])
    summary = thread_audit.get("summary", {})
    arcs = infer_founder_arcs(threads, repo_map)
    saves = build_save_location_index(threads, repo_map)
    repos = build_repo_structure_summary(repo_map)

    lines: list[str] = []
    lines.append("## The whole story")
    if intake_root:
        lines.append(f"This is an advisor-session intake folder: `{intake_root}`. Nothing here is live SG law until staged and registered.")
    lines.append("")

    lines.append("### What you were doing (machine guess)")
    if arcs:
        for arc in arcs[:3]:
            lines.append(f"- **{arc['arc_id'].replace('_', ' ').title()}** ({int(arc['confidence']*100)}% confidence): {arc['plain_summary']}")
    else:
        lines.append("- The machine sees scattered drafts without a strong shared arc yet — likely early sorting or mixed topics.")
    lines.append("")

    lines.append("### Repo structure (who owns what)")
    for r in repos:
        flag = "INTAKE" if r.get("intake") else f"rank {r['authority_rank']}"
        exists = "on disk" if r.get("exists") else "path missing"
        lines.append(f"- **{r['name']}** ({flag}, {exists}): {r['role']}. Writes: `{r.get('write_owner')}`.")
    lines.append("")

    lines.append("### Progress snapshot")
    lines.append(
        f"- **{summary.get('completed', 0)} completed** · "
        f"**{summary.get('pending_founder', 0)} waiting on founder** · "
        f"**{summary.get('pending_thread', 0)} blocked on thread/phase** · "
        f"**{summary.get('in_progress', 0)} in progress**"
    )
    lines.append("")

    lines.append("### Where the most complete files live")
    for row in saves[:8]:
        lines.append(
            f"- **{row['display_name']}** → `{row['most_complete_path']}` "
            f"({row['completion_state']}, {row['progress_pct']}%) · promote target: `{row['should_promote_to']}`"
        )
    lines.append("")

    lines.append("### Thread-by-thread")
    for thread in sorted(threads, key=lambda t: -t.get("progress_pct", 0)):
        lines.append(f"- {paragraph_thread_story(thread, repo_map)}")
    lines.append("")

    if merge_plan:
        ms = merge_plan.get("summary", {})
        lines.append("### Merge plan")
        lines.append(
            f"- **{ms.get('auto_count', 0)} auto-safe actions** (stage to SG intake, void stale pointers, section adopts without conflict)"
        )
        lines.append(f"- **{ms.get('manual_count', 0)} manual actions** (founder ratification, registry promotion, cross-repo copies)")
        if merge_plan.get("staging_root"):
            lines.append(f"- Staging folder: `{merge_plan['staging_root']}`")
        lines.append("")

    lines.append("### What happens next (sensible order)")
    open_threads = [t for t in threads if t.get("completion_state") != "COMPLETED"]
    if any(t.get("completion_state") == "PENDING_FOUNDER" for t in open_threads):
        lines.append("1. Close **PENDING_FOUNDER** threads first — conflict log and versioning proposal need your 5-option decision.")
    if any(t.get("completion_state") == "PENDING_THREAD" for t in open_threads):
        lines.append("2. Then unblock **PENDING_THREAD** work — Brain Gate Phase 2 stays closed until Phase 1 registry is verified.")
    if merge_plan and merge_plan.get("auto_actions"):
        lines.append("3. Run **auto-merge (dry-run)** then `--apply` to stage best intake files into SG without touching venture repos.")
    lines.append("4. Manual promote: registry rows + library pointers only after receipts — never direct write to SourceA from this lane.")
    lines.append("")

    return "\n".join(lines)


def build_session_story(
    thread_audit: dict,
    repo_map: dict | None = None,
    merge_plan: dict | None = None,
    intake_root: str | None = None,
) -> dict[str, Any]:
    repo_map = repo_map or load_repo_map()
    threads = thread_audit.get("threads", [])
    story = build_plain_story(thread_audit, repo_map, merge_plan, intake_root)

    return {
        "schema": "governance-session-story-v1",
        "intake_root": intake_root,
        "founder_arcs": infer_founder_arcs(threads, repo_map),
        "repo_structure": build_repo_structure_summary(repo_map),
        "save_location_index": build_save_location_index(threads, repo_map),
        "thread_stories": [
            {
                "thread_id": t.get("thread_id"),
                "display_name": t.get("display_name"),
                "completion_state": t.get("completion_state"),
                "founder_why_guess": guess_founder_why(t),
                "paragraph": paragraph_thread_story(t, repo_map),
            }
            for t in threads
        ],
        "plain_story": story,
        "summary": thread_audit.get("summary", {}),
        "ok": bool(threads),
    }
