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
    "openai",
    reviewPrompt("correctness"),
    payload,
    1500,
  );
  raw.security = await runRole(
    env,
    "security_verifier",
    "gemini",
    reviewPrompt("security"),
    payload,
    1500,
  );
  raw.doctrine = await runRole(
    env,
    "doctrine_verifier",
    "workers_ai",
    reviewPrompt("doctrine"),
    payload,
    1500,
  );
  raw.skeptic = await runRole(
    env,
    "skeptical_critic",
    "glm",
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
  await github(token, `/repos/${owner}/${repo}/pulls/${pr.number}/reviews`, {
    method: "POST",
    body: JSON.stringify({ event: "COMMENT", body: rendered.body }),
  });
  try {
    await github(token, `/repos/${owner}/${repo}/issues/${pr.number}/labels`, {
      method: "POST",
      body: JSON.stringify({
        labels: [
          rendered.pass ? "ai-circle-reviewed" : "ai-circle-changes-requested",
          "independent-machine-review",
        ],
      }),
    });
  } catch {
    // The review comment is canonical; labels are optional routing metadata.
  }
  // Closed-loop repair signal only — verifier never edits the PR.
  if (!rendered.pass) {
    try {
      await github(token, `/repos/${owner}/${repo}/issues/${pr.number}/comments`, {
        method: "POST",
        body: JSON.stringify({
          body:
            `## Independent repair request\n\n` +
            `Exact head \`${pr.head.sha}\` requires a **new** \`ai-circle/*\` draft (do not push over this head).\n` +
            `Builder circle must open a bounded repair draft addressing the findings above.\n` +
            `HOLD preserved. Verifier cannot edit, approve, merge, or deploy.\n` +
            `Receipt: \`${receiptId}\``,
        }),
      });
    } catch {
      // Review comment remains the canonical signal.
    }
  }
  return {
    pr_number: pr.number,
    pr_url: pr.html_url,
    head_sha: pr.head.sha,
    verdict: rendered.pass ? "PASS_ADVISORY" : "REQUEST_CHANGES",
    deterministic,
    provider_diversity: rendered.provider_diversity,
    model: model.normalized,
    repair_requested: !rendered.pass,
  };
}

async function persist(env, receipt) {
  if (!env.RECEIPTS) return;
  await env.RECEIPTS.put(`tick:${receipt.at}`, JSON.stringify(receipt), {
    expirationTtl: 60 * 60 * 24 * 30,
  });
  await env.RECEIPTS.put("last_fired_at", receipt.at);
  await env.RECEIPTS.put("last_receipt", JSON.stringify(receipt));
  for (const review of receipt.reviews || []) {
    await env.RECEIPTS.put(`reviewed:${review.pr_number}`, review.head_sha);
  }
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
      reviews.push(await reviewPull(token, owner, repo, pr, env, receiptId));
    }
    const receipt = {
      schema: SCHEMA,
      receipt_id: receiptId,
      loop_id: env.LOOP_ID || SCHEMA,
      at,
      source: meta.source || "cf-cron",
      cron: meta.cron || "30 * * * *",
      mode: "INDEPENDENT_REVIEW_ONLY",
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
      mode: "INDEPENDENT_REVIEW_ONLY",
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
      const last = env.RECEIPTS ? await env.RECEIPTS.get("last_fired_at") : null;
      return json({
        ok: true,
        schema: `${SCHEMA}-health`,
        loop_id: env.LOOP_ID || SCHEMA,
        cron: "30 * * * *",
        last_fired_at: last,
        mode: "INDEPENDENT_REVIEW_ONLY",
        hold: "HOLD",
        can_edit: false,
        can_merge: false,
        execution_runtime: "cloudflare_cron_secondary_account",
        live_activation_authorized: String(env.LIVE_ACTIVATION || "") === "true",
        model_keys_present: {
          openai: Boolean((env.VERIFIER_OPENAI_API_KEY || env.OPENAI_API_KEY || "").trim()),
          gemini: Boolean((env.VERIFIER_GEMINI_API_KEY || env.GEMINI_API_KEY || "").trim()),
          glm: Boolean((env.GLM_API_KEY || "").trim()),
          workers_ai: Boolean(env.AI),
          verifier_github_app: Boolean(
            (env.VERIFIER_GITHUB_APP_PRIVATE_KEY || env.SG_CANDIDATE_APP_PRIVATE_KEY || "").trim(),
          ),
        },
      });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const provided = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
      if (!(await secretMatches(provided, env.TICK_SECRET))) return json({ ok: false }, 401);
      const receipt = await runVerifierTick(env, { source: "authenticated_http_tick" });
      return json(receipt, String(receipt.verdict || "").startsWith("FAIL") ? 500 : 200);
    }
    if (url.pathname === "/last" && env.RECEIPTS) {
      const raw = await env.RECEIPTS.get("last_receipt");
      return json(raw ? JSON.parse(raw) : { ok: false, error: "no_receipt_yet" });
    }
    if (url.pathname === "/map") return json(circleMap);
    return json({ ok: false, error: "not_found" }, 404);
  },
};
