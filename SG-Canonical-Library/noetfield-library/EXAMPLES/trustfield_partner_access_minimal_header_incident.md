# Example — TrustField Partner Access Minimal Header Incident

## Raw move
```text
Use a minimal partner-access header and remove conflicting product funnel.
```

## What went wrong
The agent may interpret "minimal" as permission to remove:
- Sign in
- Create account
- Partner Access Platform
- View application status

## Chess forecast
Move 1:
- Remove sandbox/product CTA.

Move 2 risk:
- Agent removes all header/account/platform CTAs.

Move 3 consequence:
- Candidate cannot access platform.
- Partner Access loses operational capability.
- Founder must manually repair live funnel.

## Patched move
```text
Improve Partner Access header clarity.

REMOVE ONLY:
- Start free sandbox CTA
- buyer pricing CTA
- product sandbox closing block

PRESERVE:
- Sign in
- Create account
- Partner Access Platform
- Enter Partner Access Platform
- View application status
- Request Partner Access
```

## Lesson
No clean UX is allowed to reduce operational capability.
