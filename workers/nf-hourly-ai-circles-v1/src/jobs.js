/**
 * Bounded assist-only job catalog for the hourly builder circle.
 * Dispatches real Runway plans/jobs; never merges, deploys, or lifts HOLD.
 */

export const JOB_CATALOG = Object.freeze({
  commissioning_tick: {
    id: "commissioning_tick",
    kind: "repository_dispatch",
    repo_env: "RUNWAY_REPO",
    default_repo: "Noetfield-Systems/NOETFIELD-RUNWAY",
    event_type: "commissioning_tick",
    value_class: "GUARD",
    description: "Commissioning Runway closed loop: observe → heal → QUALIFIED evidence → draft PR",
  },
  motor_job: {
    id: "motor_job",
    kind: "workflow_dispatch",
    repo_env: "RUNWAY_REPO",
    default_repo: "Noetfield-Systems/NOETFIELD-RUNWAY",
    workflow: "motor-job.yml",
    ref_env: "RUNWAY_REF",
    default_ref: "main",
    inputs: {
      failing_test: "assert add(2, 2) == 5  # currently returns 4",
      language: "python",
    },
    value_class: "REVENUE",
    description: "Real multi-step Motor job: compile plan → route cheap models → receipt",
  },
  repair_run: {
    id: "repair_run",
    kind: "workflow_dispatch",
    repo_env: "RUNWAY_REPO",
    default_repo: "Noetfield-Systems/NOETFIELD-RUNWAY",
    workflow: "repair-run.yml",
    ref_env: "RUNWAY_REF",
    default_ref: "main",
    inputs: {},
    value_class: "REVENUE",
    description: "Software Repair Runway: diagnose failing check → machine draft PR → exact-head CI",
  },
  live_model_smoke: {
    id: "live_model_smoke",
    kind: "workflow_dispatch",
    repo_env: "RUNWAY_REPO",
    default_repo: "Noetfield-Systems/NOETFIELD-RUNWAY",
    workflow: "live-model-smoke.yml",
    ref_env: "RUNWAY_REF",
    default_ref: "main",
    inputs: {},
    value_class: "GUARD",
    description: "Prove cheap model providers still answer live",
  },
});

export function listJobs() {
  return Object.values(JOB_CATALOG);
}

export function resolveJob(jobId) {
  if (!jobId) return null;
  return JOB_CATALOG[String(jobId).trim()] || null;
}

export function pickRotatingJob(atIso = new Date().toISOString(), prefer = null) {
  if (prefer && JOB_CATALOG[prefer]) return JOB_CATALOG[prefer];
  const order = ["motor_job", "commissioning_tick", "repair_run", "live_model_smoke"];
  const hour = new Date(atIso).getUTCHours();
  return JOB_CATALOG[order[hour % order.length]];
}

export async function dispatchRunwayJob(token, env, job, receiptMeta = {}) {
  const spec = typeof job === "string" ? resolveJob(job) : job;
  if (!spec) return { ok: false, error: "unknown_job" };
  const repo = String(env[spec.repo_env] || spec.default_repo).trim();
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github+json",
    "Content-Type": "application/json",
    "User-Agent": "nf-hourly-builder-circle-v1",
    "X-GitHub-Api-Version": "2022-11-28",
  };

  if (spec.kind === "repository_dispatch") {
    const resp = await fetch(`https://api.github.com/repos/${repo}/dispatches`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        event_type: spec.event_type,
        client_payload: {
          source: "nf-hourly-builder-circle-v1",
          job_id: spec.id,
          at: receiptMeta.at || new Date().toISOString(),
          receipt_id: receiptMeta.receipt_id || null,
          hold: "HOLD",
          mode: "ASSIST_ONLY",
        },
      }),
    });
    return {
      ok: resp.status === 204,
      status: resp.status,
      kind: "dispatch_job",
      job_id: spec.id,
      repo,
      event_type: spec.event_type,
      value_class: spec.value_class,
      description: spec.description,
    };
  }

  if (spec.kind === "workflow_dispatch") {
    const ref = String(env[spec.ref_env] || spec.default_ref || "main").trim();
    const inputs = {
      ...(spec.inputs || {}),
      ...(receiptMeta.inputs || {}),
    };
    const resp = await fetch(
      `https://api.github.com/repos/${repo}/actions/workflows/${encodeURIComponent(spec.workflow)}/dispatches`,
      {
        method: "POST",
        headers,
        body: JSON.stringify({
          ref,
          inputs,
        }),
      },
    );
    return {
      ok: resp.status === 204,
      status: resp.status,
      kind: "dispatch_job",
      job_id: spec.id,
      repo,
      workflow: spec.workflow,
      ref,
      inputs,
      value_class: spec.value_class,
      description: spec.description,
    };
  }

  return { ok: false, error: `unsupported_job_kind:${spec.kind}` };
}

/**
 * Deterministic bounded plan+test artifact when models return unusable patches.
 * Creates a real reviewable draft PR the independent verifier can criticize.
 */
export function buildDeterministicJobPlanArtifact(job, receiptId, planWhy = "") {
  const stamp = new Date().toISOString();
  const jobId = job?.id || "motor_job";
  const scriptPath = "scripts/hourly_ai_circle_job_plan_v1.py";
  const testPath = "tests/test_hourly_ai_circle_job_plan_v1.py";
  const script = `#!/usr/bin/env python3
"""Hourly AI circle job plan artifact (assist-only; HOLD preserved)."""
from __future__ import annotations

import json
from typing import Any

SCHEMA = "nf.hourly-ai-circle-job-plan.v1"
ALLOWED_JOBS = {
    "commissioning_tick",
    "motor_job",
    "repair_run",
    "live_model_smoke",
}


def build_plan(
    job_id: str,
    receipt_id: str,
    why: str = "",
    hold: str = "HOLD",
) -> dict[str, Any]:
    if job_id not in ALLOWED_JOBS:
        raise ValueError(f"job_id_not_allowlisted:{job_id}")
    if hold != "HOLD":
        raise ValueError("hold_must_remain_HOLD")
    return {
        "schema": SCHEMA,
        "job_id": job_id,
        "receipt_id": receipt_id,
        "why": why,
        "mode": "ASSIST_ONLY",
        "hold": hold,
        "forbidden": ["merge", "deploy", "authority_change", "secret_change"],
        "closed_loop": [
            "Observe",
            "Detect",
            "Plan",
            "DispatchOrDraft",
            "IndependentVerify",
            "RepairByNewDraftOnly",
            "ReObserve",
        ],
    }


def main() -> None:
    plan = build_plan(${JSON.stringify(jobId)}, ${JSON.stringify(receiptId)}, ${JSON.stringify(planWhy.slice(0, 400))})
    print(json.dumps(plan, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
`;

  const test = `"""Tests for hourly AI circle job plan artifact."""
from __future__ import annotations

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "hourly_ai_circle_job_plan_v1",
    ROOT / "scripts" / "hourly_ai_circle_job_plan_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)


class JobPlanTests(unittest.TestCase):
    def test_build_plan_allowlisted(self) -> None:
        plan = MOD.build_plan("motor_job", "receipt-test", "bounded proof")
        self.assertEqual(plan["schema"], MOD.SCHEMA)
        self.assertEqual(plan["hold"], "HOLD")
        self.assertEqual(plan["job_id"], "motor_job")
        self.assertIn("IndependentVerify", plan["closed_loop"])

    def test_rejects_unknown_job(self) -> None:
        with self.assertRaises(ValueError):
            MOD.build_plan("merge_main", "receipt-test")

    def test_rejects_hold_lift(self) -> None:
        with self.assertRaises(ValueError):
            MOD.build_plan("motor_job", "receipt-test", hold="LIFTED")


if __name__ == "__main__":
    unittest.main()
`;

  return {
    action: "draft_pr",
    title: `ai-circle: wire real job plan for ${jobId}`,
    rationale:
      `Deterministic fallback produced a bounded job-plan artifact for \`${jobId}\` ` +
      `so the independent verifier has a real draft PR to criticize. ` +
      `Companion Runway dispatch is attempted in the same tick. HOLD preserved.\n` +
      `Generated_at: ${stamp}\nWhy: ${planWhy || "models returned no safe patch"}`,
    changes: [
      { path: scriptPath, content: script },
      { path: testPath, content: test },
    ],
    tests: [
      "python3 -m unittest tests/test_hourly_ai_circle_job_plan_v1.py",
      "Independent verifier must review exact head SHA",
    ],
  };
}
