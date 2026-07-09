# CHESS_PATTERN_REASONING_MACHINE_v2.0

**Status:** Canonical reasoning method  
**Authority:** Tier-0 agent reasoning layer  
**Type:** Non-blocking move-improvement machine  
**Applies to:** implementation prompts, website edits, deploys, UX changes, onboarding funnels, legal/commercial wording, outbound systems, restore passes

---

## 1. Prime sentence

> **Chess reasoning does not block the move. It upgrades the move before execution.**

The machine is not a blocker, verifier wall, or permission loop.

It exists to help agents forecast likely next moves and improve their own execution.

---

## 2. Core loop

```text
Forecast → Patch → Proceed → Verify
```

Not:

```text
Forecast → Panic → Block → Ask founder forever
```

---

## 3. Practical questions

Before acting, an agent answers five questions:

```text
1. What is the move?
2. What can go wrong two moves later?
3. What must be preserved?
4. How should the instruction be patched?
5. How do we verify after execution?
```

---

## 4. Action labels

Only three labels are allowed:

| Label | Meaning |
|---|---|
| `PROCEED` | Low-risk. Execute normally. |
| `PROCEED_WITH_PATCH` | Improve wording/plan first, then execute. |
| `ASK_IF_IRREVERSIBLE` | Ask founder only if the action deletes, exposes, signs, spends, changes control, or makes legal/regulatory claims. |

Forbidden action label:

```text
BLOCK
```

The machine may warn, patch, narrow, or require rollback readiness, but it must not default to freeze.

---

## 5. Irreversible-action rule

Ask founder only when the move would:

- delete or hide working production features
- expose private material
- change equity/control terms
- make legal/regulatory status claims
- sign or send binding external commitments
- spend material money
- run destructive migrations
- transfer ownership, credentials, domains, repos, IP, or authority

For reversible work:

```text
Patch the move → preserve capability → proceed → verify
```

---

## 6. Anti-downgrade translation

When the user says:

```text
clean
minimal
simplify
polish
streamline
reduce clutter
modernize
make classy
separate funnels
```

the agent must translate safely as:

```text
Improve clarity without removing working capability.
```

Those words are not permission to delete features.

---

## 7. The chess pass object

```yaml
CHESS_PASS:
  move: ""
  immediate_goal: ""
  protected_assets: []
  likely_misread: []
  second_move_risk: []
  third_move_consequence: []
  patch_before_execution: ""
  verification_after_execution: []
  action: PROCEED | PROCEED_WITH_PATCH | ASK_IF_IRREVERSIBLE
```

---

## 8. Default behavior

If unsure:

```text
Preserve the existing feature.
Report uncertainty.
Proceed with the additive/patched move if reversible.
```

---

## 9. Final doctrine

> Before playing a move, forecast the next two moves.  
> If the move creates hidden damage, patch it.  
> If the action is reversible, proceed.  
> If the action is irreversible, ask.  
> After execution, verify the live board.
