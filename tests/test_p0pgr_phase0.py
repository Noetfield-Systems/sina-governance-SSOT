"""Phase-0 tests for P0-PGR/PDR scripts (advisor-required list, v1.1)."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from p0pgr_packet_lint_v1 import lint_packet  # noqa: E402
from p0pgr_cycle_v1 import run_cycle  # noqa: E402

EXAMPLE = ROOT / "p0-pgr" / "EXAMPLE_PACKET_P0PGR-20260708-001.json"


def load_example():
    return json.loads(EXAMPLE.read_text())


# T1 — valid v1.1 packet passes
def test_valid_packet_passes():
    r = lint_packet(load_example())
    assert r["verdict"] == "PASS", r["reasons"]
    assert r["runtime_action"] == "continue"


# T2 — missing execution_mode -> REPAIR_CANDIDATE
def test_missing_execution_mode_repair_candidate():
    p = load_example()
    del p["execution_mode"]
    r = lint_packet(p)
    assert r["verdict"] == "REPAIR_CANDIDATE"
    assert any("execution_mode" in x for x in r["reasons"])
    assert r["runtime_action"] == "continue"  # never lane STOP


# T3 — HYBRID_MAC without canonical_path -> REPAIR_CANDIDATE
def test_hybrid_mac_without_canonical_path():
    p = load_example()
    p["execution_mode"] = "HYBRID_MAC"
    r = lint_packet(p)
    assert r["verdict"] == "REPAIR_CANDIDATE"
    assert any("canonical_path" in x for x in r["reasons"])


# T4 — invalid HARD_BLOCK reason -> REPAIR_CANDIDATE
def test_invalid_hard_block_reason():
    p = load_example()
    p["quality_handling"]["hard_block_allowed_reasons"] = ["low_quality_output"]
    r = lint_packet(p)
    assert r["verdict"] == "REPAIR_CANDIDATE"
    assert any("hard_block" in x for x in r["reasons"])


# T5 — cloud_safe=false with CLOUD_ONLY -> REPAIR_CANDIDATE
def test_cloud_unsafe_cloud_only():
    p = load_example()
    p["cloud_safe"] = False
    r = lint_packet(p)
    assert r["verdict"] == "REPAIR_CANDIDATE"
    assert any("cloud_safe" in x.lower() for x in r["reasons"])


# T6 — deploy without FOUNDER_ONLY -> REPAIR_CANDIDATE
def test_deploy_without_founder_only():
    p = load_example()
    p["authority_scope"] = "deploy"
    r = lint_packet(p)
    assert r["verdict"] == "REPAIR_CANDIDATE"
    assert any("FOUNDER_ONLY" in x for x in r["reasons"])


# T7 — P0 leakage in worker prompt -> REPAIR_CANDIDATE
def test_p0_leakage_repair_candidate():
    from p0pgr_packet_lint_v1 import p0_fingerprints
    prints = p0_fingerprints()
    assert prints, "no P0-CORE fingerprints found — leak detector is blind"
    p = load_example()
    p["task"] = p["task"] + " " + prints[0]
    r = lint_packet(p)
    assert r["verdict"] == "REPAIR_CANDIDATE"
    assert any("P0 leakage" in x for x in r["reasons"])


# T8 — valid HARD_BLOCK with allowed reason passes, not malformed
def test_valid_hard_block_reason_passes():
    p = load_example()
    p["quality_handling"]["allowed_result_states"] = ["PASS", "PARTIAL", "HARD_BLOCK"]
    p["quality_handling"]["hard_block_allowed_reasons"] = ["credential_or_security_exposure"]
    r = lint_packet(p)
    assert r["verdict"] == "PASS", r["reasons"]
    assert r["hard_block_configured"] is True


# T9 — cycle emits loop-state receipt with bundle_hash and quality_state
def test_cycle_emits_receipt(tmp_path):
    result = run_cycle(EXAMPLE)
    assert result["verdict"] == "PASS"
    assert result["decision"] == "DISPATCH_CLOUD"
    assert result["bundle_hash"] and len(result["bundle_hash"]) == 64
    assert result["quality_state"] in {
        "PASS", "PARTIAL", "DEGRADED", "SANDBOXED", "PROVISIONAL",
        "NEEDS_RETRY", "NEEDS_REVIEW", "FOUNDER_ONLY", "HARD_BLOCK",
    }
    assert result["receipt_schema_errors"] == []
    receipt = json.loads((ROOT / result["receipt_path"]).read_text())
    assert receipt["evidence"]["bundle_hash"] == result["bundle_hash"]
    assert receipt["cost"]["total_usd"] == 0.0  # no LLM calls in Phase-0
    assert receipt["dispatch"]["mode"] == "shadow"


# T10 — malformed packet round-trip files a repair candidate, lane continues
def test_repair_candidate_filed_not_lane_stop(tmp_path):
    p = load_example()
    del p["execution_mode"]
    bad = tmp_path / "bad_packet.json"
    bad.write_text(json.dumps(p))
    result = run_cycle(bad)
    assert result["verdict"] == "REPAIR_CANDIDATE"
    assert result["decision"] == "HOLD"
    assert result["receipt_schema_errors"] == []  # receipt still valid + written
    candidates = list((ROOT / "receipts" / "p0pgr" / "repair_candidates").glob(
        f"{result['cycle_id']}-*.json"))
    assert candidates, "repair candidate file not written"
