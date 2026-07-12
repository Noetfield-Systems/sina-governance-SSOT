# Signal Factory v1 Skill

name: Signal Factory v1
version: 0.1.0
maintainer: SourceA / Noetfield Systems
description: |
  Skill to convert inbound market signals (vendor pitches, partner DMs, client forms)
  into structured SIGNAL SUMMARY, CLASSIFICATION, IMPLIED NEED, SCORES, DECISION,
  NEXT ACTION, RECEIPT JSON, and MEMORY LINE. Optional sections (AUTOMATION_RECIPE,
  COMMERCIAL_IDEA) produced only when decision ∈ {build_automation, create_service_pattern}.

schema: receipt_schema.json

enums:
  classification: [vendor, partner, client, investor, risk, bug, idea, spam, unclear]
  decision: [ignore, archive, reply, route, build_automation, create_service_pattern]

scores:
  anchors:
    - name: trust
      range: [0,5]
    - name: risk
      range: [0,5]
    - name: automation_value
      range: [0,5]
    - name: commercial_value
      range: [0,5]

gating:
  optional_sections_allowed_if_decision_in:
    - build_automation
    - create_service_pattern

risk_routing:
  threshold: 4
  action: route_to_human_review

receipt_requirements:
  required_fields: [signal_id, timestamp, source, classification, decision, risk_score, action, status]

notes: |
  - Preserve provenance: do not launder sender claims as facts; include original text in evidence when escalating.
  - Partner/advisor items require milestone template before equity discussion.
  - No outbound connectors enabled by default.
