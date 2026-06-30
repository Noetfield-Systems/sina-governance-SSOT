# INDEPENDENT_VERIFIER_LOCK_PLAN_v0.1
Status: SUBMITTED / HOLD / SUBMITTED
Authority: SPEC only; no implementation authorized by this document
Governing SSOT: ssot/strategy-ssot-v6-split.md
Remote advisory staging: https://github.com/kazemnezhadsina144-dot/sina-governance-SSOT
No PASS claimed.

## 1. Executive Conclusion

Recommended v0 path: a Cloudflare Worker in a separate Cloudflare account, using a separate read-only GitHub credential, reading a private GitHub canonical repo and emitting strict D4 receipt output.

Remote git is prerequisite infrastructure, not authority by itself. Authority requires remote canonical artifact plus separate verifier identity, separate runtime, separate read-only credential, and strict receipt rules.

## 2. One Load-Bearing Question

What is a genuinely separate verifier read path in Sina's actual setup, where the verifier shares no builder identity, no builder runtime, and no builder network path with the thing it checks?

The first viable answer is an externally hosted verifier operated under separate credentials, reading a private remote canonical repo with read-only access and writing its own receipt output.

## 3. Definition Of Independence

An independent verifier must have:

- separate identity
- separate credentials
- separate runtime
- separate network path
- read-only access
- no mutation authority
- no builder self-verification

The actor that created or modified an artifact cannot emit final PASS for that artifact.

## 4. Why Local/Self Checks Cannot PASS

Same-Mac, same-Cursor, same-account, same-network checks can produce LOCAL_CHECK, SUBMITTED, or advisory evidence only.

They cannot emit PASS because they share too many failure domains with the builder: local filesystem state, shell environment, Git identity, network path, credentials, agent context, and prose reporting.

## 5. Minimum Verifier v0

Verifier v0 should be dumb and strict:

- fetch canonical repo/artifact from private remote
- check expected commit hash
- check expected file path
- compute content SHA256
- check receipt fields
- emit PASS / FAIL / BLOCKED only under D4 rules
- write receipt output
- never mutate source artifacts

It must not decide business intent, legal claims, public claims, founder strategy, or product direction.

## 6. Remote Prerequisite

A private remote is required because the verifier needs a canonical source it can read independently from the builder machine.

The repo should contain:

- `ssot/strategy-ssot-v6-split.md`
- governance ledger/spec artifacts when explicitly committed
- future D4 kernel/spec files only after founder authorization
- no SourceA, NOOS, or runtime implementation unless separately authorized

The verifier must read repository identity, commit hash, file path, file contents, and receipt files or receipt metadata.

The verifier should use a dedicated read-only deploy key, GitHub App installation token, or fine-scoped read token. Founder personal credentials should not be reused if avoidable.

## 7. Deployment Options

Cloudflare Worker on separate Cloudflare account/token:
Can emit real PASS if it uses separate identity/runtime/network, read-only GitHub credential, reads the private remote, and writes verifier-owned receipt output.

GitHub Actions with separate read-only token:
Can potentially emit PASS if isolated carefully, but has weaker separation because verification runs inside the same platform hosting the remote.

Small external VPS/Render/Railway job with read-only deploy key:
Can emit real PASS if operated under separate account/runtime/network and read-only credentials, with more operational burden.

Local second machine:
Advisory only. Useful for reducing obvious errors, but not PASS-capable.

## 8. Recommended v0 Path

Recommended: Cloudflare Worker in a separate Cloudflare account, using a dedicated read-only GitHub credential against the private canonical repo.

This optimizes for true independence, low cost, low operational complexity, future SourceA and NOOS compatibility, lower Sina manual load, and lower false-PASS risk.

## 9. PASS / FAIL / BLOCKED Rules

PASS is impossible unless all are true:

- verifier is not the builder
- verifier runtime is separate from builder runtime
- verifier read credential is separate and read-only
- verifier reads from remote canonical source
- expected commit hash matches
- expected file path matches
- content SHA256 matches
- receipt fields satisfy D4 rules
- output is written by verifier path, not builder path

FAIL applies when the remote artifact is reachable but commit, file, hash, or receipt fields mismatch.

BLOCKED applies when the remote, credential, independent runtime, expected inputs, canonical source proof, or receipt destination is unavailable.

## 10. Forbidden Patterns

- same-agent self-verification
- same Cursor session verification
- same Mac verification claiming PASS
- verifier using founder's normal GitHub credentials if avoidable
- verifier mutating artifacts
- verifier deciding business/legal/public claims
- verifier replacing Founder DECIDE
- PASS by mode flag
- PASS by prose report
- PASS without receipt fields

## 11. Next 10 Actions After Founder DECIDE

1. Founder chooses private remote provider/account for canonical staging.
2. Founder creates or authorizes private remote repo.
3. Agent adds remote only after explicit founder instruction.
4. Agent pushes only approved local staging commits after explicit founder instruction.
5. Founder creates separate verifier identity/account.
6. Founder or authorized agent creates read-only verifier credential.
7. Agent drafts verifier v0 spec-to-implementation prompt.
8. Agent implements verifier only after founder approves the implementation prompt.
9. Verifier fetches remote canonical artifact and emits receipt.
10. Founder reviews first verifier receipt before PASS-dependent automation.

## 12. Sina-Hours Reduction Map

The verifier path reduces Sina-hours by replacing repeated manual checks with strict receipt checks.

It reduces manual hash/path/commit checking, false done claims, context switches, repeated prompts, and time spent deciding whether an agent output can be trusted.

## 13. Open Founder DECIDEs

- verifier deployment account
- verifier credential model
- receipt output location
- public/private receipt visibility
- when D4 implementation becomes authorized

## 14. Stop Condition

Stop until founder selects the verifier deployment path and credential identity model.
