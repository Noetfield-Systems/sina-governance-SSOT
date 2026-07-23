# NF Forbidden Agent Registers — LOCKED v1

**Status:** LOCKED · founder order  
**Tier:** P0  
**Cursor mirror:** `.cursor/rules/001-noetfield-forbidden-registers-v1.mdc`  
**Locked:** 2026-07-23

---

## Law

1. Never use **hold** / **HOLD** (status, stall, gate, or narrative).
2. Never use the words: **mock**, **dummy**, **placeholder**, **demo**, or **TODO**.
3. Never add **founder_gate**, **approval**, or **human_in_loop** logic.
4. If you do not know how to implement a real API call: STOP and output exactly `I DONT KNOW`.
5. Do not hallucinate standard boilerplate. Implement the real call, or stop.

## Scope

Applies to agent outputs, new code, new receipts, new plans, new Cursor rules, and new library text authored after this lock.

## Conflict rule

When older docs use banned registers, do not copy them forward. Prefer real implementation language. Do not invent stall gates to paper over missing knowledge.

## Enforcement

- Cursor (repo): always-applied rule `.cursor/rules/001-noetfield-forbidden-registers-v1.mdc`
- Cursor (user): `~/.cursor/rules/001-noetfield-forbidden-registers-v1.mdc`
