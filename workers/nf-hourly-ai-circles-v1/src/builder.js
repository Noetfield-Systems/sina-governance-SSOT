import { WorkflowEntrypoint } from "cloudflare:workers";
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
import {
  buildProductionJobContract,
  productionJobBody,
} from "./jobs.js";
import { normalizeAction, safePath, validateAction } from "./policy.js";

const SCHEMA = "nf-hourly-builder-circle-v1";

function repoParts(env) {
  const [owner, repo] = String(
    env.TARGET_REPO || "Noetfield-Systems/sina-governance-SSOT",
  ).split("/");
  if (!owner || !repo) throw new Error("TARGET_REPO_invalid");
  return { owner, repo };
}

async function fetchVerifierFeedback(env) {
  const url = String(env.VERIFIER_LAST_URL || "").trim() ||
    String(env.VERIFIER_HEALTH_URL || "").replace(/\/health$/, "/last");
  if (!url) return { ok: false, reason: "verifier_last_url_missing" };
  try {
    const resp = await fetch(url, {
      signal: AbortSignal.timeout(10_000),
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${env.PEER_TICK_SECRET || ""}`,
        "User-Agent": SCHEMA,
      },
    });
    const body = await resp.json();
    const reviews = body.reviews || [];
    return {
      ok: resp.ok,
      at: body.at || null,
      verdict: body.verdict || null,
      reviews: reviews.map((review) => ({
        pr_number: review.pr_number,
        head_sha: review.head_sha,
        verdict: review.verdict,
        review_channel: review.review_channel,
        review_body: review.review_body || null,
        github_delivery: review.github_delivery || [],
        findings: review.deterministic?.findings || [],
      })),
      repairs: reviews
        .filter((review) => review.verdict === "REQUEST_CHANGES")
        .map((review) => ({
          pr_number: review.pr_number,
          head_sha: review.head_sha,
          review_channel: review.review_channel,
          findings: review.deterministic?.findings || [],
        })),
    };
  } catch (error) {
    return { ok: false, reason: String(error?.message || error) };
  }
}

async function snapshot(token, owner, repo, env) {
  const [metadata, commits, issues, pulls, tree, verifierFeedback] = await Promise.all([
    github(token, `/repos/${owner}/${repo}`),
    github(token, `/repos/${owner}/${repo}/commits?per_page=8`),
    github(token, `/repos/${owner}/${repo}/issues?state=open&per_page=15&sort=updated`),
    github(token, `/repos/${owner}/${repo}/pulls?state=open&per_page=15&sort=updated`),
    github(token, `/repos/${owner}/${repo}/git/trees/main?recursive=1`),
    fetchVerifierFeedback(env),
  ]);
  const openPrs = pulls.map((item) => ({
    number: item.number,
    title: item.title,
    draft: item.draft,
    head: item.head?.ref,
  }));
  return {
    repo: metadata.full_name,
    description: metadata.description,
    default_branch: metadata.default_branch,
    pushed_at: metadata.pushed_at,
    recent_commits: commits.map((item) => ({
      sha: item.sha.slice(0, 12),
      message: clip(item.commit?.message || "", 180),
    })),
    open_issues: issues
      .filter((item) => !item.pull_request)
      .map((item) => ({ number: item.number, title: item.title, labels: item.labels?.map((x) => x.name) })),
    open_prs: openPrs,
    open_ai_circle_prs: openPrs.filter((pr) => {
      const head = String(pr.head || "");
      return head.startsWith("ai-circle/") || head.startsWith("production-job/");
    }),
    verifier_feedback: verifierFeedback,
    production_job_kind: "repository_patch",
    candidate_paths: (tree.tree || [])
      .filter((item) => item.type === "blob" && safePath(item.path))
      .map((item) => item.path)
      .slice(0, 350),
  };
}

async function readTarget(token, owner, repo, branch, path) {
  if (!safePath(path)) return { path: null, content: null, reason: "unsafe_or_missing_target" };
  try {
    const file = await github(
      token,
      `/repos/${owner}/${repo}/contents/${encodeURIComponent(path)}?ref=${encodeURIComponent(branch)}`,
    );
    if (file.encoding !== "base64" || Number(file.size || 0) > 24000) {
      return { path, content: null, reason: "file_too_large_or_not_text" };
    }
    const raw = atob(file.content.replace(/\n/g, ""));
    const bytes = Uint8Array.from(raw, (character) => character.charCodeAt(0));
    return { path, content: new TextDecoder().decode(bytes) };
  } catch (error) {
    return { path, content: null, reason: String(error?.message || error) };
  }
}

function rolePrompt(role) {
  const common =
    "You are in the Noetfield production repository-job builder. Evidence beats confidence. " +
    "Rank portfolio value by ECQR. Preserve CAT_07 and Data HOLD. Do not package operations as product SKUs. " +
    "For media supply, prefer qualified gallery reuse, then deterministic composition, then paid generation only when required. " +
    "Execute only real repository work under AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD. " +
    "Never merge, deploy, alter authority/secrets/workflows/locked architecture, or claim ratification. " +
    "Never emit demos, fixtures, placeholders, sample jobs, planning artifacts, or issue-only work. " +
    "The only external action is a draft_pr containing an actual bounded repair or improvement with executable acceptance checks.";
  const prompts = {
    scout: `${common} Find one concrete, evidenced production defect or momentum opportunity in candidate_paths. Return JSON only: {"target_path":string|null,"problem":string,"evidence":[string],"value":"revenue|risk|reliability|velocity","recommended_action":"draft_pr|noop"}.`,
    researcher: `${common} Independently investigate the supplied snapshot and scout claim. Seek contradictory evidence and expansion/revenue value. Return JSON only: {"facts":[string],"contradictions":[string],"search_next":[string],"recommendation":string}.`,
    critic: `${common} Attack the proposal. Identify duplication, stale assumptions, protected-surface risk, and work that merely creates governance theater. Return JSON only: {"fatal":[string],"nonfatal":[string],"minimum_real_work":string,"verifier_checks":[string]}.`,
    frugal: `${common} Find the smallest production change with measurable proof. Return JSON only: {"different_view":string,"smaller_change":string,"proof":string}.`,
    planner: `${common} Reconcile evidence without hiding disagreement. Select one safe target already present in candidate_paths. Return JSON only: {"action":"draft_pr|noop","target_path":string|null,"title":string,"why":string,"acceptance":[string],"unresolved_objections":[string]}.`,
    implementer:
      `${common} Produce one bounded production patch with complete UTF-8 file contents (max 3 safe files; include or update executable tests for code). ` +
      `Every tests entry must be an executable shell command beginning with python, pytest, node, npm, npx, bash, or sh. ` +
      `Never replace an existing file with empty/minimal content. Do not edit protected paths. Use noop if evidence is insufficient or no production patch is safe. ` +
      `Return JSON only: {"action":"draft_pr|noop","title":string,"rationale":string,"changes":[{"path":string,"content":string}],"tests":[string]}.`,
  };
  return prompts[role];
}

async function runCircle(env, repoSnapshot, token, owner, repo) {
  const transcript = {};
  transcript.scout = await runRole(
    env,
    "scout",
    "workers_ai_fast",
    rolePrompt("scout"),
    JSON.stringify(repoSnapshot),
  );
  transcript.researcher = await runRole(
    env,
    "researcher",
    "workers_ai_fast",
    rolePrompt("researcher"),
    JSON.stringify({ snapshot: repoSnapshot, scout: transcript.scout.content }),
  );
  transcript.critic = await runRole(
    env,
    "critic",
    "workers_ai_fast",
    rolePrompt("critic"),
    JSON.stringify({
      snapshot: repoSnapshot,
      scout: transcript.scout.content,
      researcher: transcript.researcher.content,
    }),
  );
  transcript.frugal = await runRole(
    env,
    "frugal_divergence",
    "workers_ai_fast",
    rolePrompt("frugal"),
    JSON.stringify({
      scout: transcript.scout.content,
      researcher: transcript.researcher.content,
      critic: transcript.critic.content,
    }),
  );
  transcript.planner = await runRole(
    env,
    "planner",
    "workers_ai_reasoning",
    rolePrompt("planner"),
    JSON.stringify({ snapshot: repoSnapshot, transcript }),
    1100,
  );
  const planner = parseModelJson(transcript.planner.content) || {};
  const target = await readTarget(
    token,
    owner,
    repo,
    repoSnapshot.default_branch,
    planner.target_path,
  );
  transcript.implementer = await runRole(
    env,
    "implementer",
    "workers_ai_reasoning",
    rolePrompt("implementer"),
    JSON.stringify({
      snapshot: repoSnapshot,
      transcript,
      selected_target: target,
      verifier_feedback: repoSnapshot.verifier_feedback,
      preference: "Production repository patch only. No demos, fixtures, placeholders, issues, or external synthetic workflows.",
    }),
    8000,
  );
  const quorum = Object.values(transcript).filter((result) => result.ok).length;
  const providerDiversity = new Set(
    Object.values(transcript).filter((result) => result.ok).map((result) => result.provider),
  ).size;
  const rawAction =
    quorum >= Number(env.MIN_ROLE_QUORUM || 4) &&
    providerDiversity >= Number(env.MIN_PROVIDER_DIVERSITY || 3)
      ? parseModelJson(transcript.implementer.content)
      : { action: "noop", rationale: "role_or_provider_diversity_quorum_not_met" };
  return {
    transcript,
    quorum,
    providerDiversity,
    target,
    planner,
    action: normalizeAction(rawAction, planner),
  };
}

async function createDraftPr(token, owner, repo, base, action, receiptId) {
  const branch = `production-job/${receiptId.replace(/[^a-zA-Z0-9._-]/g, "-")}`;
  try {
    const existingRef = await github(
      token,
      `/repos/${owner}/${repo}/git/ref/heads/${encodeURIComponent(branch)}`,
    );
    const pulls = await github(
      token,
      `/repos/${owner}/${repo}/pulls?state=open&head=${encodeURIComponent(`${owner}:${branch}`)}`,
    );
    return {
      kind: "draft_pr",
      reused: true,
      number: pulls[0]?.number || null,
      url: pulls[0]?.html_url || null,
      branch,
      head_sha: existingRef.object.sha,
    };
  } catch (error) {
    if (!String(error?.message || error).startsWith("github_404:")) throw error;
  }
  for (const change of action.changes) {
    const existing = await readTarget(token, owner, repo, base, change.path);
    if (
      existing.content &&
      existing.content.length >= 100 &&
      change.content.length < existing.content.length * 0.5
    ) {
      return {
        kind: "noop",
        reason: `suspicious_file_truncation:${change.path}`,
      };
    }
  }
  const baseRef = await github(token, `/repos/${owner}/${repo}/git/ref/heads/${base}`);
  const baseCommit = await github(token, `/repos/${owner}/${repo}/git/commits/${baseRef.object.sha}`);
  const treeEntries = [];
  for (const change of action.changes) {
    const blob = await github(token, `/repos/${owner}/${repo}/git/blobs`, {
      method: "POST",
      body: JSON.stringify({ content: change.content, encoding: "utf-8" }),
    });
    treeEntries.push({ path: change.path, mode: "100644", type: "blob", sha: blob.sha });
  }
  const tree = await github(token, `/repos/${owner}/${repo}/git/trees`, {
    method: "POST",
    body: JSON.stringify({ base_tree: baseCommit.tree.sha, tree: treeEntries }),
  });
  if (tree.sha === baseCommit.tree.sha) {
    return { kind: "noop", reason: "no_effective_repository_change" };
  }
  const contract = buildProductionJobContract({
    receiptId,
    repo: `${owner}/${repo}`,
    base,
    baseSha: baseRef.object.sha,
    action,
  });
  const commit = await github(token, `/repos/${owner}/${repo}/git/commits`, {
    method: "POST",
    body: JSON.stringify({
      message: `ai-circle: ${clip(action.title || "bounded improvement", 120)}`,
      tree: tree.sha,
      parents: [baseRef.object.sha],
    }),
  });
  await github(token, `/repos/${owner}/${repo}/git/refs`, {
    method: "POST",
    body: JSON.stringify({ ref: `refs/heads/${branch}`, sha: commit.sha }),
  });
  const pull = await github(token, `/repos/${owner}/${repo}/pulls`, {
    method: "POST",
    body: JSON.stringify({
      title: clip(action.title || "Hourly AI circle candidate", 180),
      head: branch,
      base,
      draft: true,
      body: productionJobBody(contract),
    }),
  });
  try {
    await github(token, `/repos/${owner}/${repo}/issues/${pull.number}/labels`, {
      method: "POST",
      body: JSON.stringify({
        labels: ["ai-circle-candidate", "production-job", "independent-review-required"],
      }),
    });
  } catch {
    // Branch namespace remains the machine-readable candidate marker when labels are absent.
  }
  return {
    kind: "draft_pr",
    number: pull.number,
    url: pull.html_url,
    branch,
    head_sha: commit.sha,
    exact_base_sha: baseRef.object.sha,
    job_contract: contract,
  };
}

async function persist(env, receipt) {
  if (!env.RECEIPTS) return;
  await env.RECEIPTS.put(`tick:${receipt.at}`, JSON.stringify(receipt), {
    expirationTtl: 60 * 60 * 24 * 30,
  });
  await env.RECEIPTS.put("last_fired_at", receipt.at);
  await env.RECEIPTS.put("last_receipt", JSON.stringify(receipt));
  if (receipt.receipt_id) {
    await env.RECEIPTS.put(`job:${receipt.receipt_id}`, JSON.stringify({
      job_id: receipt.receipt_id,
      state: receipt.delivery?.kind === "draft_pr" ? "DRAFT_PR_OPENED" : receipt.verdict,
      exact_head_sha: receipt.delivery?.head_sha || null,
      pr_number: receipt.delivery?.number || null,
      updated_at: receipt.at,
    }), { expirationTtl: 60 * 60 * 24 * 90 });
  }
}

async function claimTickLease(env, receiptId) {
  if (!env.RECEIPTS) return { claimed: true, reason: "ledger_unavailable" };
  const current = await env.RECEIPTS.get("active_tick", "json");
  if (current?.expires_at && Date.parse(current.expires_at) > Date.now()) {
    return { claimed: false, active: current };
  }
  const expiresAt = new Date(Date.now() + 30 * 60 * 1000).toISOString();
  await env.RECEIPTS.put(
    "active_tick",
    JSON.stringify({ receipt_id: receiptId, expires_at: expiresAt }),
    { expirationTtl: 30 * 60 },
  );
  return { claimed: true, expires_at: expiresAt };
}

async function releaseTickLease(env, receiptId) {
  if (!env.RECEIPTS) return;
  const current = await env.RECEIPTS.get("active_tick", "json");
  if (current?.receipt_id === receiptId) await env.RECEIPTS.delete("active_tick");
}

async function deliverProductionJob({
  token,
  owner,
  repo,
  base,
  action,
  receiptId,
}) {
  const validated = validateAction(action);
  if (!validated.ok) {
    return {
      delivery: { kind: "noop", reason: validated.reason },
      validated,
    };
  }
  if (action.action !== "draft_pr") {
    return {
      delivery: { kind: "noop", reason: action.rationale || "no_production_patch" },
      validated,
    };
  }
  return {
    delivery: await createDraftPr(token, owner, repo, base, action, receiptId),
    validated,
  };
}

export async function runBuilderTick(env, meta = {}) {
  const at = new Date().toISOString();
  const executionId = String(meta.instance_id || crypto.randomUUID())
    .replace(/[^a-zA-Z0-9]/g, "")
    .slice(0, 24);
  const receiptId = `builder-${executionId}`;
  const peer = await checkPeerAndRestart(env, env.VERIFIER_HEALTH_URL, env.VERIFIER_TICK_URL);
  const lease = await claimTickLease(env, receiptId);
  if (!lease.claimed) {
    return {
      schema: SCHEMA,
      receipt_id: receiptId,
      at,
      mode: "PRODUCTION_REPOSITORY_JOBS_HOLD",
      hold: "HOLD",
      verdict: "SKIP_DUPLICATE_TICK",
      active_tick: lease.active,
    };
  }
  try {
    const { owner, repo } = repoParts(env);
    const token = await mintInstallationToken(env, "builder");
    const repoSnapshot = await snapshot(token, owner, repo, env);
    const openCandidateNumbers = new Set(
      (repoSnapshot.open_ai_circle_prs || []).map((pr) => pr.number),
    );
    const actionableRepairs = (repoSnapshot.verifier_feedback?.repairs || [])
      .filter((repair) => openCandidateNumbers.has(repair.pr_number));
    const maxOpenCandidates = Number(env.MAX_OPEN_CANDIDATES || 2);
    if (
      openCandidateNumbers.size >= maxOpenCandidates ||
      (openCandidateNumbers.size > 0 && actionableRepairs.length === 0)
    ) {
      const receipt = {
        schema: SCHEMA,
        receipt_id: receiptId,
        loop_id: env.LOOP_ID || SCHEMA,
        at,
        source: meta.source || "cf-cron",
        cron: meta.cron || "0 * * * *",
        mode: "PRODUCTION_REPOSITORY_JOBS_HOLD",
        hold: "HOLD",
        peer_deadman: peer,
        open_candidates: [...openCandidateNumbers],
        actionable_repairs: actionableRepairs,
        verdict: openCandidateNumbers.size >= maxOpenCandidates
          ? "WAIT_WIP_CAP"
          : "WAIT_INDEPENDENT_VERIFICATION",
      };
      await persist(env, receipt);
      await releaseTickLease(env, receiptId);
      return receipt;
    }
    const circle = await runCircle(env, repoSnapshot, token, owner, repo);
    const delivered = await deliverProductionJob({
      token,
      owner,
      repo,
      base: repoSnapshot.default_branch,
      action: circle.action,
      receiptId,
    });
    const delivery = delivered.delivery;
    const receipt = {
      schema: SCHEMA,
      receipt_id: receiptId,
      loop_id: env.LOOP_ID || SCHEMA,
      at,
      source: meta.source || "cf-cron",
      cron: meta.cron || "0 * * * *",
      mode: "PRODUCTION_REPOSITORY_JOBS_HOLD",
      hold: "HOLD",
      peer_deadman: peer,
      snapshot: {
        repo: repoSnapshot.repo,
        pushed_at: repoSnapshot.pushed_at,
        open_ai_circle_prs: (repoSnapshot.open_ai_circle_prs || []).length,
      },
      role_results: Object.fromEntries(
        Object.entries(circle.transcript).map(([name, result]) => [
          name,
          {
            ok: result.ok,
            provider: result.provider,
            content: clip(result.content, 2400),
            errors: result.ok ? [] : (result.errors || []).slice(0, 8),
          },
        ]),
      ),
      role_quorum: circle.quorum,
      provider_diversity: circle.providerDiversity,
      planner: circle.planner,
      action_validation: delivered.validated,
      delivery,
      verifier_feedback: repoSnapshot.verifier_feedback,
      verdict: delivery?.kind === "draft_pr"
        ? "PASS_PRODUCTION_DRAFT_JOB"
        : circle.quorum < Number(env.MIN_ROLE_QUORUM || 4)
          ? "DEGRADED_MODEL_RUNTIME"
          : "PASS_NO_SAFE_PRODUCTION_ACTION",
    };
    await persist(env, receipt);
    await releaseTickLease(env, receiptId);
    return receipt;
  } catch (error) {
    const receipt = {
      schema: SCHEMA,
      receipt_id: receiptId,
      loop_id: env.LOOP_ID || SCHEMA,
      at,
      source: meta.source || "cf-cron",
      mode: "PRODUCTION_REPOSITORY_JOBS_HOLD",
      hold: "HOLD",
      peer_deadman: peer,
      verdict: "FAIL_SCOPED_TICK",
      error: String(error?.message || error),
    };
    await persist(env, receipt);
    await releaseTickLease(env, receiptId);
    return receipt;
  }
}

export class BuilderCircleWorkflow extends WorkflowEntrypoint {
  async run(event, step) {
    return step.do(
      "bounded builder circle",
      { timeout: "20 minutes", retries: { limit: 2, delay: "30 seconds", backoff: "exponential" } },
      async () =>
        runBuilderTick(this.env, {
          source: event.schedule ? "workflow_schedule" : event.payload?.source || "workflow_api",
          cron: event.schedule?.cron || "0 * * * *",
          instance_id: event.instanceId,
        }),
    );
  }
}

async function requestAuthorized(request, env) {
  const provided = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  return secretMatches(provided, env.TICK_SECRET);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      const last = env.RECEIPTS ? await env.RECEIPTS.get("last_fired_at") : null;
      const raw = env.RECEIPTS ? await env.RECEIPTS.get("last_receipt") : null;
      const lastReceipt = raw ? JSON.parse(raw) : null;
      return json({
        ok: true,
        schema: `${SCHEMA}-health`,
        loop_id: env.LOOP_ID || SCHEMA,
        cron: "0 * * * *",
        last_fired_at: last,
        last_verdict: lastReceipt?.verdict || null,
        mode: "PRODUCTION_REPOSITORY_JOBS_HOLD",
        hold: "HOLD",
        execution_runtime: "cloudflare_workflows",
        workflow_name: env.WORKFLOW_NAME || "nf-hourly-production-repository-jobs-v2",
        production_phase: true,
        production_job_kind: "repository_patch",
        commissioned: false,
        version_id: env.CF_VERSION_METADATA?.id || null,
      });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      if (!(await requestAuthorized(request, env))) return json({ ok: false }, 401);
      const instance = await env.BUILDER_WORKFLOW.create({
        params: { source: "authenticated_http_tick" },
      });
      return json({ accepted: true, workflow_instance_id: instance.id }, 202);
    }
    if (url.pathname === "/status" && url.searchParams.get("id")) {
      if (!(await requestAuthorized(request, env))) return json({ ok: false }, 401);
      const instance = await env.BUILDER_WORKFLOW.get(url.searchParams.get("id"));
      return json({ id: instance.id, status: await instance.status() });
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
    if (url.pathname === "/jobs") {
      if (!(await requestAuthorized(request, env))) return json({ ok: false }, 401);
      return json({
        schema: `${SCHEMA}-jobs`,
        job_kind: "repository_patch",
        mutation_boundary: "draft_pr_only",
      });
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
