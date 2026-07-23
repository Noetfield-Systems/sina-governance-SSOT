"""Path disjointness — fail before any write on prohibited overlaps."""
from __future__ import annotations

from pathlib import Path

from .errors import GovernanceBlock


def _resolve(p: Path | None) -> Path | None:
    if p is None:
        return None
    return Path(p).resolve()


def assert_paths_disjoint(
    *,
    store_dir: Path | None = None,
    out_dir: Path | None = None,
    event_ledger_path: Path | None = None,
    staging_path: Path | None = None,
    backup_path: Path | None = None,
) -> None:
    """
    Fail when store/out/ledger/staging/backup share equality or parent/child overlap.
    Dry-run diagnostics and event ledgers must not live under store_dir.
    """
    store = _resolve(store_dir)
    out = _resolve(out_dir)
    ledger = _resolve(event_ledger_path)
    staging = _resolve(staging_path)
    backup = _resolve(backup_path)

    pairs = [
        ("store_dir", store),
        ("out_dir", out),
        ("event_ledger_path", ledger),
        ("staging_path", staging),
        ("backup_path", backup),
    ]
    named = [(n, p) for n, p in pairs if p is not None]

    def _overlap(a: Path, b: Path) -> bool:
        if a == b:
            return True
        try:
            a.relative_to(b)
            return True
        except ValueError:
            pass
        try:
            b.relative_to(a)
            return True
        except ValueError:
            pass
        return False

    for i, (na, a) in enumerate(named):
        for nb, b in named[i + 1 :]:
            # Ledger may sit under out_dir (allowed). Staging/backup under out_dir allowed.
            allowed = {
                frozenset({"out_dir", "event_ledger_path"}),
                frozenset({"out_dir", "staging_path"}),
                frozenset({"out_dir", "backup_path"}),
                frozenset({"staging_path", "backup_path"}),
            }
            if frozenset({na, nb}) in allowed:
                continue
            if _overlap(a, b):
                raise GovernanceBlock(
                    f"path overlap forbidden before write: {na}={a} overlaps {nb}={b}"
                )

    # Explicit: ledger/out must never be inside store
    if store is not None:
        for label, p in (("out_dir", out), ("event_ledger_path", ledger), ("staging_path", staging), ("backup_path", backup)):
            if p is None:
                continue
            if p == store or _overlap(p, store):
                # out inside store or store inside out both forbidden except we already checked
                if label == "out_dir" or label == "event_ledger_path":
                    raise GovernanceBlock(
                        f"{label} must be path-disjoint from store_dir (got {p} vs {store})"
                    )
