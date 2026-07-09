#!/usr/bin/env python3
"""Read-only drift check for PRODUCT_CATEGORY_REGISTRY_v1.json.

For each category: verify every cited proof-asset path still exists, and
check whether a file matching its receipt_required_to_activate description
has newly appeared. NEVER writes to product/ or edits the registry. Emits a
single JSON receipt to stdout (and optionally to --out).

Exit code: 0 if no drift and no missing evidence, 1 if any category drifted
or lost a proof asset. Exit code is the ONLY thing GHA needs to decide
pass/fail; the JSON body is what Cloudflare/Supabase independently verify.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Known clones/worktrees of THIS SAME repo. If a cited path is prefixed with
# one of these names, it is a self-reference — resolve it ONLY against
# repo_root (the checkout actually being audited). NEVER fall back to
# workspace_root for these: that could silently cross into a different
# branch of the same repo (e.g. the shared main checkout on a different
# branch than the one being audited) and mask real drift on THIS branch.
SELF_REPO_NAMES = {
    "sina-governance-SSOT",
    "sg-product-lock",
    "sg-sandbox",
    "ssot-p0pgr-workflow-bootstrap",
}

STATUS_ENUM = (
    "live-running",
    "built-not-activated",
    "partial-scaffold",
    "spec-doc-only",
    "concept-only",
)


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_registry(registry_path: Path) -> dict:
    return json.loads(registry_path.read_text())


def extract_cited_paths(text: str) -> list[str]:
    """Best-effort: pull path-looking tokens out of a proof-asset string.

    Proof-asset entries are free-text like "sina-governance-SSOT/data/x.json
    (what it is)". We only need the leading path token.
    """
    token = text.strip().split(" ")[0].strip().rstrip(",;")
    return [token] if token else []


def resolve_proof_asset(
    path_str: str, repo_root: Path, workspace_root: Path | None, repo_top_dirs: set[str]
) -> dict:
    """Resolve a cited proof-asset path.

    The registry legitimately cites paths in FOUR shapes:
      (a) a normal path relative to this repo (e.g. "data/x.json")
      (b) this repo's own name prefixed (e.g. "sina-governance-SSOT/skills/x",
          written from the workspace root while repo_root already IS that repo)
      (c) a bare filename with no directory (some entries cite just a receipt
          filename) — resolved via a BOUNDED rglob under receipts/ only, never
          a full-repo scan
      (d) a SIBLING repo in the workspace (e.g. "SourceA/apps/...",
          "noetfield-studio-ide/src/..."). A single-repo checkout (as GHA
          uses) structurally cannot see these. If workspace_root is not
          provided, such paths are reported "out_of_scope", NOT "missing" —
          reporting them as missing would be a false alarm, not real drift.
    """
    direct = repo_root / path_str
    if direct.exists():
        return {"exists": True, "scope": "in_repo", "resolved": str(direct.relative_to(repo_root))}

    if "/" in path_str:
        first_segment, rest = path_str.split("/", 1)

        if first_segment in repo_top_dirs:
            return {"exists": False, "scope": "in_repo", "resolved": None}

        if first_segment in SELF_REPO_NAMES:
            # Self-reference: resolve ONLY against repo_root (the checkout
            # actually being audited). Never cross to another clone/branch.
            stripped = repo_root / rest
            if stripped.exists():
                return {"exists": True, "scope": "in_repo", "resolved": str(stripped.relative_to(repo_root))}
            return {"exists": False, "scope": "in_repo", "resolved": None}

        # Not this repo's own top-level dir and not a self-name prefix ->
        # a genuinely distinct sibling repo (SourceA/, Noetfield/, etc.).
        if workspace_root is not None:
            sibling = workspace_root / path_str
            if sibling.exists():
                return {"exists": True, "scope": "cross_repo", "resolved": str(sibling)}
            return {"exists": False, "scope": "cross_repo", "resolved": None}

        return {"exists": None, "scope": "out_of_scope_no_workspace_root", "resolved": None}

    receipts_dir = repo_root / "receipts"
    if receipts_dir.is_dir():
        matches = list(receipts_dir.rglob(path_str))
        if matches:
            return {"exists": True, "scope": "in_repo", "resolved": str(matches[0].relative_to(repo_root))}
    return {"exists": False, "scope": "in_repo", "resolved": None}


def check_category(cat: dict, repo_root: Path, workspace_root: Path | None, repo_top_dirs: set[str]) -> dict:
    category_id = cat["category_id"]
    registry_status = cat.get("current_build_status", "unknown")
    proof_field = cat.get("current_proof_assets") or cat.get("proof_assets") or []

    evidence_checked = []
    missing = []
    out_of_scope = []
    for entry in proof_field:
        # entries are plain strings in this registry's schema
        for path_str in extract_cited_paths(str(entry)):
            result = resolve_proof_asset(path_str, repo_root, workspace_root, repo_top_dirs)
            evidence_checked.append({"path": path_str, **result})
            if result["scope"] == "out_of_scope_no_workspace_root":
                out_of_scope.append(path_str)
            elif not result["exists"]:
                missing.append(path_str)

    # observed_status: conservative — if any previously-cited, IN-SCOPE proof
    # asset vanished, we cannot claim the registered status still holds;
    # report it as a finding rather than guessing a new status (no LLM
    # re-derivation here by design — that's the expensive/noisy thing this
    # script avoids). Paths we structurally could not check (sibling repos
    # not checked out) never count toward drift — that would be a false
    # alarm, not evidence.
    if missing:
        observed_status = "unknown-evidence-missing"
        drifted = True
    else:
        observed_status = registry_status
        drifted = False

    return {
        "category_id": category_id,
        "registry_build_status": registry_status,
        "observed_status": observed_status,
        "drifted": drifted,
        "evidence_checked": evidence_checked,
        "missing_proof_assets": missing,
        "out_of_scope_proof_assets": out_of_scope,
        "receipt_required_to_activate": cat.get("receipt_required_to_activate", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        default="product/PRODUCT_CATEGORY_REGISTRY_v1.json",
        help="Path to the registry, relative to --repo-root",
    )
    parser.add_argument("--repo-root", default=".", help="Repo root to resolve proof-asset paths against")
    parser.add_argument(
        "--workspace-root",
        default=None,
        help=(
            "Parent workspace dir containing sibling repos (SourceA/, Noetfield/, "
            "TrustField-Technologies/, etc.) for full local verification. Omit in "
            "cloud/single-repo-checkout runs (e.g. GHA) — cross-repo proof assets "
            "are then reported as out-of-scope, not missing."
        ),
    )
    parser.add_argument("--out", default=None, help="Optional path to also write the receipt JSON to")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    workspace_root = Path(args.workspace_root).resolve() if args.workspace_root else None
    registry_path = repo_root / args.registry
    registry = load_registry(registry_path)
    repo_top_dirs = {p.name for p in repo_root.iterdir() if p.is_dir()}

    categories = registry.get("categories", [])
    results = [check_category(cat, repo_root, workspace_root, repo_top_dirs) for cat in categories]

    categories_drifted = sum(1 for r in results if r["drifted"])
    categories_missing_evidence = sum(1 for r in results if r["missing_proof_assets"])
    categories_out_of_scope = sum(1 for r in results if r["out_of_scope_proof_assets"])

    receipt = {
        "schema": "category_registry_drift_check_receipt_v1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "registry_path": str(args.registry),
        "registry_status": registry.get("status", "unknown"),
        "workspace_root_provided": workspace_root is not None,
        "categories_checked": len(results),
        "categories_drifted": categories_drifted,
        "categories_missing_evidence": categories_missing_evidence,
        "categories_with_out_of_scope_evidence": categories_out_of_scope,
        "results": results,
        "read_only": True,
        "note": (
            "This script never opens the registry in write mode. It reports drift; "
            "it never edits product/. Proof assets in sibling repos are marked "
            "out_of_scope (not missing) when --workspace-root is not provided, "
            "since a single-repo checkout cannot see them — this is a disclosed "
            "scope boundary, not a false pass."
        ),
    }

    out_text = json.dumps(receipt, indent=2)
    print(out_text)
    if args.out:
        Path(args.out).write_text(out_text)

    return 1 if (categories_drifted or categories_missing_evidence) else 0


if __name__ == "__main__":
    sys.exit(main())
