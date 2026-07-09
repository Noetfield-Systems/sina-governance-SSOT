# FOUNDER INTENT FILTER v1 — Canon

Status: **binding**. This file is the short law. `policy/founder_intent.yaml` is the machine-readable form of the same law. `scripts/check_founder_runtime_dependency.py` enforces it in CI. If any of the three disagree, this file wins and the others must be fixed to match.

Source: downscoped from `deep-research-report.md` (Founder Intent Filter for Sandbox-First Autonomy). That report is the theory layer — full enterprise stack (OPA, Kubernetes admission, Firecracker, gVisor, SLSA, Sigstore, in-toto). This canon is the **implementation layer** for the current repo: no new infra, just rules a checker script can enforce today.

## Goal

Reduce founder (Sina) runtime dependency, preserve sandbox-first autonomy, and move toward deterministic autorun — without adopting infrastructure the current repo doesn't already have.

## What this filter is NOT

It is not a human approval router. It does not ask "would Sina approve this run?" It asks three narrower, machine-checkable questions per control:

1. Does it reduce Sina's future workload on the normal path?
2. Is it a boundary wall (fires only on violation/escape) or a permission loop (pauses routine work)?
3. When it denies, does it preserve progress (repair/reroute/escalation) or freeze into a dead-end blocker?

## Hard rules (v1)

1. **No founder-specific approval on the normal path.** If successful routine operation requires Sina's identity, click, key, or synchronous availability, the control fails and must be redesigned.
2. **Boundary wall, not permission loop.** Controls fire only at admission, capability issuance, side-effect execution, or audit — never as a routine pause on compliant work.
3. **Denial must preserve progress.** Every denial returns one of: a narrower allowed target, a request for a missing artifact, a safe substitute action, a repair plan, or a structured escalation packet. "Not allowed" / "await approval" / "manual review required" with nothing else is a contract violation.
4. **L5 (or equivalent max-severity review) is anomaly-only.** Normal rule is no L5. It fires only for unclassified irreversible effects, unknown policy classes, legal/compliance ambiguity, or explicit break-glass — never as a routine workflow stage.
5. **Merge and phase unlocks are evidence-based, not founder-click-based.** Promotion happens automatically when: required checks pass, provenance/signature present (if the repo already does this), rollback path healthy, and no policy violations. A manual "Sina merges" step is a red anti-pattern.
6. **Repeated founder judgment must become policy.** If the same judgment call is asked of Sina more than 3 times, it must be codified into policy, a parameter, or an exemplar — or the control is flagged as a recurring runtime dependency and fails.
7. **Frozen zero-drift/proof targets don't block execution** unless the specific sold claim actually depends on that exact proof. Perfection targets are goals, not gates, by default.

## Severity rubric (per control)

- **Green** — any authorized role or no human needed; Sina's involvement is zero on the normal path.
- **Yellow** — human involved, but not founder-specific, limited to protected-branch changes, high-risk deploys, or break-glass.
- **Red** — Sina is a required approver, secret holder, or merge/deploy operator for routine work. Red must be redesigned or explicitly logged as a temporary, expiring exception.

## Escape packet contract (rule 3, made concrete)

A structured escape/escalation packet must contain, at minimum:
- what was denied (the specific capability or action)
- why (which rule/policy it violated)
- risk class / blast radius
- the minimum proposed change that would cross the boundary safely
- an expiry (overrides are temporary by construction — see "override half-life" below)
- a replay reference (so the same input reproduces the same decision)

## Metrics this filter should be able to report (evidence, not vibes)

| Metric | Desired direction |
|---|---|
| Founder touch rate (Sina touches / all successful normal-path runs) | → 0 |
| Founder specificity (paths requiring Sina specifically) | 0 on normal path |
| Progress preservation rate (denials with repair/reroute/escape / all denials) | High |
| Override half-life (median age of temp overrides before removal/codification) | Low |
| False-positive denial rate | Low |

## What is explicitly out of scope for v1

Do not introduce Kubernetes admission, OPA/Rego, Firecracker, gVisor, SLSA attestation infra, Sigstore, or in-toto **unless the repo already uses them**. v1 enforcement is: GitHub branch/merge checks already in use, a repo-local policy YAML, a Python checker script, negative tests, and a receipt — nothing heavier.

## Enforcement chain

```
FOUNDER_INTENT_FILTER.md (this file, binding law)
        ↓
policy/founder_intent.yaml (machine-readable rules + violation patterns)
        ↓
scripts/check_founder_runtime_dependency.py (scans repo, applies rules, exit 1 on violation)
        ↓
tests/negative_cases/* (fixtures proving the checker actually catches each rule)
        ↓
receipts/*.json (what was scanned, what failed, what passed — sealed per run)
```

CI gate: any PR that trips a rule with no attached exception (explicit, expiring, logged) fails the build.
