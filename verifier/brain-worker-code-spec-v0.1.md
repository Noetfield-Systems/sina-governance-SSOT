# Brain Worker Bundle Spec v0.1

Artifact type: `brain_worker_bundle`

## Scope

Verifies a coordinated SourceA Brain Worker deploy set:

- `cloud/workers/sourcea-brain-chat-v1/src/index.js`
- `cloud/workers/sourcea-brain-chat-v1/src/guardrails.js`
- `cloud/workers/sourcea-brain-chat-v1/src/brain-core-gate-v1.js`
- `cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json`

## Hash rules

- `knowledge_bundle_sha256`: SHA256 of the bundle file bytes; must pass `knowledge_bundle` validation.
- `worker_code_sha256`: SHA256 of UTF-8 JSON object mapping each code path to its SHA256, keys sorted.
- `proposed_sha256`: SHA256 of UTF-8 JSON object mapping all four paths to SHA256, keys sorted.

## Descriptor fields

Same base fields as `knowledge_bundle`, plus:

- `worker_code_sha256`
- `knowledge_bundle_sha256`

## PASS

PASS when remote bytes at `candidate_ref` match all three hashes and bundle validation passes.
Independence checks unchanged from knowledge_bundle verification.
