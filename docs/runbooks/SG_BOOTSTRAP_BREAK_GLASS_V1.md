# Runbook — SG bootstrap break-glass v1

Break-glass exists only to land containment while SG runtime is absent.

A valid record must bind: exact repository, PR number, head SHA, base SHA, containment-only changed paths, founder/threshold actor, issuance time, expiry no longer than two hours, and single-use nonce. Record it in P99 before merge and close it immediately after exact merge-SHA verification.

Allowed: disable autonomous workflows; install HOLD; deny legacy authority; add runtime truth, tests, incident evidence, and SG v2 design. Forbidden: production deploy/promotion, secret mutation, authority commissioning, ruleset bypass, permission expansion, legacy credential revocation, or HOLD removal.

Any path/SHA/PR mismatch, expiry, replay, or scope expansion is `BLOCKED`. Break-glass cannot self-extend and cannot be issued by candidate SG, Motor, Brain, or NOOS.
