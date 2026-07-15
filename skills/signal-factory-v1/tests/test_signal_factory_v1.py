# Six synthetic sample receipts for Signal Factory v1
# Tests validate receipt shape and optional-section gating expectations.

sample_receipts = [
    # 1. SEO vendor pitch
    {
        "signal_id": "s1",
        "timestamp": "2026-07-03T00:00:00Z",
        "source": "email:seo@example.com",
        "classification": "vendor",
        "decision": "reply",
        "scores": {"trust": 2, "risk": 1, "automation_value": 1, "commercial_value": 2},
        "risk_score": 1,
        "action": "reply",
        "status": "handled",
        "optional_sections": {}
    },
    # 2. cofounder/advisor DM
    {
        "signal_id": "s2",
        "timestamp": "2026-07-03T00:01:00Z",
        "source": "dm:linkedin:user123",
        "classification": "partner",
        "decision": "route",
        "scores": {"trust": 4, "risk": 2, "automation_value": 0, "commercial_value": 3},
        "risk_score": 2,
        "action": "route",
        "status": "escalated",
        "optional_sections": {}
    },
    # 3. client inquiry / bare paste
    {
        "signal_id": "s3",
        "timestamp": "2026-07-03T00:02:00Z",
        "source": "webform:contact",
        "classification": "client",
        "decision": "create_service_pattern",
        "scores": {"trust": 3, "risk": 2, "automation_value": 4, "commercial_value": 4},
        "risk_score": 2,
        "action": "create_service_pattern",
        "status": "candidate",
        "optional_sections": {"automation_recipe": "shell: starter", "commercial_idea": "SMB chatbot"}
    },
    # 4. investor/funding note
    {
        "signal_id": "s4",
        "timestamp": "2026-07-03T00:03:00Z",
        "source": "email:investor@vc.com",
        "classification": "investor",
        "decision": "route",
        "scores": {"trust": 3, "risk": 1, "automation_value": 0, "commercial_value": 5},
        "risk_score": 1,
        "action": "route",
        "status": "escalated",
        "optional_sections": {}
    },
    # 5. spam/scam
    {
        "signal_id": "s5",
        "timestamp": "2026-07-03T00:04:00Z",
        "source": "email:scam@example.com",
        "classification": "spam",
        "decision": "archive",
        "scores": {"trust": 0, "risk": 5, "automation_value": 0, "commercial_value": 0},
        "risk_score": 5,
        "action": "archive",
        "status": "discarded",
        "optional_sections": {}
    },
    # 6. regulatory-risk/custody request
    {
        "signal_id": "s6",
        "timestamp": "2026-07-03T00:05:00Z",
        "source": "form:custody",
        "classification": "risk",
        "decision": "route",
        "scores": {"trust": 1, "risk": 5, "automation_value": 0, "commercial_value": 0},
        "risk_score": 5,
        "action": "route",
        "status": "legal_review",
        "optional_sections": {}
    }
]

REQUIRED_KEYS = [
    "signal_id",
    "timestamp",
    "source",
    "classification",
    "decision",
    "risk_score",
    "action",
    "status"
]

OPTIONAL_ALLOWED_DECISIONS = {"build_automation", "create_service_pattern"}


def test_receipts_have_required_keys():
    for r in sample_receipts:
        for k in REQUIRED_KEYS:
            assert k in r, f"Missing required key {k} in receipt {r.get('signal_id') }"


def test_optional_sections_only_when_allowed():
    for r in sample_receipts:
        optional = r.get("optional_sections", {}) or {}
        if optional:
            assert r.get("decision") in OPTIONAL_ALLOWED_DECISIONS, (
                f"Optional sections present for decision {r.get('decision')} in {r.get('signal_id')}"
            )


if __name__ == "__main__":
    test_receipts_have_required_keys()
    test_optional_sections_only_when_allowed()
    print("All sample receipt checks passed.")
