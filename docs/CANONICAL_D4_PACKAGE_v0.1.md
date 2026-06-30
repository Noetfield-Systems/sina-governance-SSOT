# CANONICAL_D4_PACKAGE_v0.1
Status: APPROVED-AS-SPEC / HOLD / SUBMITTED
Authority: SPEC only; no implementation authorized by this document
Governing SSOT: ssot/strategy-ssot-v6-split.md
SSOT staging commit: 69bba2d1a0eabd2bc6f608e5d1dffc7656e5b2f2
SSOT SHA256: 1ba4a793dba183388afd244ea21e850cad879c78824f78603e961070ae9b3af4
No PASS claimed.

## Purpose

CANONICAL_D4_PACKAGE_v0.1 defines the approved-as-spec direction for D4 receipt logic. It is a governance specification, not executable verifier code.

The package exists to prevent prose, mode flags, or local self-checks from being treated as final governance truth. D4 status must be computed from identity, path, receipt, and artifact fields.

## Core Invariant

PASS is computed per receipt from required identity/path fields. PASS is never declared by mode flag, agent prose, color, UI state, or advisory checker output.

## Status Vocabulary

- PASS: reserved for a future D4-compliant independent verifier path.
- FAIL: objective mismatch in required fields, hashes, paths, commits, or receipt constraints.
- BLOCKED: required verifier inputs, authority path, credentials, or receipt fields are unavailable.
- LOCAL_CHECK: same-machine or same-agent check only.
- REMOTE_CHECK_ADVISORY: remote-read advisory check only; not PASS.
- SUBMITTED: artifact has been produced for founder review or later verification.
- HOLD: approved concept or spec exists, but implementation is not authorized.

## Required Receipt Fields

A D4 receipt must bind at minimum:

- canonical source repository or artifact authority
- remote read path
- expected commit hash
- observed commit hash
- expected file path
- observed file path
- expected content SHA256
- observed content SHA256
- verifier identity
- verifier credential class
- verifier runtime identity
- receipt writer identity
- receipt timestamp
- status
- failure or blocked reason when not matching

## Runtime Rule Split

- R1/R2 plus D4-RECEIPT-LAW and D4-AGENT-NO-SELF-VERIFY are D4-portable.
- R3/R4/R5 are control-panel only.
- D4-RECEIPT-LAW means PASS/FAIL/BLOCKED is computed from receipt identity, path, artifact, and evidence fields.
- D4-AGENT-NO-SELF-VERIFY means author and subject must be structurally separated; an agent cannot certify its own work.
- R6/R7 in SourceA ops = Langfuse/Telegram, distinct from these D4 rules.
- No wholesale runtime-rule import into brain-governance specs.
- Runtime rule movement remains pending implementation.

## Non-Authority

This document does not:

- implement D4
- create a verifier
- authorize SourceA registry implementation
- authorize NOOS shim implementation
- create private remote authority
- replace Founder DECIDE
- convert advisory checks into PASS

## Implementation Gate

D4 implementation remains on HOLD until the founder authorizes an implementation prompt after required prerequisites are settled, including canonical remote policy and independent verifier path.
