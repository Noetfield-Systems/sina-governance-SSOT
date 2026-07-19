import assert from "node:assert/strict";
import test from "node:test";

import { resolveGithubIdentity } from "../src/common.js";
import {
  buildProductionJobContract,
  containsDemoMarker,
  productionJobBody,
} from "../src/jobs.js";
import {
  deterministicReview,
  normalizeAction,
  safePath,
  validateAction,
} from "../src/policy.js";

function productionAction(overrides = {}) {
  return {
    action: "draft_pr",
    title: "Fix production routing failure",
    rationale: "The live routing path drops valid results; preserve them.",
    changes: [{ path: "scripts/useful_fix.py", content: "print('ok')\n" }],
    tests: ["python3 -m unittest tests/test_useful_fix.py"],
    ...overrides,
  };
}

test("builder blocks authority, workflow, secret, and self-edit paths", () => {
  assert.equal(safePath("scripts/useful_fix.py"), true);
  assert.equal(safePath("tests/test_useful_fix.py"), true);
  assert.equal(safePath(".github/workflows/deploy.yml"), false);
  assert.equal(safePath("data/runtime_reality_v1.json"), false);
  assert.equal(safePath("workers/sg-authority-v2/src/index.ts"), false);
  assert.equal(safePath("workers/nf-hourly-ai-circles-v1/src/builder.js"), false);
  assert.equal(safePath("scripts/private-key.pem"), false);
});

test("builder permits bounded production patches only", () => {
  assert.equal(validateAction(productionAction()).ok, true);
  assert.equal(
    validateAction(productionAction({
      changes: [{ path: ".github/workflows/unsafe.yml", content: "name: unsafe\n" }],
    })).ok,
    false,
  );
  assert.equal(
    validateAction(productionAction({
      changes: [{ path: "scripts/too_big.py", content: "x".repeat(24001) }],
    })).ok,
    false,
  );
  assert.equal(validateAction(productionAction({ tests: [] })).ok, false);
  assert.equal(validateAction({ action: "dispatch_job", job_id: "motor_job" }).ok, false);
  assert.equal(validateAction({ action: "issue", title: "plan" }).ok, false);
});

test("builder denies demo, fixture, and placeholder content", () => {
  for (const marker of [
    "demo task",
    "red fixture",
    "placeholder value",
    "assert add(2, 2) == 5",
    "sample_job",
  ]) {
    assert.equal(containsDemoMarker(marker), true);
    assert.equal(validateAction(productionAction({ rationale: marker })).ok, false);
  }
});

test("verifier rejects protected paths, missing tests, and missing CI", () => {
  const verdict = deterministicReview(
    { draft: true, head: { ref: "ai-circle/20260718-example" } },
    [
      {
        filename: "scripts/change.py",
        additions: 4,
        deletions: 1,
        patch: "@@ -1 +1 @@\n-old\n+new",
        status: "modified",
      },
      {
        filename: ".github/workflows/escape.yml",
        additions: 3,
        deletions: 0,
        patch: "@@ -0,0 +1 @@\n+unsafe",
        status: "added",
      },
    ],
    { check_runs: [] },
  );
  assert.equal(verdict.pass, false);
  assert.ok(verdict.findings.includes("code_change_without_test_change"));
  assert.ok(verdict.findings.includes("protected_path:.github/workflows/escape.yml"));
  assert.ok(verdict.findings.includes("no_check_runs"));
});

test("builder and verifier identities stay disjoint and deny legacy advisory", () => {
  const builder = resolveGithubIdentity(
    {
      MOTOR_APP_ID: "4275961",
      MOTOR_INSTALLATION_ID: "145975487",
      MOTOR_APP_PRIVATE_KEY: "-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----",
    },
    "builder",
  );
  const verifier = resolveGithubIdentity(
    {
      VERIFIER_GITHUB_APP_ID: "4330805",
      VERIFIER_GITHUB_INSTALLATION_ID: "147378007",
      VERIFIER_GITHUB_APP_PRIVATE_KEY:
        "-----BEGIN PRIVATE KEY-----\ndef\n-----END PRIVATE KEY-----",
    },
    "verifier",
  );
  assert.equal(builder.appId, "4275961");
  assert.equal(verifier.appId, "4330805");
  assert.notEqual(builder.appId, verifier.appId);
  assert.throws(
    () => resolveGithubIdentity({
      VERIFIER_GITHUB_APP_ID: "4179901",
      VERIFIER_GITHUB_INSTALLATION_ID: "143449507",
      VERIFIER_GITHUB_APP_PRIVATE_KEY: "x",
    }, "verifier"),
    /legacy_advisory_app_denied/,
  );
});

test("verifier passes a bounded tested patch with completed healthy CI", () => {
  const verdict = deterministicReview(
    { draft: true, head: { ref: "ai-circle/20260718-example" } },
    [
      {
        filename: "scripts/change.py",
        additions: 4,
        deletions: 1,
        patch: "@@ -1 +1 @@\n-old\n+new",
        status: "modified",
      },
      {
        filename: "tests/test_change.py",
        additions: 5,
        deletions: 0,
        patch: "@@ -0,0 +1 @@\n+test",
        status: "added",
      },
    ],
    { check_runs: [{ name: "unit", status: "completed", conclusion: "success" }] },
  );
  assert.equal(verdict.pass, true);
  assert.deepEqual(verdict.findings, []);
});

test("normalizeAction converts changes-only payload but validation remains strict", () => {
  const action = normalizeAction({
    title: "Fix production result persistence",
    rationale: "Persist real provider output before returning.",
    changes: [{ path: "scripts/x.py", content: "print(1)\n" }],
    tests: ["python3 -m unittest tests/test_x.py"],
  });
  assert.equal(action.action, "draft_pr");
  assert.equal(validateAction(action).ok, true);
});

test("production job contract pins exact base and real acceptance checks", () => {
  const action = productionAction();
  const contract = buildProductionJobContract({
    receiptId: "builder-20260719000000-abcdef12",
    repo: "Noetfield-Systems/sina-governance-SSOT",
    base: "main",
    baseSha: "a".repeat(40),
    action,
  });
  assert.equal(contract.schema, "nf.production-repository-job.v1");
  assert.equal(contract.target.exact_base_sha, "a".repeat(40));
  assert.equal(contract.execution.kind, "github_draft_pr");
  assert.match(productionJobBody(contract), /No synthetic fixture/);
});
