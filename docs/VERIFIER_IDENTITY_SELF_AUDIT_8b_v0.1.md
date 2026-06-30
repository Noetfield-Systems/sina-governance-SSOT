# VERIFIER_IDENTITY_SELF_AUDIT_8b_v0.1
Status: SUBMITTED / HOLD / SUBMITTED
Authority: SPEC audit only; no implementation authorized by this document
Related plan: docs/INDEPENDENT_VERIFIER_LOCK_PLAN_v0.1.md
No PASS claimed.

## 1. Executive Conclusion

A Cloudflare Worker with a GitHub read-only token is not automatically identity-independent.

If the token is minted from Sina's normal GitHub account, the model is permission-separated but identity-shared. It may support REMOTE_CHECK_ADVISORY, but it should not emit strict D4 PASS because the verifier credential still roots back to the same human/account authority that owns or pushes the canonical repo.

Cheapest genuinely PASS-capable v0: private repo under a separate governance GitHub org, verified by a GitHub App or separate verifier account with read-only access, running from a separate Cloudflare account/runtime.

## 2. Identity Root Vs Permission Split

Identity root is the upstream authority that owns, controls, can recover, revoke, recreate, or impersonate the credential used by the verifier.

For this verifier system, identity root includes:

- GitHub account or org that owns the canonical repo
- account that mints verifier credentials
- account that can grant/revoke verifier access
- account that can push canonical changes
- Cloudflare account that runs verifier runtime
- any recovery/admin path that can override these identities

Permission separation means a credential is scoped read-only.

Identity-root separation means the credential is controlled by a different account or authority path than the builder/pusher.

A read-only token can be permission-separated while still identity-shared.

## 3. Audit Of Fine-Grained Token From Sina Account

Model: Sina personal GitHub account owns the repo and also mints a fine-grained read-only token for the verifier.

Classification: permission-separated but identity-shared.

It is not fully independent because the same identity root controls both the canonical repo authority and the verifier credential. It is not same-path/local only because the Cloudflare Worker and remote fetch still improve runtime/network separation.

Receipt level:

- PASS: no, under strict D4
- BLOCKED: yes, if strict PASS was requested
- FAIL: yes, for objective mismatches
- REMOTE_CHECK_ADVISORY: yes
- LOCAL_CHECK: no, because fetch/runtime are remote, but identity root is still shared

## 4. PASS Capability By Credential Model

GitHub App installation identity:

- Identity root separation: strong if app is owned/controlled outside the builder identity and installed with read-only repo permissions.
- Credential scope: fine-grained installation token, short-lived, read-only.
- Cost/complexity: low to medium.
- False-PASS risk: low if app ownership/admin is separated.
- Strict D4 PASS-capable: yes, if app/root ownership is separate from builder/pusher.
- v0 advisory acceptable: yes.

Separate verifier GitHub account with read-only access:

- Identity root separation: strong if account recovery/admin is separate from builder identity.
- Credential scope: read-only collaborator or deploy key/token.
- Cost/complexity: low.
- False-PASS risk: low to medium, depending on account recovery hygiene.
- Strict D4 PASS-capable: yes, if separate account is not controlled by builder path.
- v0 advisory acceptable: yes.

Separate GitHub organization with least-privilege verifier app/account:

- Identity root separation: strongest realistic option.
- Credential scope: org-owned repo, explicit roles, read-only app/account.
- Cost/complexity: medium.
- False-PASS risk: lowest.
- Strict D4 PASS-capable: yes.
- v0 advisory acceptable: yes.

Fine-grained token from Sina account:

- Identity root separation: weak; identity-shared.
- Credential scope: can be read-only and repo-scoped.
- Cost/complexity: lowest.
- False-PASS risk: medium to high for strict governance.
- Strict D4 PASS-capable: no.
- v0 advisory acceptable: yes, as REMOTE_CHECK_ADVISORY.

## 5. Repo Ownership Recommendation

Do not treat the current remote advisory repo as final PASS-capable authority until repo ownership and verifier credential identity root are settled.

Sina personal account:

- Lowest friction.
- Suitable for local staging continuation or advisory remote checks.
- Not ideal for strict PASS because builder/founder identity root likely owns both source authority and verifier credential path.

Separate governance org:

- Recommended for PASS-capable authority.
- Gives clearer separation between builder/pusher identity, verifier identity, and repo administration.
- Supports future SourceA and NOOS governance without tying everything to Sina's personal account.

Other account model:

- Acceptable only if it creates real separation of repo ownership, verifier credential issuance, recovery/admin control, and builder/pusher access.
- Must be judged by identity-root separation, not naming.

## 6. Recommended PASS-Capable v0

Cheapest genuinely PASS-capable v0:

- create a separate private GitHub governance org
- put the canonical private repo under that org
- use a GitHub App installation or separate verifier GitHub account with read-only access
- run verifier in a separate Cloudflare account/runtime
- ensure builder/pusher identity cannot mint or replace verifier credentials alone
- ensure verifier cannot mutate source artifacts

This is the minimum model that preserves separate runtime, network path, credential, and identity root.

## 7. Acceptable Advisory-Only Fallback

Cheapest acceptable v0 advisory model if full independence is deferred:

- private GitHub repo under Sina personal account
- advisory checker reads remote
- fine-grained read-only GitHub token minted from Sina account if needed
- receipt status limited to REMOTE_CHECK_ADVISORY, FAIL, or BLOCKED
- no strict D4 PASS

This reduces manual checking, but it must not be represented as independent final verification.

## 8. Exact Founder DECIDE

Before creating private GitHub repo:
Founder must decide repo ownership model: Sina personal account, separate governance org, or another separated account model.

Before adding remote:
Founder must decide the exact remote URL/account and whether it is advisory-only or PASS-capable.

Before pushing:
Founder must decide which local commits are allowed to become remote canonical staging artifacts.

Before creating verifier credential:
Founder must decide credential model: GitHub App, separate verifier account, org-scoped access, or Sina fine-grained advisory token.

Before implementing verifier:
Founder must decide expected receipt level: strict D4 PASS-capable verifier or advisory remote checker.

## 9. Stop Condition

Stop until founder decides repo ownership and verifier credential identity root for the PASS-capable verifier path.
