-- CATEGORY_DRIFT_GUARD_v1 — durable, queryable run history for the
-- category-registry drift guard. Follows the exact <subject>_v1 /
-- <subject>_runs_v1 pattern established in 001_workflow_census_v1.sql.
-- Project: noetfield (tkgpapowwplupyekpivy)
--
-- This is a READ-side history table. Nothing in this schema references
-- back into product/PRODUCT_CATEGORY_REGISTRY_v1.json by foreign key —
-- the registry is never written to by this pipeline, by design.

create table if not exists public.category_drift_status_v1 (
  category_id text primary key check (category_id in (
    'CAT-01-GOVERNED-AGENT-MEMORY', 'CAT-02-REPO-CODE-GRAPH-MEMORY',
    'CAT-03-PROMPT-GOVERNANCE-RUNTIME', 'CAT-04-CLOUD-FACTORY-LINES',
    'CAT-05-SANDBOX-WORKTREE-EXECUTION', 'CAT-06-AGENTIC-WORKFLOW-BUILDER',
    'CAT-07-NOCODE-APP-BUILDER', 'CAT-08-STUDIO-IDE-CONTROL-COCKPIT',
    'CAT-09-RECEIPT-TRUST-AUDIT-LAYER', 'CAT-10-VERTICAL-PROOF-PRODUCTS'
  )),
  registry_build_status text not null,
  observed_status text not null,
  drifted boolean not null default false,
  missing_proof_assets jsonb not null default '[]'::jsonb,
  out_of_scope_proof_assets jsonb not null default '[]'::jsonb,
  last_checked_at timestamptz not null,
  last_run_id text,
  updated_at timestamptz not null default now()
);

create index if not exists category_drift_status_v1_drifted_idx
  on public.category_drift_status_v1 (drifted);

create table if not exists public.category_drift_runs_v1 (
  run_id text primary key,
  recorded_at timestamptz not null default now(),
  categories_checked integer not null default 0,
  categories_drifted integer not null default 0,
  categories_missing_evidence integer not null default 0,
  categories_with_out_of_scope_evidence integer not null default 0,
  github_run_id text,
  verifier_status text check (verifier_status in ('PASS', 'FAIL', 'BLOCKED', 'UNVERIFIED')) default 'UNVERIFIED',
  receipt jsonb not null default '{}'::jsonb
);

create index if not exists category_drift_runs_v1_recorded_idx
  on public.category_drift_runs_v1 (recorded_at desc);

comment on table public.category_drift_status_v1 is
  'Current per-category drift status — upserted by each run of scripts/category_registry_drift_check_v1.py via .github/workflows/category-drift-guard-v1.yml. Never written to by anything else; never writes back to product/.';

comment on table public.category_drift_runs_v1 is
  'One row per category-drift-guard run, full receipt preserved in jsonb for audit.';
