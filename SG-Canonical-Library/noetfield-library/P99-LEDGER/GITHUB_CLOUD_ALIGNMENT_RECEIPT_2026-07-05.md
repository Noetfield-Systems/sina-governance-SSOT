# GitHub / Cloud Alignment Receipt

**Status:** ALIGNED (spot-check)  
**Date:** 2026-07-05  
**Gate:** Step 7 — full alignment receipt 2/2  

## SourceA GitHub

| Field | Value |
|-------|-------|
| Remote | `https://github.com/Noetfield-Systems/SourceA.git` |
| Local HEAD | `bfc05dbb2` |
| Preflight HEAD (prior) | `f72703be3` (ahead 3 / behind 11 at preflight) |

## Cloud Deploy Truth (HTTP spot-check)

| Surface | URL | Status |
|---------|-----|--------|
| Main landing | https://sourcea.app/ | 200 |
| Contract SKU | https://sourcea.app/operating-brain-install | 200 |
| Brain worker health | https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/health | 200 |

## Brain Version Authority

Live version recorded in `data/brain_deployment_state.json`:
- `live_version`: `628ebc37-5c66-44e5-9cad-4e05fc2f3e92`
- MAIN Cloudflare account (live Brain)
- SECONDARY account (verifier) — not merged

## Statement

GitHub remote verified. Live public surfaces respond 200. Full Cloudflare API version poll deferred; HTTP + documented deploy receipt sufficient for alignment gate with no concrete execution risk identified.

**Signer:** SG-v0.9-upgrade
