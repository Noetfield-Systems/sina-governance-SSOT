# Deploy workflow (GOOD example - should PASS, zero violations)

Merges into main require passing status checks and a signed commit; any authorized
reviewer may approve protected-branch changes. No founder-specific identity is required.

Deploys promote automatically once tests are green, provenance is verified, and
rollback health checks pass.

If a task requests an out-of-scope capability, the response is: denied, with an
attached repair plan narrowing the target to the allowed capability set, or a
structured escalation packet with expiry and replay reference.

L5 review is reserved for anomaly-triggered cases only: unclassified irreversible
effects, unknown policy classes, or explicit break-glass actions.

Zero-drift required before proceeding, only when the sold claim depends on it.
