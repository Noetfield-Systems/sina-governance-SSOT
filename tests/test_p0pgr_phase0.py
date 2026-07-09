"""Phase 0 tests for the P0-PGR runtime scaffold. Must stay green after any script change."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from p0pgr_cycle_v1 import run_cycle  # noqa: E402
from p0pgr_packet_lint_v1 import NINE_GATES, lint_packet  # noqa: E402
from p0pgr_phase2_rank_v1 import score_packet  # noqa: E402

P0PGR_DIR = ROOT / "p0-pgr"


def make_valid_packet(**overrides) -> dict:
    packet = {
        "schema": "p0_prompt_packet_v1.1",
        "packet_id": "PKT-9999-test-fixture",
        "created_at": "2026-01-01T00:00:00+00:00",
        "mission": "Validate one receipt against its schema deterministically",
        "problem_statement": "Test fixture packet for lint and routing checks.",
        "deliverable": {
            "type": "validation_report",
            "destination": "receipts/p0pgr/",
            "acceptance": "report lists every required field with PASS/FAIL",
        },
        "route": "CLOUD_WORKER",
        "gates": {g: True for g in NINE_GATES},
        "roi": {"revenue": 1, "trust": 4, "workload_relief": 3, "cloud_now": 5, "reversibility": 5, "rationale": "test"},
        "evidence_required": ["script_run output"],
        "confidence": "HIGH",
        "status": "OUTBOX",
    }
    packet.update(overrides)
    return packet


def test_contract_and_schema_files_exist():
    for name in (
        "P0_DISPATCH_BRAIN_RUNTIME_v1.1.md",
        "P0_DISPATCH_ROUTER_RULES_v1.md",
        "P0_PROMPT_COMPILER_MVP_PLAN_v1.md",
    ):
        text = (P0PGR_DIR / name).read_text()
        assert text.strip()
    contract = (P0PGR_DIR / "P0_DISPATCH_BRAIN_RUNTIME_v1.1.md").read_text()
    assert "nine execution gates" in contract.lower()
    assert "continuity law" in contract.lower()
    assert "PHASE_2_CLOUD_ONLY_ROI_TRACK" in contract


def test_schemas_parse_and_require_nine_gates():
    packet_schema = json.loads((P0PGR_DIR / "P0_PROMPT_PACKET_SCHEMA_v1.json").read_text())
    loop_schema = json.loads((P0PGR_DIR / "P0_PROMPT_LOOP_STATE_SCHEMA_v1.json").read_text())
    exec_schema = json.loads((P0PGR_DIR / "P0_EXECUTION_RECEIPT_SCHEMA_v1.json").read_text())
    assert packet_schema["properties"]["gates"]["required"] == NINE_GATES
    assert exec_schema["properties"]["gates_checked"]["required"] == NINE_GATES
    assert "REPAIR_CANDIDATE" in loop_schema["properties"]["verdict"]["enum"]


def test_lint_passes_valid_packet():
    assert lint_packet(make_valid_packet()) == []


def test_lint_rejects_mac_routes():
    for route in ("MAC_RUNNER", "HYBRID_MAC"):
        rejects = lint_packet(make_valid_packet(route=route))
        assert any(r.startswith("R3") for r in rejects), route


def test_lint_rejects_missing_gate_and_vague_mission():
    gates = {g: True for g in NINE_GATES}
    gates.pop("no_deploy")
    rejects = lint_packet(make_valid_packet(gates=gates))
    assert any("no_deploy" in r for r in rejects)

    vague = make_valid_packet(mission="Explore some options around receipts")
    vague["deliverable"]["acceptance"] = "tbd"
    assert any(r.startswith("R6") for r in lint_packet(vague))


def test_lint_rejects_founder_routing():
    packet = make_valid_packet(problem_statement="Founder will validate the output afterwards.")
    assert any(r.startswith("R7") for r in lint_packet(packet))


def test_rank_scoring_weights():
    top = make_valid_packet()
    top["roi"] = {"revenue": 5, "trust": 5, "workload_relief": 5, "cloud_now": 5, "reversibility": 5, "rationale": "max"}
    assert score_packet(top) == 100.0
    zero = make_valid_packet()
    zero["roi"] = {"revenue": 0, "trust": 0, "workload_relief": 0, "cloud_now": 0, "reversibility": 0, "rationale": "min"}
    assert score_packet(zero) == 0.0


def test_shadow_cycle_routes_and_never_executes(tmp_path):
    receipts_dir = tmp_path / "p0pgr"
    (receipts_dir / "founder").mkdir(parents=True)
    (receipts_dir / "founder" / "founder-authorization-test.json").write_text("{}")

    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(make_valid_packet()))
    receipt = run_cycle(packet_path, receipts_dir)
    assert receipt["verdict"] == "ROUTED"
    assert receipt["counters"] == {"executions": 0, "sends": 0, "deploys": 0, "leaks": 0, "freezes": 0}
    saved = json.loads(Path(receipt["_receipt_path"]).read_text())
    assert saved["schema"] == "p0_prompt_loop_state_v1"


def test_shadow_cycle_queues_without_founder_receipt(tmp_path):
    receipts_dir = tmp_path / "p0pgr"
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(make_valid_packet()))
    receipt = run_cycle(packet_path, receipts_dir)
    assert receipt["verdict"] == "QUEUED_FOUNDER_REVIEW"


def test_shadow_cycle_files_repair_candidate_and_continues(tmp_path):
    receipts_dir = tmp_path / "p0pgr"
    packet_path = tmp_path / "bad.json"
    packet_path.write_text(json.dumps({"schema": "wrong", "mission": ""}))
    receipt = run_cycle(packet_path, receipts_dir)
    assert receipt["verdict"] == "REPAIR_CANDIDATE"
    assert list((receipts_dir / "repair_candidates").glob("*.json"))


def test_hold_cloud_unsafe_label(tmp_path):
    receipts_dir = tmp_path / "p0pgr"
    (receipts_dir / "founder").mkdir(parents=True)
    (receipts_dir / "founder" / "founder-authorization-test.json").write_text("{}")
    gates = {g: True for g in NINE_GATES}
    gates["cloud_only"] = False
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(make_valid_packet(gates=gates)))
    receipt = run_cycle(packet_path, receipts_dir)
    assert receipt["verdict"] == "HOLD_CLOUD_UNSAFE"
