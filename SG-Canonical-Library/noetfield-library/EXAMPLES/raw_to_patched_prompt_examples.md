# Raw-to-Patched Prompt Examples

## Example 1 — UX cleanup

Raw:
```text
Clean up the Partner Access page.
```

Patched:
```text
Improve Partner Access clarity without removing existing capabilities.

PRESERVE:
- Sign in
- Create account
- Partner Access Platform
- View application status
- Request Partner Access
- three tracks
- apply routes

REMOVE ONLY:
- none, unless explicitly listed later
```

---

## Example 2 — Remove conflicting funnel

Raw:
```text
Remove product funnel from Partner Access.
```

Patched:
```text
Remove only buyer/product CTAs from Partner Access.

REMOVE ONLY:
- Start free sandbox CTA
- product sandbox closing block
- buyer pricing CTA if shown on Partner Access

PRESERVE:
- Partner Access Platform
- Sign in
- Create account
- View application status
- Request Partner Access
```

---

## Example 3 — Deploy

Raw:
```text
Deploy the new build.
```

Patched:
```text
Deploy the new build and verify live truth.

VERIFY:
- build marker updated
- expected routes 200
- protected features visible
- expected removals absent
- tests pass
- receipt written
```
