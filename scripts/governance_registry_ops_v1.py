#!/usr/bin/env python3
"""Strict registry + structure tree operations for daily add/remove/amend."""
from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/governance_artifact_registry_v1.json"
STRUCTURE_TREE = ROOT / "data/governance_structure_tree_v1.json"
THREAD_REGISTRY = ROOT / "data/governance_thread_registry_v1.json"
STAGING = ROOT / "data/governance_intake_staging_v1"
RECEIPTS = ROOT / "receipts"

REQUIRED_ARTIFACT_FIELDS = (
    "artifact_id",
    "path",
    "layer",
    "domain",
    "version",
    "status",
    "authority_rank",
    "owner_repo",
    "saved_at",
    "affects_layers",
    "depends_on",
    "amends",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_receipt(command: str, payload: dict) -> Path:
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    rid = f"governance-registry-ops-{utc_stamp()}"
    body = {
        "schema": "governance-registry-ops-receipt-v1",
        "receipt_id": rid,
        "recorded_at": utc_now(),
        "command": command,
        "ok": payload.get("ok", True),
        "result": payload,
    }
    out = RECEIPTS / f"{rid}.json"
    out.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return out


def load_registry() -> dict:
    return load_json(REGISTRY)


def save_registry(registry: dict, command: str) -> Path:
    registry["saved_at"] = utc_now()
    save_json(REGISTRY, registry)
    return write_receipt(command, {"ok": True, "artifact_count": len(registry.get("artifacts", []))})


def load_structure_tree() -> dict:
    return load_json(STRUCTURE_TREE)


def load_thread_registry() -> dict:
    if not THREAD_REGISTRY.is_file():
        payload = {
            "schema": "governance_thread_registry_v1",
            "version": "1.0.0",
            "saved_at": utc_now(),
            "owner": "SG (sina-governance-ssot)",
            "purpose": "Daily thread registry",
            "threads": [],
        }
        save_json(THREAD_REGISTRY, payload)
        return payload
    return load_json(THREAD_REGISTRY)


def save_thread_registry(payload: dict, command: str) -> Path:
    payload["saved_at"] = utc_now()
    save_json(THREAD_REGISTRY, payload)
    return write_receipt(command, {"ok": True, "thread_count": len(payload.get("threads", []))})


def registry_index(registry: dict) -> dict[str, dict]:
    return {a["artifact_id"]: a for a in registry.get("artifacts", []) if a.get("artifact_id")}


def validate_artifact_spec(spec: dict, registry: dict, tree: dict) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_ARTIFACT_FIELDS:
        if field not in spec:
            errors.append(f"missing required field: {field}")

    aid = spec.get("artifact_id", "")
    if not aid or not re.match(r"^[a-z0-9][a-z0-9-]*$", aid):
        errors.append("artifact_id must be lowercase slug")

    if aid in registry_index(registry):
        errors.append(f"duplicate artifact_id: {aid}")

    layers = set(registry.get("layer_model", tree.get("layers", {})))
    domains = set(registry.get("domains", tree.get("domains", [])))
    statuses = set(registry.get("status_model", {}))

    if spec.get("layer") not in layers:
        errors.append(f"invalid layer: {spec.get('layer')}")
    if spec.get("domain") not in domains and spec.get("domain") != "intake_thread":
        errors.append(f"invalid domain: {spec.get('domain')}")
    if spec.get("status") not in statuses:
        errors.append(f"invalid status: {spec.get('status')}")

    rel = spec.get("path", "")
    if registry.get("owner_repo") and spec.get("authority_rank", 99) <= 3:
        if spec.get("owner_repo") != "sina-governance-ssot":
            errors.append("authority_rank <= 3 must be owner_repo sina-governance-ssot")

    for dep in spec.get("depends_on", []) + spec.get("amends", []):
        if dep not in registry_index(registry):
            errors.append(f"unknown lineage target: {dep}")

    full = ROOT / rel if rel and not str(rel).startswith("P") else None
    if full and not full.is_file():
        errors.append(f"path not found on disk: {rel}")

    paths = {a.get("path") for a in registry.get("artifacts", [])}
    if rel in paths:
        errors.append(f"duplicate path: {rel}")

    return errors


def validate_structure_strict(registry: dict, tree: dict) -> list[str]:
    errors: list[str] = []
    layers = set(tree.get("layers", {}))
    domains = set(tree.get("domains", []))
    statuses = set(registry.get("status_model", {}))
    index = registry_index(registry)

    for art in registry.get("artifacts", []):
        aid = art.get("artifact_id", "")
        if art.get("layer") not in layers:
            errors.append(f"{aid}: layer {art.get('layer')} not in structure tree")
        if art.get("domain") not in domains:
            errors.append(f"{aid}: domain {art.get('domain')} not in structure tree")
        if art.get("status") not in statuses:
            errors.append(f"{aid}: invalid status")
        for dep in art.get("depends_on", []) + art.get("amends", []):
            if dep not in index:
                errors.append(f"{aid}: missing lineage target {dep}")
        if art.get("status") == "ACTIVE_BASE":
            amended_by = [a for a in registry.get("artifacts", []) if aid in a.get("amends", [])]
            if not amended_by and art.get("domain") == "governance_structure":
                pass

    machine_scripts = {m.get("script") for m in tree.get("machines", [])}
    for script in machine_scripts:
        if script and not (ROOT / script).is_file():
            errors.append(f"structure tree machine missing script: {script}")

    if tree.get("registry_doc") != "data/governance_artifact_registry_v1.json":
        errors.append("structure tree registry_doc mismatch")

    return errors


def build_structure_tree_view(registry: dict, tree: dict, thread_reg: dict) -> dict:
    by_layer: dict[str, list] = {k: [] for k in tree.get("layers", {})}
    for art in registry.get("artifacts", []):
        layer = art.get("layer", "P0")
        by_layer.setdefault(layer, []).append(
            {
                "artifact_id": art.get("artifact_id"),
                "path": art.get("path"),
                "status": art.get("status"),
                "domain": art.get("domain"),
                "version": art.get("version"),
            }
        )

    return {
        "schema": "governance-structure-tree-view-v1",
        "generated_at": utc_now(),
        "authority_order": tree.get("authority_order", []),
        "layers": tree.get("layers", {}),
        "domains": tree.get("domains", []),
        "machines": tree.get("machines", []),
        "daily_ops": tree.get("daily_ops", {}),
        "artifacts_by_layer": by_layer,
        "artifact_count": len(registry.get("artifacts", [])),
        "thread_count": len(thread_reg.get("threads", [])),
        "threads": thread_reg.get("threads", []),
    }


def op_registry_list(registry: dict, layer: str | None, domain: str | None, status: str | None) -> dict:
    rows = []
    for art in registry.get("artifacts", []):
        if layer and art.get("layer") != layer:
            continue
        if domain and art.get("domain") != domain:
            continue
        if status and art.get("status") != status:
            continue
        rows.append(
            {
                "artifact_id": art.get("artifact_id"),
                "path": art.get("path"),
                "layer": art.get("layer"),
                "domain": art.get("domain"),
                "status": art.get("status"),
                "version": art.get("version"),
            }
        )
    return {"schema": "governance-registry-list-v1", "count": len(rows), "artifacts": rows, "ok": True}


def op_registry_show(registry: dict, artifact_id: str) -> dict:
    art = registry_index(registry).get(artifact_id)
    if not art:
        return {"ok": False, "error": f"artifact not found: {artifact_id}"}
    amended_by = [
        a["artifact_id"]
        for a in registry.get("artifacts", [])
        if artifact_id in a.get("amends", [])
    ]
    return {"ok": True, "artifact": art, "amended_by": amended_by}


def op_registry_add(registry: dict, tree: dict, spec: dict, apply: bool) -> dict:
    errors = validate_artifact_spec(spec, registry, tree)
    if errors:
        return {"ok": False, "errors": errors}
    new_registry = deepcopy(registry)
    new_registry.setdefault("artifacts", []).append(spec)
    structure_errors = validate_structure_strict(new_registry, tree)
    if structure_errors:
        return {"ok": False, "errors": structure_errors}
    receipt = None
    if apply:
        save_json(REGISTRY, {**new_registry, "saved_at": utc_now()})
        receipt = str(write_receipt("registry-add", {"artifact_id": spec["artifact_id"], "ok": True}))
    return {"ok": True, "dry_run": not apply, "artifact": spec, "receipt_path": receipt}


def op_registry_amend(registry: dict, artifact_id: str, amends: str, status: str | None, apply: bool) -> dict:
    index = registry_index(registry)
    art = index.get(artifact_id)
    target = index.get(amends)
    if not art:
        return {"ok": False, "error": f"artifact not found: {artifact_id}"}
    if not target:
        return {"ok": False, "error": f"amends target not found: {amends}"}
    new_registry = deepcopy(registry)
    for row in new_registry["artifacts"]:
        if row["artifact_id"] == artifact_id:
            row.setdefault("amends", [])
            if amends not in row["amends"]:
                row["amends"].append(amends)
            row["status"] = status or "ACTIVE_AMENDMENT"
            row["saved_at"] = utc_now()
    receipt = None
    if apply:
        save_json(REGISTRY, {**new_registry, "saved_at": utc_now()})
        receipt = str(write_receipt("registry-amend", {"artifact_id": artifact_id, "amends": amends, "ok": True}))
    return {"ok": True, "dry_run": not apply, "artifact_id": artifact_id, "amends": amends, "receipt_path": receipt}


def op_registry_retire(registry: dict, artifact_id: str, reason: str, apply: bool) -> dict:
    index = registry_index(registry)
    art = index.get(artifact_id)
    if not art:
        return {"ok": False, "error": f"artifact not found: {artifact_id}"}
    if art.get("authority_rank", 99) <= 1 and art.get("status") == "ACTIVE":
        dependents = [
            a["artifact_id"]
            for a in registry.get("artifacts", [])
            if artifact_id in a.get("depends_on", []) and a.get("status") != "SUPERSEDED"
        ]
        if dependents:
            return {"ok": False, "error": f"cannot retire — dependents still live: {dependents}"}
    new_registry = deepcopy(registry)
    for row in new_registry["artifacts"]:
        if row["artifact_id"] == artifact_id:
            row["status"] = "SUPERSEDED"
            row["retired_at"] = utc_now()
            row["retire_reason"] = reason
    receipt = None
    if apply:
        save_json(REGISTRY, {**new_registry, "saved_at": utc_now()})
        receipt = str(write_receipt("registry-retire", {"artifact_id": artifact_id, "reason": reason, "ok": True}))
    return {"ok": True, "dry_run": not apply, "artifact_id": artifact_id, "status": "SUPERSEDED", "receipt_path": receipt}


def op_registry_remove(registry: dict, artifact_id: str, apply: bool) -> dict:
    art = registry_index(registry).get(artifact_id)
    if not art:
        return {"ok": False, "error": f"artifact not found: {artifact_id}"}
    if art.get("status") != "SUPERSEDED":
        return {"ok": False, "error": "strict rule: only SUPERSEDED artifacts may be removed — retire first"}
    if art.get("authority_rank", 99) <= 2:
        return {"ok": False, "error": "strict rule: rank <= 2 artifacts are never deleted — keep row as SUPERSEDED"}
    dependents = [
        a["artifact_id"]
        for a in registry.get("artifacts", [])
        if artifact_id in a.get("depends_on", []) + a.get("amends", [])
    ]
    if dependents:
        return {"ok": False, "error": f"cannot remove — referenced by: {dependents}"}
    new_registry = deepcopy(registry)
    new_registry["artifacts"] = [a for a in new_registry["artifacts"] if a["artifact_id"] != artifact_id]
    receipt = None
    if apply:
        save_json(REGISTRY, {**new_registry, "saved_at": utc_now()})
        receipt = str(write_receipt("registry-remove", {"artifact_id": artifact_id, "ok": True}))
    return {"ok": True, "dry_run": not apply, "removed": artifact_id, "receipt_path": receipt}


def op_thread_list(thread_reg: dict) -> dict:
    return {
        "schema": "governance-thread-registry-list-v1",
        "count": len(thread_reg.get("threads", [])),
        "threads": thread_reg.get("threads", []),
        "ok": True,
    }


def op_thread_register(thread_reg: dict, thread_id: str, from_staging: bool, spec: dict | None, apply: bool) -> dict:
    existing = {t["thread_id"] for t in thread_reg.get("threads", [])}
    if thread_id in existing:
        return {"ok": False, "error": f"thread already registered: {thread_id}"}

    row: dict[str, Any] = {
        "thread_id": thread_id,
        "status": "REGISTERED",
        "registered_at": utc_now(),
        "source": "manual",
    }
    if from_staging:
        staging_dir = STAGING / thread_id
        if not staging_dir.is_dir():
            return {"ok": False, "error": f"no staging folder: {staging_dir}"}
        files = [str(p) for p in staging_dir.glob("*") if p.is_file() and p.name != "manifest.json"]
        row["source"] = "intake_staging"
        row["staging_paths"] = files
        row["staging_dir"] = str(staging_dir)
    if spec:
        row.update(spec)

    new_reg = deepcopy(thread_reg)
    new_reg.setdefault("threads", []).append(row)
    receipt = None
    if apply:
        save_thread_registry(new_reg, "thread-register")
        receipt = str(RECEIPTS / f"governance-registry-ops-{utc_stamp()}.json")
    return {"ok": True, "dry_run": not apply, "thread": row, "receipt_path": receipt}


def op_thread_retire(thread_reg: dict, thread_id: str, reason: str, apply: bool) -> dict:
    found = False
    new_reg = deepcopy(thread_reg)
    for row in new_reg.get("threads", []):
        if row.get("thread_id") == thread_id:
            row["status"] = "RETIRED"
            row["retired_at"] = utc_now()
            row["retire_reason"] = reason
            found = True
    if not found:
        return {"ok": False, "error": f"thread not found: {thread_id}"}
    receipt = None
    if apply:
        receipt = str(save_thread_registry(new_reg, "thread-retire"))
    return {"ok": True, "dry_run": not apply, "thread_id": thread_id, "status": "RETIRED", "receipt_path": receipt}
