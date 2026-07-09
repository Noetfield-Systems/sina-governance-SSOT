// Independent verifier for category_registry_drift_check_receipt_v1 receipts.
// Mirrors the doctrine in workers/github-app-advisory/index.js: never trust
// the job's own claim. This Worker re-derives PASS/FAIL from the receipt's
// OWN internal logic (does it cover all 10 known categories? is every
// observed_status a legal value? is `drifted` self-consistent?) and proves
// it ran on a separate account/runtime via the cf-ray edge header — the
// same independence proof already used for the SSOT verifier.
//
// Phase-2/future: this Worker could additionally re-fetch
// product/PRODUCT_CATEGORY_REGISTRY_v1.json from GitHub directly (via a
// GitHub App, same pattern as github-app-advisory) to independently
// recompute drift rather than only validating the submitted receipt's
// internal consistency. Not built in Phase 1 — that needs its own
// credential wiring, which is a founder-authorized step, not a code change.

const KNOWN_CATEGORY_IDS = [
  "CAT-01-GOVERNED-AGENT-MEMORY",
  "CAT-02-REPO-CODE-GRAPH-MEMORY",
  "CAT-03-PROMPT-GOVERNANCE-RUNTIME",
  "CAT-04-CLOUD-FACTORY-LINES",
  "CAT-05-SANDBOX-WORKTREE-EXECUTION",
  "CAT-06-AGENTIC-WORKFLOW-BUILDER",
  "CAT-07-NOCODE-APP-BUILDER",
  "CAT-08-STUDIO-IDE-CONTROL-COCKPIT",
  "CAT-09-RECEIPT-TRUST-AUDIT-LAYER",
  "CAT-10-VERTICAL-PROOF-PRODUCTS",
];

const VALID_BUILD_STATUSES = new Set([
  "live-running",
  "built-not-activated",
  "partial-scaffold",
  "spec-doc-only",
  "concept-only",
]);

const VALID_OBSERVED_STATUSES = new Set([...VALID_BUILD_STATUSES, "unknown-evidence-missing"]);

const SECONDARY_CF_ACCOUNT_ID = "b7282b4a5c17b84d62e3ef8866b878f8"; // same secondary account already used by the SSOT verifier

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function edgeMetadata(request, env) {
  const edgeExecutionProven = Boolean(request.headers.get("cf-ray"));
  const secondaryAccountProven = env.CF_ACCOUNT_ID === SECONDARY_CF_ACCOUNT_ID;
  return {
    cf_account_id: env.CF_ACCOUNT_ID || null,
    cf_ray: request.headers.get("cf-ray"),
    cf_colo: request.cf?.colo || null,
    edge_execution_proven: edgeExecutionProven,
    secondary_account_proven: secondaryAccountProven,
    runtime_separation: edgeExecutionProven && secondaryAccountProven ? "SECONDARY_CF_ACCOUNT_EDGE_PROVEN" : "UNCONFIRMED",
  };
}

// Independently re-derive whether the SUBMITTED receipt is internally
// consistent. This never trusts drift/missing counts the job reports — it
// recomputes them from the per-category `results` array and compares.
function verifyReceiptConsistency(receipt) {
  const failures = [];

  if (!receipt || typeof receipt !== "object") {
    return { failures: ["receipt must be a JSON object"], recomputed: null };
  }
  if (receipt.schema !== "category_registry_drift_check_receipt_v1") {
    failures.push(`unexpected schema: ${receipt.schema}`);
  }
  if (!Array.isArray(receipt.results)) {
    return { failures: [...failures, "receipt.results must be an array"], recomputed: null };
  }

  const seenIds = new Set();
  let recomputedDrifted = 0;
  let recomputedMissing = 0;
  let recomputedOutOfScope = 0;

  for (const result of receipt.results) {
    if (!result || typeof result !== "object") {
      failures.push("a result entry is not an object");
      continue;
    }
    seenIds.add(result.category_id);

    if (!VALID_OBSERVED_STATUSES.has(result.observed_status)) {
      failures.push(`${result.category_id}: observed_status "${result.observed_status}" is not a legal value`);
    }
    if (result.registry_build_status && !VALID_BUILD_STATUSES.has(result.registry_build_status)) {
      failures.push(`${result.category_id}: registry_build_status "${result.registry_build_status}" is not a legal value`);
    }

    const missingCount = Array.isArray(result.missing_proof_assets) ? result.missing_proof_assets.length : 0;
    const outOfScopeCount = Array.isArray(result.out_of_scope_proof_assets) ? result.out_of_scope_proof_assets.length : 0;
    const expectedDrifted = missingCount > 0;

    if (Boolean(result.drifted) !== expectedDrifted) {
      failures.push(
        `${result.category_id}: drifted=${result.drifted} is inconsistent with missing_proof_assets.length=${missingCount}`,
      );
    }

    if (missingCount > 0) recomputedDrifted += 1;
    if (missingCount > 0) recomputedMissing += 1;
    if (outOfScopeCount > 0) recomputedOutOfScope += 1;
  }

  for (const expectedId of KNOWN_CATEGORY_IDS) {
    if (!seenIds.has(expectedId)) failures.push(`missing category in results: ${expectedId}`);
  }
  for (const seenId of seenIds) {
    if (!KNOWN_CATEGORY_IDS.includes(seenId)) failures.push(`unknown category_id in results: ${seenId}`);
  }

  if (receipt.categories_drifted !== recomputedDrifted) {
    failures.push(`categories_drifted claimed=${receipt.categories_drifted} recomputed=${recomputedDrifted}`);
  }
  if (receipt.categories_missing_evidence !== recomputedMissing) {
    failures.push(`categories_missing_evidence claimed=${receipt.categories_missing_evidence} recomputed=${recomputedMissing}`);
  }

  return {
    failures,
    recomputed: {
      categories_drifted: recomputedDrifted,
      categories_missing_evidence: recomputedMissing,
      categories_with_out_of_scope_evidence: recomputedOutOfScope,
    },
  };
}

async function buildVerifiedReceipt(request, env, submittedReceipt) {
  const { failures, recomputed } = verifyReceiptConsistency(submittedReceipt);
  const edge = edgeMetadata(request, env);

  const verified = {
    verified_receipt_id: crypto.randomUUID(),
    receipt_type: "CATEGORY_DRIFT_VERIFY",
    verifier_runtime: "cloudflare_worker",
    checked_at: new Date().toISOString(),
    submitted_receipt: submittedReceipt,
    recomputed,
    ...edge,
    failures,
  };

  if (!edge.edge_execution_proven || !edge.secondary_account_proven) {
    failures.push("PASS requires secondary-account + edge-execution proof");
  }

  verified.status = failures.length === 0 ? "PASS" : "FAIL";
  verified.result = verified.status;
  return verified;
}

async function writeReceipt(env, receipt) {
  const value = JSON.stringify(receipt, null, 2);
  await env.DRIFT_RECEIPTS.put(`receipt:${receipt.verified_receipt_id}`, value);
  await env.DRIFT_RECEIPTS.put("latest", value);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/category-drift/verify" && request.method === "POST") {
      let submittedReceipt;
      try {
        submittedReceipt = await request.json();
      } catch {
        return jsonResponse({ error: "body must be valid JSON" }, 400);
      }
      const verified = await buildVerifiedReceipt(request, env, submittedReceipt);
      await writeReceipt(env, verified);
      return jsonResponse(verified, verified.status === "PASS" ? 200 : 422);
    }

    if (url.pathname === "/category-drift/latest") {
      const receipt = await env.DRIFT_RECEIPTS.get("latest");
      if (!receipt) return jsonResponse({ error: "no verified receipt yet" }, 404);
      return new Response(receipt, {
        headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
      });
    }

    return jsonResponse({
      service: "category-drift-verifier",
      endpoints: ["/category-drift/verify (POST)", "/category-drift/latest (GET)"],
      note: "Independently re-validates category_registry_drift_check_receipt_v1 receipts. Never trusts the submitting job's own claim.",
    });
  },
};
