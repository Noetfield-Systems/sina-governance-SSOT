import assert from "node:assert/strict";
import test from "node:test";

import { resolveGithubIdentity } from "../src/common.js";
import { deterministicReview, safePath, validateAction } from "../src/policy.js";

test("builder blocks authority, workflow, secret, and self-edit paths", () => {
  assert.equal(safePath("scripts/useful_fix.py"), true);
  assert.equal(safePath("tests/test_useful_fix.py"), true);
  assert.equal(safePath(".github/workflows/deploy.yml"), false);
  assert.equal(safePath("data/runtime_reality_v1.json"), false);
  assert.equal(safePath("workers/sg-authority-v2/src/index.ts"), false);
  assert.equal(safePath("workers/nf-hourly-ai-circles-v1/src/builder.js"), false);
  assert.equal(safePath("scripts/private-key.pem"), false);
});

test("builder permits one bounded draft and rejects oversized or protected changes", () => {
  assert.equal(
    validateAction({
      action: "draft_pr",
      changes: [{ path: "scripts/useful_fix.py", content: "print('ok')\n" }],
    }).ok,
    true,
  );
  assert.equal(
    validateAction({
      action: "draft_pr",
      changes: [{ path: ".github/workflows/unsafe.yml", content: "name: unsafe\n" }],
    }).ok,
    false,
  );
  assert.equal(
    validateAction({
      action: "draft_pr",
      changes: [{ path: "scripts/too_big.py", content: "x".repeat(24001) }],
    }).ok,
    false,
  );
});

test("verifier rejects protected paths and code without tests", () => {
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
});

test("builder and verifier GitHub identities stay disjoint and deny legacy advisory", () => {
  const builder = resolveGithubIdentity(
    {
      MOTOR_APP_ID: "4275961",
      MOTOR_INSTALLATION_ID: "145975487",
      MOTOR_APP_PRIVATE_KEY: "-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----",
    },
    "builder",
  );
  assert.equal(builder.appId, "4275961");

  const verifier = resolveGithubIdentity(
    {
      VERIFIER_GITHUB_APP_ID: "4330805",
      VERIFIER_GITHUB_INSTALLATION_ID: "147378007",
      VERIFIER_GITHUB_APP_PRIVATE_KEY:
        "-----BEGIN PRIVATE KEY-----\ndef\n-----END PRIVATE KEY-----",
    },
    "verifier",
  );
  assert.equal(verifier.appId, "4330805");
  assert.notEqual(builder.appId, verifier.appId);

  assert.throws(
    () =>
      resolveGithubIdentity(
        {
          VERIFIER_GITHUB_APP_ID: "4179901",
          VERIFIER_GITHUB_INSTALLATION_ID: "143449507",
          VERIFIER_GITHUB_APP_PRIVATE_KEY: "x",
        },
        "verifier",
      ),
    /legacy_advisory_app_denied/,
  );
  assert.throws(
    () =>
      resolveGithubIdentity(
        {
          VERIFIER_GITHUB_APP_ID: "4275961",
          VERIFIER_GITHUB_INSTALLATION_ID: "145975487",
          VERIFIER_GITHUB_APP_PRIVATE_KEY: "x",
        },
        "verifier",
      ),
    /motor_app_denied_for_verifier_identity/,
  );
});

test("verifier passes a bounded tested patch with healthy checks", () => {
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
