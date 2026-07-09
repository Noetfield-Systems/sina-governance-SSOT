#!/usr/bin/env python3
"""P0-PGR Evidence Reader v1 (Phase-0, shadow).

Reads P0-PGR/PDR contract files, schemas, registry, alive docs, receipts,
census state, and example packets. Emits a normalized, deterministic
evidence bundle with bundle_hash for replay (L13).

Read-only over authority files. Writes only the bundle JSON under
receipts/p0pgr/evidence/. No agent self-report is trusted: every entry
is derived from file bytes on disk, never from claims.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P0PGR_DIR = ROOT / "p0-pgr"
RECEIPTS_DIR = ROOT / "receipts"
EVIDENCE_OUT_DIR = RECEIPTS_DIR / "p0pgr" / "evidence"

REGISTRY = ROOT / "data" / "github_automation_registry_v1.json"
ALIVE_DOCS = ROOT / "data" / "agent_read_surfaces_v1.json"
STALENESS_SCRIPT = ROOT / "scripts" / "verify_agent_read_staleness_v1.sh"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001 — continuity: record, don't crash
        return {"_unreadable": str(exc)}


def collect() -> dict:
    bundle: dict = {"schema": "p0pgr-evidence-bundle-v1"}

    # 1. P0-PGR contract + schema files (bytes on disk, hashed)
    p0pgr_files = {}
    if P0PGR_DIR.is_dir():
        for f in sorted(P0PGR_DIR.iterdir()):
            if f.is_file():
                p0pgr_files[f.name] = sha256_file(f)
    bundle["p0pgr_files"] = p0pgr_files

    # 2. Registry state
    reg = load_json(REGISTRY)
    bundle["registry"] = {
        "version": reg.get("version"),
        "saved_at": reg.get("saved_at"),
        "motor_ids": sorted(m.get("motor_id", "?") for m in reg.get("motors", [])),
        "lanes": sorted({m.get("lane", "?") for m in reg.get("motors", [])}),
        "p0pgr_registered": any(
            m.get("lane") == "p0pgr" for m in reg.get("motors", [])
        ),
    }

    # 3. Alive docs / read surfaces
    alive = load_json(ALIVE_DOCS)
    bundle["alive_docs"] = {
        "keys": sorted(alive.keys()) if isinstance(alive, dict) else [],
        "sha256": sha256_file(ALIVE_DOCS) if ALIVE_DOCS.exists() else None,
    }

    # 4. Receipts surface: newest 25 by name (names embed timestamps),
    #    mtimes recorded for staleness signal.
    receipts = []
    if RECEIPTS_DIR.is_dir():
        entries = sorted(
            (p for p in RECEIPTS_DIR.iterdir() if p.is_file()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:25]
        for p in entries:
            receipts.append(
                {"name": p.name, "mtime_utc": datetime.fromtimestamp(
                    p.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds")}
            )
    bundle["latest_receipts"] = receipts

    # 5. Latest workflow census (evidence, not self-report)
    census_files = sorted(RECEIPTS_DIR.glob("workflow-census-*.json"))
    if census_files:
        census = load_json(census_files[-1])
        bundle["census"] = {
            "file": census_files[-1].name,
            "audit_status": census.get("audit_status"),
            "loop_count": census.get("loop_count"),
            "counts": census.get("counts"),
            "flag_count": len(census.get("audit_flags", [])),
        }
    else:
        bundle["census"] = {"file": None, "note": "STALE_DATA: no census receipt"}

    # 6. Staleness gate availability (recorded, not executed — Mac 90s law)
    bundle["staleness_gate"] = {
        "script_present": STALENESS_SCRIPT.exists(),
        "latest_receipts": sorted(
            p.name for p in RECEIPTS_DIR.glob("agent-read-staleness-*")
        )[-3:],
    }

    # 7. Open packets / repair candidates
    outbox = RECEIPTS_DIR / "p0pgr" / "outbox"
    repairs = RECEIPTS_DIR / "p0pgr" / "repair_candidates"
    bundle["p0pgr_queue"] = {
        "outbox": sorted(p.name for p in outbox.glob("*.json")) if outbox.is_dir() else [],
        "repair_candidates": sorted(p.name for p in repairs.glob("*.json")) if repairs.is_dir() else [],
    }

    # Deterministic replay hash over everything above (L13), then stamp time.
    bundle["bundle_hash"] = canonical_hash(bundle)
    bundle["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return bundle


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=None,
                    help="output path (default receipts/p0pgr/evidence/<hash>.json)")
    ap.add_argument("--stdout", action="store_true", help="print full bundle")
    args = ap.parse_args()

    bundle = collect()
    out = args.out or EVIDENCE_OUT_DIR / f"evidence-{bundle['bundle_hash'][:16]}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n")

    if args.stdout:
        print(json.dumps(bundle, indent=2, sort_keys=True))
    else:
        print(json.dumps({
            "bundle_hash": bundle["bundle_hash"],
            "out": str(out.relative_to(ROOT)),
            "p0pgr_registered": bundle["registry"]["p0pgr_registered"],
            "census_status": bundle["census"].get("audit_status"),
        }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
