import circleMap from "./circle-map.json" with { type: "json" };
import {
  checkPeerAndRestart,
  clip,
  github,
  json,
  mintInstallationToken,
  parseModelJson,
  runRole,
  secretMatches,
} from "./common.js";
import { deterministicReview } from "./policy.js";

const SCHEMA = "nf-hourly-independent-verifier-circle-v1";

function repoParts(env) {
  const [owner, repo] = String(
    env.TARGET_REPO || "Noetfield-Systems/sina-governance-SSOT",
  ).split("/");
  if (!owner || !repo) throw new Error("TARGET_REPO_invalid");
  return { owner, repo };
}

function reviewPrompt(role) {
  const boundary =
    "You are in an independent verifier runtime. You receive only the actual PR metadata, diff, and checks—never the builder's private reasoning. " +
    "You cannot edit, merge, deploy, approve, or ratify. Find concrete defects; do not reward confidence or consensus.";
  const prompts = {
    correctness:
      `${boundary} Review behavior, edge cases, tests, and whether the patch actually solves its stated problem. ` +
      `Return JSON only: {"verdict":"PASS_ADVISORY|REQUEST_CHANGES","findings":[{"severity":"P0|P1|P2|P3","file":string|null,"problem":string,"required_fix":string}],"missing_tests":[string]}.`,
    security:
      `${boundary} Review for secrets, authority bypass, prompt injection, unsafe network/GitHub operations, supply-chain risk, and privilege expansion. ` +
      `Return the same JSON shape with verdict and findings.`,
    doctrine:
      `${boundary} Review against HOLD, author-not-subject, protected surfaces, bounded roles, no unsupervised architecture redesign, and no docs-only theater. ` +
      `Return the same JSON shape with verdict and findings.`,
    skeptic:
      `${boundary} Assume the other reviewers missed the strongest objection. Stress-test evidence and identify false claims or hidden regressions. ` +
      `Return the same JSON shape with verdict and findings.`,
  };
  return prompts[role];
}

function normalizeModelVerdict(result) {
  if (!result.ok) return { verdict: "UNAVAILABLE", findings: [], provider: null };
  const parsed = parseModelJson(result.content);
  if (!parsed || !["PASS_ADVISORY", "REQUEST_CHANGES"].includes(parsed.verdict)) {
    return {
      verdict: "REQUEST_CHANGES",
      findings: [{ severity: "P2", problem: "reviewer_returned_invalid_schema", required_fix: "rerun review" }],
      provider: result.provider,
    };
  }
  return {
    verdict: parsed.verdict,
    findings: Array.isArray(parsed.findings) ? parsed.findings.slice(0, 12) : [],
    missing_tests: Array.isArray(parsed.missing_tests) ? parsed.missing_tests.slice(0, 12) : [],
    provider: result.provider,
  };
}

async function modelReview(env, payload) {
  const raw = {};
  raw.correctness = await runRole(
    env,
    "correctness_verifier",
    "workers_ai_reasoning",
    reviewPrompt("correctness"),
    payload,
    1500,
  );
  raw.security = await runRole(
    env,
    "security_verifier",
    "workers_ai_fast",
    reviewPrompt("security"),
    payload,
    1500,
  );
  raw.doctrine = await runRole(
    env,
    "doctrine_verifier",
    "workers_ai_fast",
    reviewPrompt("doctrine"),
    payload,
    1500,
  );
  raw.skeptic = await runRole(
    env,
    "skeptical_critic",
    "workers_ai_reasoning",
    reviewPrompt("skeptic"),
    payload,
    1500,
  );
  return {
    raw,
    normalized: Object.fromEntries(
      Object.entries(raw).map(([role, result]) => [role, normalizeModelVerdict(result)]),
    ),
  };
}

function renderReview(deterministic, model, receiptId, headSha) {
  const modelEntries = Object.entries(model.normalized);
  const available = modelEntries.filter(([, result]) => result.verdict !== "UNAVAILABLE");
  const requests = available.filter(([, result]) => result.verdict === "REQUEST_CHANGES");
  const providerDiversity = new Set(available.map(([, result]) => result.provider)).size;
  const pass =
    deterministic.pass &&
    available.length >= 2 &&
    providerDiversity >= 2 &&
    requests.length === 0;
  const lines = [
    "## Independent machine verification",
    "",
    `**Verdict:** \`${pass ? "PASS_ADVISORY" : "REQUEST_CHANGES"}\``,
    `**Exact head:** \`${headSha}\``,
    `**Receipt:** \`${receiptId}\``,
    "",
    "This verdict was produced by a separate runtime and KV ledger using only the PR diff and checks. It is not merge approval or SG ratification.",
    "",
    "### Deterministic gate",
    deterministic.findings.length
      ? deterministic.findings.map((item) => `- ${item}`).join("\n")
      : "- PASS: bounded diff, reviewable paths, and no observed failing checks.",
    "",
    "### Independent critics",
  ];
  for (const [role, result] of modelEntries) {
    lines.push(`- **${role}** (${result.provider || "unavailable"}): \`${result.verdict}\``);
    for (const finding of result.findings || []) {
      lines.push(
        `  - ${finding.severity || "P2"}${finding.file ? ` \`${finding.file}\`` : ""}: ` +
          `${finding.problem || "unspecified"} — ${finding.required_fix || "fix required"}`,
      );
    }
  }
  lines.push("", "### Machine boundary", "- No edit", "- No approve", "- No merge", "- No deploy");
  return {
    pass,
    body: clip(lines.join("\n"), 60000),
    available: available.length,
    provider_diversity: providerDiversity,
    requests: requests.length,
  };
}

async function reviewPull(token, owner, repo, pr, env, receiptId) {
  const [files, checks] = await Promise.all([
    github(token, `/repos/${owner}/${repo}/pulls/${pr.number}/files?per_page=100`),
    github(token, `/repos/${owner}/${repo}/commits/${pr.head.sha}/check-runs?per_page=100`),
  ]);
  const externalChecks = (checks.check_runs || [])
    .filter((check) => check.name !== "Noetfield Independent Production Verification");
  if (
    externalChecks.length === 0 ||
    externalChecks.some((check) => check.status !== "completed")
  ) {
    return {
      deferred: true,
      pr_number: pr.number,
      head_sha: pr.head.sha,
      reason: externalChecks.length === 0 ? "waiting_for_ci" : "ci_in_progress",
      checks_seen: externalChecks.map((check) => ({
        name: check.name,
        status: check.status,
        conclusion: check.conclusion,
      })),
    };
  }
  const deterministic = deterministicReview(pr, files, checks);
  const reviewPayload = clip(
    JSON.stringify({
      pr: {
        number: pr.number,
        title: pr.title,
        body: pr.body,
        draft: pr.draft,
        base: pr.base?.ref,
        head: pr.head?.ref,
        head_sha: pr.head?.sha,
      },
      deterministic,
      files: files.map((file) => ({
        filename: file.filename,
        status: file.status,
        additions: file.additions,
        deletions: file.deletions,
        patch: clip(file.patch || "", 10000),
      })),
    }),
    48000,
  );
  const model = await modelReview(env, reviewPayload);
  const rendered = renderReview(deterministic, model, receiptId, pr.head.sha);
  const check = await github(token, `/repos/${owner}/${repo}/check-runs`, {
    method: "POST",
    body: JSON.stringify({
      name: "Noetfield Independent Production Verification",
      head_sha: pr.head.sha,
      status: "completed",
      conclusion: rendered.pass ? "success" : "failure",
      output: {
        title: rendered.pass
          ? "Production verification passed"
          : "Production verification requires changes",
        summary: clip(rendered.body, 65000),
      },
    }),
  });
  const checkFingerprint = externalChecks
    .map((item) => `${item.name}:${item.status}:${item.conclusion || ""}`)
    .sort()
    .join("|");
  return {
    pr_number: pr.number,
    pr_url: pr.html_url,
    head_sha: pr.head.sha,
    verdict: rendered.pass ? "PASS_ADVISORY" : "REQUEST_CHANGES",
    deterministic,
    provider_diversity: rendered.provider_diversity,
    model: model.normalized,
    repair_requested: !rendered.pass,
    review_channel: "github_check_run",
    review_body: rendered.body,
    github_check_run: {
      id: check.id,
      url: check.html_url,
      conclusion: check.conclusion,
    },
    review_fingerprint: `${pr.head.sha}:${checkFingerprint}`,
  };
}

/** In-isolate last tick time for /health. Avoids KV on every health poll. */
let memLastFiredAt = null;

async function persist(env, receipt) {
  if (!env.RECEIPTS) return;
  // KV free-tier: no tick:${at} history key; keep last_fired_at + last_receipt
  // (+ reviewed:* only when needed).
  await env.RECEIPTS.put("last_fired_at", receipt.at);
  await env.RECEIPTS.put("last_receipt", JSON.stringify(receipt));
  for (const review of receipt.reviews || []) {
    if (!review.deferred) {
      await env.RECEIPTS.put(`reviewed:${review.pr_number}`, review.head_sha);
    }
  }
  memLastFiredAt = receipt.at;
}

export async function runVerifierTick(env, meta = {}) {
  const at = new Date().toISOString();
  const receiptId = `verifier-${at.replace(/\D/g, "").slice(0, 14)}-${crypto.randomUUID().slice(0, 8)}`;
  const builderDeadman = await checkPeerAndRestart(env, env.BUILDER_HEALTH_URL, env.BUILDER_TICK_URL);
  try {
    const { owner, repo } = repoParts(env);
    const token = await mintInstallationToken(env, "verifier");
    const pulls = await github(token, `/repos/${owner}/${repo}/pulls?state=open&per_page=50`);
    const candidates = pulls.filter(
      (pr) =>
        String(pr.head?.ref || "").startsWith("ai-circle/") ||
        String(pr.head?.ref || "").startsWith("production-job/") ||
        (pr.labels || []).some((label) => label.name === "ai-circle-candidate"),
    );
    const reviews = [];
    const skipped = [];
    for (const pr of candidates.slice(0, Number(env.MAX_PRS_PER_TICK || 3))) {
      const prior = env.RECEIPTS ? await env.RECEIPTS.get(`reviewed:${pr.number}`) : null;
      if (prior === pr.head.sha) {
        skipped.push({ pr_number: pr.number, head_sha: pr.head.sha, reason: "exact_head_already_reviewed" });
        continue;
      }
      const review = await reviewPull(token, owner, repo, pr, env, receiptId);
      if (review.deferred) skipped.push(review);
      else reviews.push(review);
    }
    const receipt = {
      schema: SCHEMA,
      receipt_id: receiptId,
      loop_id: env.LOOP_ID || SCHEMA,
      at,
      source: meta.source || "cf-cron",
      cron: meta.cron || "30 * * * *",
      mode: "PRODUCTION_INDEPENDENT_VERIFICATION_HOLD",
      hold: "HOLD",
      builder_deadman: builderDeadman,
      candidates_seen: candidates.length,
      reviews,
      skipped,
      verdict: reviews.some((review) => review.verdict === "REQUEST_CHANGES")
        ? "PASS_CRITICIZED"
        : "PASS_VERIFIER_TICK",
    };
    await persist(env, receipt);
    return receipt;
  } catch (error) {
    const receipt = {
      schema: SCHEMA,
      receipt_id: receiptId,
      loop_id: env.LOOP_ID || SCHEMA,
      at,
      source: meta.source || "cf-cron",
      mode: "PRODUCTION_INDEPENDENT_VERIFICATION_HOLD",
      hold: "HOLD",
      builder_deadman: builderDeadman,
      reviews: [],
      verdict: "FAIL_VERIFIER_TICK",
      error: String(error?.message || error),
    };
    await persist(env, receipt);
    return receipt;
  }
}

async function requestAuthorized(request, env) {
  const provided = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  return secretMatches(provided, env.TICK_SECRET);
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(
      runVerifierTick(env, { source: "cf-cron", cron: event?.cron || "30 * * * *" }).then(
        (receipt) =>
          console.log(JSON.stringify({ schema: SCHEMA, verdict: receipt.verdict, at: receipt.at })),
      ),
    );
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      // Prefer in-isolate last tick; cold start may KV-read once.
      let last = memLastFiredAt;
      if (!last && env.RECEIPTS) {
        last = await env.RECEIPTS.get("last_fired_at");
        if (last) memLastFiredAt = last;
      }
      return json({
        ok: true,
        schema: `${SCHEMA}-health`,
        loop_id: env.LOOP_ID || SCHEMA,
        cron: "",
        last_fired_at: last,
        mode: "PRODUCTION_INDEPENDENT_VERIFICATION_HOLD",
        hold: "HOLD",
        can_edit: false,
        can_merge: false,
        execution_runtime: "cloudflare_cron_secondary_account",
        production_phase: true,
        delivery: "github_check_run",
        commissioned: false,
        version_id: env.CF_VERSION_METADATA?.id || null,
      });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      if (!(await requestAuthorized(request, env))) return json({ ok: false }, 401);
      const receipt = await runVerifierTick(env, { source: "authenticated_http_tick" });
      return json(receipt, String(receipt.verdict || "").startsWith("FAIL") ? 500 : 200);
    }
    if (url.pathname === "/last" && env.RECEIPTS) {
      if (!(await requestAuthorized(request, env))) return json({ ok: false }, 401);
      const raw = await env.RECEIPTS.get("last_receipt");
      return json(raw ? JSON.parse(raw) : { ok: false, error: "no_receipt_yet" });
    }
    if (url.pathname === "/map") {
      if (!(await requestAuthorized(request, env))) return json({ ok: false }, 401);
      return json(circleMap);
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
