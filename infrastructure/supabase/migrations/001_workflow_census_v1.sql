-- WORKFLOW_CENSUS_v1 — judging layer: every loop names its receipt and value_class.
-- Project: noetfield (tkgpapowwplupyekpivy)

create table if not exists public.workflow_census_v1 (
  loop_id text primary key,
  name text not null,
  host text not null check (host in ('cloudflare', 'railway', 'github', 'supabase', 'traffic', 'mac')),
  schedule text,
  invocations_per_day numeric,
  cost_usd_month numeric default 0,
  last_receipt_at timestamptz,
  last_receipt_id text,
  receipt_target text not null,
  value_class text not null check (value_class in ('REVENUE', 'GUARD', 'META', 'NONE')),
  census_run_id text not null,
  updated_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists workflow_census_v1_value_class_idx
  on public.workflow_census_v1 (value_class);

create index if not exists workflow_census_v1_last_receipt_idx
  on public.workflow_census_v1 (last_receipt_at desc nulls last);

create table if not exists public.workflow_census_runs_v1 (
  run_id text primary key,
  recorded_at timestamptz not null default now(),
  loop_count integer not null default 0,
  revenue_count integer not null default 0,
  guard_count integer not null default 0,
  meta_count integer not null default 0,
  none_count integer not null default 0,
  revenue_cost_usd_month numeric not null default 0,
  guard_cost_usd_month numeric not null default 0,
  meta_cost_usd_month numeric not null default 0,
  audit_flags jsonb not null default '[]'::jsonb,
  audit_status text not null default 'GREEN' check (audit_status in ('GREEN', 'YELLOW', 'RED')),
  receipt_path text,
  metadata jsonb not null default '{}'::jsonb
);

comment on table public.workflow_census_v1 is
  'Current-state census row per loop motor — updated weekly by scripts/workflow_census_v1.py';

comment on table public.workflow_census_runs_v1 is
  'Weekly census run rollup with deterministic standing-audit flags';
