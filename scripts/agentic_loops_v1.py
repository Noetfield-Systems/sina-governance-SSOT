#!/usr/bin/env python3
"""Agentic loops prototype v1: orchestrator, validator, adversary, self-repair, audit, and receipt emitter.

Design constraints: self-contained, no external dependencies, repo-local, safe (no external side-effects), emits receipts under receipts/agentic/.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIR = ROOT / "receipts" / "agentic"
RECEIPT_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_FIELDS = [
    "signal_id",
    "timestamp",
    "source",
    "classification",
    "decision",
    "risk_score",
    "action",
    "status",
]


class SimpleWorker:
    """Simulated worker that processes tasks and returns structured outputs.

    It is deterministic for the demo and supports a "repair" mode to return a corrected payload.
    """

    def __init__(self, name: str = "simple-worker"):
        self.name = name

    def process(self, task_name: str, payload: Dict[str, Any], repair: bool = False) -> Dict[str, Any]:
        # Minimal logic: produce a receipt-like dict; if repair=True, include optional_sections when appropriate
        base = {
            "signal_id": payload.get("signal_id", f"{task_name}-{int(time.time())}"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": payload.get("source", "unknown"),
            "classification": payload.get("classification", "unclear"),
            "decision": payload.get("decision", "ignore"),
            "scores": payload.get("scores", {"trust": 2, "risk": 2, "automation_value": 0, "commercial_value": 0}),
            "risk_score": payload.get("risk_score", 2),
            "action": payload.get("action", payload.get("decision", "ignore")),
            "status": "generated",
            "optional_sections": payload.get("optional_sections", {}),
        }
        # Intentional bug simulation: when not repair and classification == 'client', drop required field 'source'
        if not repair and base["classification"] == "client":
            base.pop("source", None)
        # If repair=True, ensure optional_sections only present when decision allows it
        if repair:
            if base["decision"] not in {"build_automation", "create_service_pattern"}:
                base["optional_sections"] = {}
        return base


class Validator:
    """Basic validator that checks required fields and simple value bounds."""

    @staticmethod
    def validate(payload: Dict[str, Any]) -> Tuple[bool, list[str]]:
        errors = []
        for k in REQUIRED_FIELDS:
            if k not in payload:
                errors.append(f"missing required field: {k}")
        # risk_score bounds
        if "risk_score" in payload:
            try:
                v = float(payload["risk_score"])
                if v < 0 or v > 5:
                    errors.append("risk_score out of 0..5 range")
            except Exception:
                errors.append("risk_score not numeric")
        return (len(errors) == 0, errors)


class Adversary:
    """Simple adversary that mutates a payload to create failure modes."""

    @staticmethod
    def corrupt(payload: Dict[str, Any]) -> Dict[str, Any]:
        p = dict(payload)
        if "source" in p:
            p["source"] = ""  # empty source
        if "risk_score" in p:
            p["risk_score"] = 999  # unrealistic
        # remove a required field randomly (deterministic here)
        p.pop("classification", None)
        return p


class RepairStrategy:
    """Base class for repair strategies. Subclasses implement `repair` that returns a candidate payload or None."""

    def repair(self, worker: SimpleWorker, task_name: str, original_payload: Dict[str, Any]) -> Tuple[Dict[str, Any] | None, str]:
        raise NotImplementedError


class RerunStrategy(RepairStrategy):
    """Re-run the worker in repair mode and return candidate."""

    def repair(self, worker: SimpleWorker, task_name: str, original_payload: Dict[str, Any]) -> Tuple[Dict[str, Any] | None, str]:
        candidate = worker.process(task_name, original_payload, repair=True)
        return candidate, "rerun"


class AutoFillStrategy(RepairStrategy):
    """Conservative auto-fill of missing fields and normalization of bounds."""

    def repair(self, worker: SimpleWorker, task_name: str, original_payload: Dict[str, Any]) -> Tuple[Dict[str, Any] | None, str]:
        # Start from a fresh re-run candidate, then fill
        candidate = worker.process(task_name, original_payload, repair=True)
        for k in REQUIRED_FIELDS:
            if k not in candidate:
                candidate[k] = "AUTO_FILLED"
        # normalize risk_score
        try:
            rs = float(candidate.get("risk_score", 2))
            if rs < 0 or rs > 5:
                candidate["risk_score"] = 3
        except Exception:
            candidate["risk_score"] = 3
        return candidate, "autofill"


class SelfRepair:
    """Attempts a sequence of pluggable repair strategies in order.

    Returns repaired_payload or None.
    """

    STRATEGIES = [RerunStrategy(), AutoFillStrategy()]

    @staticmethod
    def attempt_repair(worker: SimpleWorker, task_name: str, original_payload: Dict[str, Any]) -> Dict[str, Any] | None:
        for strat in SelfRepair.STRATEGIES:
            candidate, name = strat.repair(worker, task_name, original_payload)
            if candidate is None:
                continue
            ok, errs = Validator.validate(candidate)
            if ok:
                candidate["status"] = f"repaired_by_{name}"
                candidate.setdefault("repair_strategy", name)
                return candidate
        return None


class Auditor:
    """Writes audit reports for externally consumable review.

    For prototype, writes a JSON audit file alongside the receipt.
    """

    @staticmethod
    def emit_audit(receipt: Dict[str, Any], note: str = "") -> Path:
        audit = {"receipt_signal_id": receipt.get("signal_id"), "timestamp": datetime.utcnow().isoformat() + "Z", "note": note, "receipt_summary": {k: receipt.get(k) for k in ["decision", "status", "risk_score"]}}
        path = RECEIPT_DIR / f"audit-{receipt.get('signal_id')}-{int(time.time())}.json"
        with open(path, "w") as fh:
            json.dump(audit, fh, indent=2)
        return path


def emit_receipt(payload: Dict[str, Any]) -> Path:
    filename = f"receipt-{payload.get('signal_id', 'x')}-{int(time.time())}.json"
    path = RECEIPT_DIR / filename
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2)
    return path


class Orchestrator:
    def __init__(self, worker: SimpleWorker):
        self.worker = worker

    def run_task(self, task_name: str, payload: Dict[str, Any], adversarial: bool = False) -> Dict[str, Any]:
        print(f"[orchestrator] running task {task_name} (adversarial={adversarial})")
        out = self.worker.process(task_name, payload)
        if adversarial:
            out = Adversary.corrupt(out)
            print("[adversary] corrupted output")
        ok, errors = Validator.validate(out)
        if ok:
            out["status"] = "validated"
            path = emit_receipt(out)
            print(f"[orchestrator] valid — receipt emitted: {path}")
            Auditor.emit_audit(out, note="initial success")
            return out
        print(f"[validator] errors: {errors}")
        # attempt self-repair
        repaired = SelfRepair.attempt_repair(self.worker, task_name, payload)
        if repaired:
            path = emit_receipt(repaired)
            print(f"[orchestrator] repaired — receipt emitted: {path}")
            Auditor.emit_audit(repaired, note="repaired")
            return repaired
        # final fallback: emit failed receipt with errors for outside audit
        failed = {"signal_id": payload.get("signal_id", f"failed-{int(time.time())}"), "timestamp": datetime.utcnow().isoformat() + "Z", "status": "validation_failed", "errors": errors}
        path = emit_receipt(failed)
        print(f"[orchestrator] failed — emitted failed receipt: {path}")
        Auditor.emit_audit(failed, note="validation_failed — needs human review")
        return failed


def demo_run():
    worker = SimpleWorker()
    orch = Orchestrator(worker)
    # Task A: benign signal
    payload_a = {"signal_id": "demo-1", "source": "email:test@example.com", "classification": "vendor", "decision": "reply", "risk_score": 1}
    orch.run_task("classify_signal", payload_a, adversarial=False)
    # Task B: client that triggers corruption bug and requires repair
    payload_b = {"signal_id": "demo-2", "source": "webform:contact", "classification": "client", "decision": "create_service_pattern", "risk_score": 2}
    orch.run_task("classify_signal", payload_b, adversarial=True)


if __name__ == "__main__":
    demo_run()
