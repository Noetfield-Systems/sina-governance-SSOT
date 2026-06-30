# Knowledge Bundle Spec v0.1

Status: SUBMITTED / SPEC / NO LIVE DEPLOY
Artifact type: `knowledge_bundle`
Artifact path: `cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json`
Generator: `scripts/brain_chatbot_refresh_v1.sh`
Manifest source: `data/CHATBOT_KNOWLEDGE_MANIFEST.json`

## Purpose

This spec defines the minimum valid shape for a SourceA Brain Worker knowledge bundle candidate. The bundle is data, not code. A verifier can check parseability, bounded size, required fields, chunk metadata, and deterministic content hash before any promotion gate can consider deployment.

## Required JSON Shape

The knowledge bundle MUST be a UTF-8 JSON object.

Top-level required keys:

- `version`: non-empty string
- `generated_at`: non-empty string
- `manifest_sha256`: lowercase 64-character SHA256 hex string
- `chunks`: non-empty array of chunk objects

No top-level executable code, functions, scripts, or HTML event handlers are valid bundle content.

## Size Bounds

- Minimum file size: 2 bytes.
- Maximum file size: 1,000,000 bytes.
- Maximum chunks: 2,000.
- Maximum single chunk text length: 20,000 characters.

## Must Parse

The verifier MUST reject the bundle unless:

- bytes decode as UTF-8
- JSON parsing succeeds
- parsed root value is an object
- `chunks` is an array
- every chunk is an object

## Required Chunk Metadata

Every chunk object MUST include:

- `id`: non-empty string
- `source`: non-empty string
- `title`: non-empty string
- `text`: non-empty string
- `metadata`: object

Every chunk `metadata` object MUST include:

- `source_path`: non-empty string
- `content_sha256`: lowercase 64-character SHA256 hex string

## Hash Rules

The verifier computes SHA256 over the exact submitted bundle bytes.

The submitted bundle SHA256 MUST match the descriptor field `proposed_sha256`.

The descriptor field `base_sha256` MUST be present and valid SHA256 hex, but Step 3 does not yet require comparison against live state. That comparison is reserved for later verifier/gate steps.

## Receipt Rules

For a knowledge bundle descriptor, the verifier receipt MUST include:

- `artifact_type`
- `artifact_path`
- `proposed_sha256`
- `base_sha256`
- `author_id`
- `subject`
- `schema_valid`
- `validator_runtime`
- `knowledge_bundle_spec_path`
- `knowledge_bundle_spec_sha256`
- `knowledge_bundle_spec_loaded`

## Step Boundary

This spec does not create a candidate bundle, validate a submitted bundle, emit a final PASS, deploy to the live Worker, or modify SourceA. It only defines what a valid knowledge bundle means for later steps.
