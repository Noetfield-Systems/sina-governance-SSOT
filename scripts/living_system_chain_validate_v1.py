#!/usr/bin/env python3
"""LIVING_SYSTEM_DOCTRINE §8 liveness rubric validator (LS-021 stub; LS-022–026 wire collectors)."""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = (
    ROOT
    / "SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/P0-CORE/LIVING_SYSTEM_DOCTRINE_v1.1_LOCKED.md"
)
PLANS = ROOT / "data/living_system_110_plans_v1_LOCKED.json"
SUBSYSTEMS = ROOT / "data/living_system_subsystems_v1.json"
REGISTRY = ROOT / "data/github_automation_registry_v1.json"
RECEIPTS = ROOT / "receipts"

MANUAL_TRIGGERS = frozenset({"founder-manual", "cursor", "agent-session", "mac-complement"})
SCHEDULED_MOTOR_KINDS = frozenset({"github_actions", "cloudflare_cron", "railway_cron"})
MANUAL_ONLY_SCHEMAS = frozenset({
    "living_system_w0_install_receipt_v1",
    "living_system_w1_parallel_start_receipt_v1",
})
PULSE_SCHEMAS = frozenset({
    "agent_read_staleness_receipt_v1",
    "workflow_census_receipt_v1",
    "brain_loop_autorun_receipt_v1",
})


@dataclass
class RubricCheck:
    id: str
    doctrine_ref: str
    status: str  # PASS | FAIL | STUB | SKIP
    detail: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class RubricReport:
    schema: str = "living_system_rubric_report_v1"
    saved_at: str = ""
    subsystem_id: str = "global"
    verdict: str = "STALE"
    mode: str = "full"
    checks: list[RubricCheck] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "saved_at": self.saved_at,
            "subsystem_id": self.subsystem_id,
            "verdict": self.verdict,
            "mode": self.mode,
            "checks": [asdict(c) for c in self.checks],
        }


def check_spine_files() -> RubricCheck:
    missing = [p for p in (DOCTRINE, PLANS) if not p.is_file()]
    if missing:
        return RubricCheck(
            id="spine_files",
            doctrine_ref="bootstrap",
            status="FAIL",
            detail="missing spine files",
            evidence=[str(p.relative_to(ROOT)) for p in missing],
        )
    return RubricCheck(
        id="spine_files",
        doctrine_ref="bootstrap",
        status="PASS",
        detail="doctrine and plans locked on disk",
        evidence=[str(DOCTRINE.relative_to(ROOT)), str(PLANS.relative_to(ROOT))],
    )


def _parse_receipt_time(payload: dict[str, Any], path: Path) -> datetime | None:
    for key in ("saved_at", "at", "timestamp", "created_at", "recorded_at"):
        raw = payload.get(key)
        if not raw:
            continue
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            continue
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return None


def _glob_receipts(pattern: str) -> list[Path]:
    pat = pattern.replace("**/", "")
    if "/" in pat:
        base, name = pat.rsplit("/", 1)
        root = ROOT / base
    else:
        root = RECEIPTS
        name = pat
    if not root.is_dir():
        return []
    return sorted(root.glob(name))


def _registry_pulse_globs() -> list[str]:
    if not REGISTRY.is_file():
        return []
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    globs: list[str] = []
    for motor in reg.get("motors", []):
        if motor.get("kind") not in SCHEDULED_MOTOR_KINDS:
            continue
        rp = motor.get("receipt_path")
        if rp:
            globs.append(rp)
    return globs


def _is_scheduled_pulse(payload: dict[str, Any], path: Path) -> bool:
    schema = str(payload.get("schema", ""))
    if schema in MANUAL_ONLY_SCHEMAS:
        return False
    if payload.get("trigger_host") in MANUAL_TRIGGERS:
        return False
    if payload.get("manual_run") is True:
        return False
    if payload.get("trigger_host") == "cloud":
        return True
    if schema in PULSE_SCHEMAS:
        return True
    motor_id = payload.get("motor_id")
    if motor_id and REGISTRY.is_file():
        reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
        kinds = {m.get("motor_id"): m.get("kind") for m in reg.get("motors", [])}
        if kinds.get(motor_id) in SCHEDULED_MOTOR_KINDS:
            return True
    # agent-read / workflow census filenames from GHA motors
    name = path.name
    if fnmatch.fnmatch(name, "agent-read-staleness-*.json"):
        return True
    if fnmatch.fnmatch(name, "workflow-census-*.json"):
        return True
    if fnmatch.fnmatch(name, "brain-loop-autorun-*.json"):
        return payload.get("trigger_host") != "mac-complement"
    return False


def check_pulse_scheduled(subsystem: dict[str, Any] | None) -> RubricCheck:
    window_h = int((subsystem or {}).get("window_hours", 168))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_h)
    globs = list((subsystem or {}).get("pulse_receipt_globs") or [])
    globs.extend(_registry_pulse_globs())
    seen: set[str] = set()
    paths: list[Path] = []
    for g in globs:
        if g in seen:
            continue
        seen.add(g)
        paths.extend(_glob_receipts(g))

    scheduled_hits: list[str] = []
    manual_only_hits: list[str] = []
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        when = _parse_receipt_time(payload, path)
        if when is None or when < cutoff:
            continue
        rel = str(path.relative_to(ROOT))
        if _is_scheduled_pulse(payload, path):
            scheduled_hits.append(rel)
        elif payload.get("trigger_host") in MANUAL_TRIGGERS:
            manual_only_hits.append(rel)

    if scheduled_hits:
        return RubricCheck(
            id="pulse_scheduled",
            doctrine_ref="§8 item 1 · governed-autorun manual green ≠ cron green",
            status="PASS",
            detail=f"{len(scheduled_hits)} scheduled pulse receipt(s) in {window_h}h window",
            evidence=scheduled_hits[:8],
        )
    detail = "no scheduled pulse receipt in window"
    if manual_only_hits:
        detail += f"; manual-only ignored ({len(manual_only_hits)})"
    return RubricCheck(
        id="pulse_scheduled",
        doctrine_ref="§8 item 1 · governed-autorun manual green ≠ cron green",
        status="FAIL",
        detail=detail,
        evidence=manual_only_hits[:5],
    )


def _window_cutoff(subsystem: dict[str, Any] | None) -> datetime:
    window_h = int((subsystem or {}).get("window_hours", 168))
    return datetime.now(timezone.utc) - timedelta(hours=window_h)


def _iter_recent_receipts(
    subsystem: dict[str, Any] | None,
    *,
    extra_globs: list[str] | None = None,
) -> list[tuple[Path, dict[str, Any], datetime]]:
    cutoff = _window_cutoff(subsystem)
    globs = ["receipts/**/*.json", "receipts/*.json"]
    if extra_globs:
        globs.extend(extra_globs)
    seen: set[Path] = set()
    out: list[tuple[Path, dict[str, Any], datetime]] = []
    for pattern in globs:
        for path in _glob_receipts(pattern):
            if path in seen:
                continue
            seen.add(path)
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            when = _parse_receipt_time(payload, path)
            if when is None or when < cutoff:
                continue
            out.append((path, payload, when))
    out.sort(key=lambda row: row[2], reverse=True)
    return out


def _payload_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload).lower()


def check_membrane_or_external(subsystem: dict[str, Any] | None) -> RubricCheck:
    hits: list[str] = []
    for path, payload, _ in _iter_recent_receipts(subsystem):
        schema = str(payload.get("schema", ""))
        rtype = str(payload.get("receipt_type", ""))
        blob = _payload_text(payload)
        rel = str(path.relative_to(ROOT))

        if "external_verify" in schema.lower() or "EXTERNAL_VERIFY" in blob:
            hits.append(rel)
            continue
        if rtype == "VERIFIER_INDEPENDENCE_PROOF" and payload.get("status") == "PASS":
            hits.append(rel)
            continue
        if payload.get("secondary_account_proven") is True:
            hits.append(rel)
            continue
        if schema.startswith("metabolism_rung") or "metabolism-rung" in path.name:
            hits.append(rel)
            continue
        if "signal_factory" in schema.lower() or "signal-factory" in path.name:
            hits.append(rel)
            continue
        if "spine_live_probe" in schema.lower() or "spine-live-probe" in path.name:
            hits.append(rel)
            continue
        if payload.get("rung", 0) >= 2 or payload.get("metabolism_rung", 0) >= 2:
            hits.append(rel)

    if hits:
        return RubricCheck(
            id="membrane_or_external",
            doctrine_ref="§8 item 2 · L4 or rung≥2",
            status="PASS",
            detail=f"{len(hits)} membrane/external proof receipt(s)",
            evidence=hits[:8],
        )
    return RubricCheck(
        id="membrane_or_external",
        doctrine_ref="§8 item 2 · L4 or rung≥2",
        status="FAIL",
        detail="no L4-grade or rung≥2 membrane receipt in window",
        evidence=[],
    )


def check_mutation_or_idle(subsystem: dict[str, Any] | None) -> RubricCheck:
    hits: list[str] = []
    for path, payload, _ in _iter_recent_receipts(subsystem):
        schema = str(payload.get("schema", ""))
        blob = _payload_text(payload)
        rel = str(path.relative_to(ROOT))

        if "IDLE_NO_WORK" in blob:
            hits.append(rel)
            continue
        if payload.get("state") == "IDLE_NO_WORK" or payload.get("decision") == "IDLE_NO_WORK":
            hits.append(rel)
            continue
        if "mutation" in schema.lower() or "mutation" in path.name:
            hits.append(rel)
            continue
        if schema in {
            "living_system_w1_terminology_receipt_v1",
            "living_system_w1_next_steps_receipt_v1",
            "living_system_w1_parallel_start_receipt_v1",
            "language-layer-rc3-cold-session-proof-v1",
        }:
            hits.append(rel)
            continue
        if payload.get("plans_complete") or payload.get("terms_minted"):
            hits.append(rel)

    if hits:
        return RubricCheck(
            id="mutation_or_idle",
            doctrine_ref="§8 item 3 · L2 IDLE_NO_WORK",
            status="PASS",
            detail=f"{len(hits)} mutation or IDLE_NO_WORK receipt(s)",
            evidence=hits[:8],
        )
    return RubricCheck(
        id="mutation_or_idle",
        doctrine_ref="§8 item 3 · L2 IDLE_NO_WORK",
        status="FAIL",
        detail="no mutation or IDLE_NO_WORK receipt in window",
        evidence=[],
    )


def _is_drift_receipt(path: Path, payload: dict[str, Any]) -> bool:
    schema = str(payload.get("schema", "")).lower()
    rtype = str(payload.get("receipt_type", "")).upper()
    name = path.name.lower()
    if rtype in {"DRIFT", "DRIFT_RECEIPT", "GOVERNANCE_DRIFT"}:
        return True
    if "drift_receipt" in schema or schema.endswith("_drift_v1"):
        return True
    if name.startswith("drift-") or name.startswith("governance-drift-"):
        return True
    return False


def check_drift_fresh(subsystem: dict[str, Any] | None) -> RubricCheck:
    stale: list[str] = []
    seen = 0
    for path, payload, when in _iter_recent_receipts(subsystem):
        if not _is_drift_receipt(path, payload):
            continue
        seen += 1
        resolved = payload.get("resolved")
        status = str(payload.get("status", "")).upper()
        if resolved is True or status in {"RESOLVED", "PASS", "CLOSED"}:
            continue
        if payload.get("unresolved") is False:
            continue
        age_h = (datetime.now(timezone.utc) - when).total_seconds() / 3600
        stale.append(f"{path.relative_to(ROOT)} ({age_h:.0f}h)")

    if stale:
        return RubricCheck(
            id="drift_fresh",
            doctrine_ref="§8 item 4 · L12",
            status="FAIL",
            detail=f"{len(stale)} unresolved DRIFT receipt(s)",
            evidence=stale[:8],
        )
    detail = "zero unresolved DRIFT receipts"
    if seen:
        detail += f" ({seen} drift record(s) all resolved)"
    return RubricCheck(
        id="drift_fresh",
        doctrine_ref="§8 item 4 · L12",
        status="PASS",
        detail=detail,
        evidence=[],
    )


def check_drill_refresh(_subsystem: dict[str, Any] | None) -> RubricCheck:
    # LS-026: homeostasis drill receipt within refresh window
    return RubricCheck(
        id="drill_refresh",
        doctrine_ref="§8 item 5 · progressive trust drills",
        status="SKIP",
        detail="no homeostasis-covered classes until LS-045",
        evidence=[],
    )


RUBRIC_RUNNERS = [
    check_pulse_scheduled,
    check_membrane_or_external,
    check_mutation_or_idle,
    check_drift_fresh,
    check_drill_refresh,
]


def load_subsystem(subsystem_id: str | None) -> dict[str, Any] | None:
    if not subsystem_id or subsystem_id == "global":
        return None
    if not SUBSYSTEMS.is_file():
        return None
    data = json.loads(SUBSYSTEMS.read_text(encoding="utf-8"))
    for row in data.get("subsystems", []):
        if row.get("id") == subsystem_id:
            return row
    return None


def run_rubric(*, fast: bool, subsystem_id: str) -> RubricReport:
    report = RubricReport(
        saved_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        subsystem_id=subsystem_id or "global",
        mode="fast" if fast else "full",
    )
    report.checks.append(check_spine_files())
    sub = load_subsystem(subsystem_id)
    for runner in RUBRIC_RUNNERS:
        report.checks.append(runner(sub))

    section8 = [c for c in report.checks if c.id != "spine_files"]
    if any(c.status == "FAIL" for c in report.checks):
        report.verdict = "STALE"
    elif all(c.status in ("PASS", "SKIP") for c in section8):
        report.verdict = "LIVING"
    else:
        report.verdict = "STALE"

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Living System §8 rubric validator")
    parser.add_argument("--fast", action="store_true", help="structural + spine checks only")
    parser.add_argument("--json", action="store_true", help="emit JSON report on stdout")
    parser.add_argument("--subsystem", default="global", help="subsystem id from living_system_subsystems_v1.json")
    args = parser.parse_args()

    report = run_rubric(fast=args.fast, subsystem_id=args.subsystem)
    payload = report.to_dict()

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"living_system_chain_validate_v1: verdict={report.verdict} mode={report.mode}")
        for check in report.checks:
            print(f"  [{check.status}] {check.id}: {check.detail}")

    if any(c.status == "FAIL" for c in report.checks):
        return 1
    if args.fast:
        # Fast mode: PASS when framework + spine present; section-8 collectors may be STUB
        return 0
    if report.verdict != "LIVING":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
