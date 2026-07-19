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
  buildDeterministicJobPlanArtifact,
  dispatchRunwayJob,
  pickRotatingJob,
  resolveJob,
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
    const resp = await fetch(url, { headers: { Accept: "application/json", "User-Agent": SCHEMA } });
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
    open_ai_circle_prs: openPrs.filter((pr) => String(pr.head || "").startsWith("ai-circle/")),
    verifier_feedback: verifierFeedback,
    job_catalog: [
      "motor_job",
      "commissioning_tick",
      "repair_run",
      "live_model_smoke",
    ],
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
    "You are in the Noetfield hourly builder circle. Evidence beats confidence. " +
    "Rank portfolio value by ECQR. Preserve CAT_07 and Data HOLD. Do not package operations as product SKUs. " +
    "For media supply, prefer qualified gallery reuse, then deterministic composition, then paid generation only when required. " +
    "The output is assist-only under AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD. " +
    "Never merge, deploy, alter authority/secrets/workflows/locked architecture, or claim ratification. " +
    "Prefer REAL work: draft_pr with code+tests, or dispatch_job into NOETFIELD-RUNWAY. Prefer issue only when blocked from both.";
  const prompts = {
    scout: `${common} Find one concrete repo problem or momentum opportunity. Return JSON only: {"target_path":string|null,"problem":string,"evidence":[string],"value":"revenue|risk|reliability|velocity","recommended_action":"draft_pr|dispatch_job|issue|noop","job_id":"motor_job|commissioning_tick|repair_run|live_model_smoke"|null}.`,
    researcher: `${common} Independently investigate the supplied snapshot and scout claim. Seek contradictory evidence and expansion/revenue value. Return JSON only: {"facts":[string],"contradictions":[string],"search_next":[string],"recommendation":string,"prefer_job_id":string|null}.`,
    critic: `${common} Attack the proposal. Identify duplication, stale assumptions, protected-surface risk, and work that merely creates governance theater. Return JSON only: {"fatal":[string],"nonfatal":[string],"minimum_real_work":string,"verifier_checks":[string]}.`,
    frugal: `${common} Act as the cheap/free-model divergence role. Find the smallest useful change with measurable proof. Return JSON only: {"different_view":string,"smaller_change":string,"proof":string,"prefer_dispatch_job":boolean}.`,
    planner: `${common} Reconcile evidence without hiding disagreement. Prefer draft_pr on a safe candidate_paths target with tests, else dispatch_job from job_catalog, else issue. Return JSON only: {"action":"draft_pr|dispatch_job|issue|noop","job_id":"motor_job|commissioning_tick|repair_run|live_model_smoke"|null,"target_path":string|null,"title":string,"why":string,"acceptance":[string],"unresolved_objections":[string]}.`,
    implementer:
      `${common} Produce one bounded REAL action. Prefer draft_pr with complete UTF-8 file contents (max 3 safe files, include tests) OR dispatch_job with job_id. ` +
      `Do not edit protected paths. Avoid noop/issue unless both draft_pr and dispatch_job are unsafe. ` +
      `Return JSON only: {"action":"draft_pr|dispatch_job|issue|noop","job_id":string|null,"title":string,"rationale":string,"issue_body":string,"changes":[{"path":string,"content":string}],"tests":[string]}.`,
  };
  return prompts[role];
}

async function runCircle(env, repoSnapshot, token, owner, repo) {
  const transcript = {};
  transcript.scout = await runRole(
    env,
    "scout",
    "deepseek",
    rolePrompt("scout"),
    JSON.stringify(repoSnapshot),
  );
  transcript.researcher = await runRole(
    env,
    "researcher",
    "kimi",
    rolePrompt("researcher"),
    JSON.stringify({ snapshot: repoSnapshot, scout: transcript.scout.content }),
  );
  transcript.critic = await runRole(
    env,
    "critic",
    "glm",
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
    "workers_ai",
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
    "gemini",
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
    "openai",
    rolePrompt("implementer"),
    JSON.stringify({
      snapshot: repoSnapshot,
      transcript,
      selected_target: target,
      preference: "Prefer draft_pr or dispatch_job. Real plans and jobs over issues.",
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

async function createIssue(token, owner, repo, action, receiptId) {
  const title = clip(action.title || "Hourly AI circle proposal", 180);
  const existing = await github(token, `/repos/${owner}/${repo}/issues?state=open&per_page=50`);
  const duplicate = existing.find((item) => item.title === title);
  if (duplicate) return { kind: "issue", reused: true, number: duplicate.number, url: duplicate.html_url };
  const issue = await github(token, `/repos/${owner}/${repo}/issues`, {
    method: "POST",
    body: JSON.stringify({
      title,
      body:
        `${clip(action.issue_body || action.rationale || "", 8000)}\n\n` +
        `---\nGenerated by the bounded hourly builder circle. Receipt: \`${receiptId}\`. ` +
        `This is a proposal, not an SG decision.\n\nMarker: \`ai-circle-proposal\``,
    }),
  });
  return { kind: "issue", reused: false, number: issue.number, url: issue.html_url };
}

async function createDraftPr(token, owner, repo, base, action, receiptId) {
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
  const commit = await github(token, `/repos/${owner}/${repo}/git/commits`, {
    method: "POST",
    body: JSON.stringify({
      message: `ai-circle: ${clip(action.title || "bounded improvement", 120)}`,
      tree: tree.sha,
      parents: [baseRef.object.sha],
    }),
  });
  const stamp = new Date().toISOString().replace(/[-:]/g, "").slice(0, 11);
  const branch = `ai-circle/${stamp}-${commit.sha.slice(0, 8)}`;
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
      body:
        `## Machine proposal\n${clip(action.rationale || "", 5000)}\n\n` +
        `## Proposed checks\n${(action.tests || []).map((item) => `- ${item}`).join("\n") || "- Independent verifier required"}\n\n` +
        `## Authority boundary\n- lane: assist_only\n- motor_id_or_human_gate: cf_nf_hourly_builder_circle_v1\n` +
        `- receipt_id: ${receiptId}\n- HOLD preserved; this PR cannot merge or deploy autonomously.\n` +
        `- A separate verifier runtime must review the exact head SHA.`,
    }),
  });
  try {
    await github(token, `/repos/${owner}/${repo}/issues/${pull.number}/labels`, {
      method: "POST",
      body: JSON.stringify({ labels: ["ai-circle-candidate", "assist-only", "independent-review-required"] }),
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
  };
}

/**
 * Motor is a dumb delivery bus for verifier-computed text when the SG-candidate
 * app lacks Issues/PR write. Judgment remains verifier-owned in KV.
 */
async function publishVerifierReviewsViaMotor(token, owner, repo, verifierFeedback) {
  const published = [];
  for (const review of verifierFeedback?.reviews || []) {
    if (!review.review_body || !review.pr_number) continue;
    if (review.review_channel && review.review_channel !== "kv_receipt_only") continue;
    const marker = `ai-circle-verifier-receipt:${review.head_sha}`;
    try {
      const existing = await github(
        token,
        `/repos/${owner}/${repo}/issues/${review.pr_number}/comments?per_page=30`,
      );
      if ((existing || []).some((comment) => String(comment.body || "").includes(marker))) {
        published.push({ pr_number: review.pr_number, reused: true, marker });
        continue;
      }
      const comment = await github(token, `/repos/${owner}/${repo}/issues/${review.pr_number}/comments`, {
        method: "POST",
        body: JSON.stringify({
          body:
            `${review.review_body}\n\n` +
            `---\nDelivery bus: Motor posted verifier-computed text. ` +
            `Judgment source remains the independent verifier KV receipt.\n` +
            `Marker: \`${marker}\``,
        }),
      });
      published.push({
        pr_number: review.pr_number,
        ok: true,
        comment_id: comment.id,
        marker,
      });
    } catch (error) {
      published.push({
        pr_number: review.pr_number,
        ok: false,
        error: clip(String(error?.message || error), 240),
      });
    }
  }
  return published;
}

async function persist(env, receipt) {
  if (!env.RECEIPTS) return;
  await env.RECEIPTS.put(`tick:${receipt.at}`, JSON.stringify(receipt), {
    expirationTtl: 60 * 60 * 24 * 30,
  });
  await env.RECEIPTS.put("last_fired_at", receipt.at);
  await env.RECEIPTS.put("last_receipt", JSON.stringify(receipt));
  if (receipt.delivery?.job_id) {
    await env.RECEIPTS.put("last_job_id", receipt.delivery.job_id);
  }
}

function preferJobId(action, planner, at) {
  return (
    resolveJob(action?.job_id)?.id ||
    resolveJob(planner?.job_id)?.id ||
    pickRotatingJob(at).id
  );
}

async function deliverRealWork({
  env,
  token,
  owner,
  repo,
  base,
  action,
  planner,
  repoSnapshot,
  receiptId,
  at,
}) {
  const deliveries = [];
  let primary = null;
  let validated = validateAction(action);

  // Prefer draft_pr when models supplied usable patches.
  if (validated.ok && action.action === "draft_pr") {
    primary = await createDraftPr(token, owner, repo, base, action, receiptId);
    deliveries.push(primary);
  } else if (validated.ok && action.action === "dispatch_job") {
    const job = resolveJob(action.job_id);
    primary = await dispatchRunwayJob(token, env, job, { at, receipt_id: receiptId });
    deliveries.push(primary);
  } else if (validated.ok && action.action === "issue") {
    // Issues are last-resort; still fire a companion runway job for real work.
    primary = await createIssue(token, owner, repo, action, receiptId);
    deliveries.push(primary);
    const companion = await dispatchRunwayJob(
      token,
      env,
      preferJobId(action, planner, at),
      { at, receipt_id: receiptId },
    );
    deliveries.push(companion);
    primary = { ...primary, companion_job: companion };
  }

  // If models failed validation, force a real job + deterministic plan draft PR.
  if (!primary || primary.kind === "noop" || primary.ok === false) {
    const jobId = preferJobId(action, planner, at);
    const job = resolveJob(jobId);
    const dispatch = await dispatchRunwayJob(token, env, job, { at, receipt_id: receiptId });
    deliveries.push(dispatch);
    primary = dispatch.ok ? dispatch : primary;

    const alreadyHasAiCirclePr = (repoSnapshot.open_ai_circle_prs || []).length > 0;
    if (!alreadyHasAiCirclePr) {
      const artifact = buildDeterministicJobPlanArtifact(
        job,
        receiptId,
        clip(action?.rationale || planner?.why || validated.reason || "invalid_model_action", 400),
      );
      const artifactValidation = validateAction(artifact);
      if (artifactValidation.ok) {
        const draft = await createDraftPr(token, owner, repo, base, artifact, receiptId);
        deliveries.push(draft);
        if (!primary || primary.ok === false) primary = draft;
        else primary = { ...primary, companion_draft_pr: draft };
      }
    }
  } else if (action.action === "draft_pr") {
    // Companion runway job keeps the closed loop moving even when a draft PR is opened.
    const jobId = preferJobId(action, planner, at);
    const companion = await dispatchRunwayJob(token, env, jobId, { at, receipt_id: receiptId });
    deliveries.push(companion);
    primary = { ...primary, companion_job: companion };
  } else if (action.action === "dispatch_job" && (repoSnapshot.open_ai_circle_prs || []).length === 0) {
    // Ensure verifier always has at least one ai-circle draft to criticize.
    const job = resolveJob(action.job_id) || pickRotatingJob(at);
    const artifact = buildDeterministicJobPlanArtifact(
      job,
      receiptId,
      clip(action.rationale || planner?.why || "dispatch_job without open ai-circle PR", 400),
    );
    if (validateAction(artifact).ok) {
      const draft = await createDraftPr(token, owner, repo, base, artifact, receiptId);
      deliveries.push(draft);
      primary = { ...primary, companion_draft_pr: draft };
    }
  }

  if (!primary) {
    primary = { kind: "noop", reason: validated.reason || action?.rationale || "no_safe_action" };
    deliveries.push(primary);
  }

  return { primary, deliveries, validated };
}

export async function runBuilderTick(env, meta = {}) {
  const at = new Date().toISOString();
  const receiptId = `builder-${at.replace(/\D/g, "").slice(0, 14)}-${crypto.randomUUID().slice(0, 8)}`;
  const peer = await checkPeerAndRestart(env, env.VERIFIER_HEALTH_URL, env.VERIFIER_TICK_URL);
  try {
    const { owner, repo } = repoParts(env);
    const token = await mintInstallationToken(env, "builder");
    const repoSnapshot = await snapshot(token, owner, repo, env);
    const circle = await runCircle(env, repoSnapshot, token, owner, repo);
    const verifierPublish = await publishVerifierReviewsViaMotor(
      token,
      owner,
      repo,
      repoSnapshot.verifier_feedback,
    );
    const delivered = await deliverRealWork({
      env,
      token,
      owner,
      repo,
      base: repoSnapshot.default_branch,
      action: circle.action,
      planner: circle.planner,
      repoSnapshot,
      receiptId,
      at,
    });
    const delivery = delivered.primary;
    const realWork =
      delivery?.kind === "draft_pr" ||
      delivery?.kind === "dispatch_job" ||
      delivery?.companion_draft_pr ||
      delivery?.companion_job?.ok;
    const receipt = {
      schema: SCHEMA,
      receipt_id: receiptId,
      loop_id: env.LOOP_ID || SCHEMA,
      at,
      source: meta.source || "cf-cron",
      cron: meta.cron || "0 * * * *",
      mode: "ASSIST_ONLY",
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
          { ok: result.ok, provider: result.provider, content: clip(result.content, 2400) },
        ]),
      ),
      role_quorum: circle.quorum,
      provider_diversity: circle.providerDiversity,
      planner: circle.planner,
      action_validation: delivered.validated,
      delivery,
      deliveries: delivered.deliveries,
      verifier_feedback: repoSnapshot.verifier_feedback,
      verifier_publish: verifierPublish,
      verdict: realWork
        ? "PASS_ASSIST_ONLY_DELIVERY"
        : delivery?.kind === "issue"
          ? "PASS_ASSIST_ONLY_DELIVERY"
          : "PASS_NO_SAFE_ACTION",
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
      mode: "ASSIST_ONLY",
      hold: "HOLD",
      peer_deadman: peer,
      verdict: "FAIL_SCOPED_TICK",
      error: String(error?.message || error),
    };
    await persist(env, receipt);
    return receipt;
  }
}

export class BuilderCircleWorkflow extends WorkflowEntrypoint {
  async run(event, step) {
    return step.do(
      "bounded builder circle",
      { timeout: "20 minutes", retries: { limit: 0, delay: "1 second" } },
      async () =>
        runBuilderTick(this.env, {
          source: event.schedule ? "workflow_schedule" : event.payload?.source || "workflow_api",
          cron: event.schedule?.cron || "0 * * * *",
          instance_id: event.instanceId,
        }),
    );
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      const last = env.RECEIPTS ? await env.RECEIPTS.get("last_fired_at") : null;
      const lastJob = env.RECEIPTS ? await env.RECEIPTS.get("last_job_id") : null;
      return json({
        ok: true,
        schema: `${SCHEMA}-health`,
        loop_id: env.LOOP_ID || SCHEMA,
        cron: "0 * * * *",
        last_fired_at: last,
        last_job_id: lastJob,
        mode: "ASSIST_ONLY",
        hold: "HOLD",
        execution_runtime: "cloudflare_workflows",
        live_activation_authorized: String(env.LIVE_ACTIVATION || "") === "true",
        real_jobs_wired: true,
        job_catalog: ["motor_job", "commissioning_tick", "repair_run", "live_model_smoke"],
        model_keys_present: {
          deepseek: Boolean((env.DEEPSEEK_API_KEY || "").trim()),
          glm: Boolean((env.GLM_API_KEY || "").trim()),
          kimi: Boolean((env.MOONSHOT_API_KEY || "").trim()),
          openai: Boolean((env.OPENAI_API_KEY || "").trim()),
          gemini: Boolean((env.GEMINI_API_KEY || "").trim()),
          huggingface: Boolean((env.HF_TOKEN || "").trim()),
          workers_ai: Boolean(env.AI),
          motor_app: Boolean((env.MOTOR_APP_PRIVATE_KEY || "").trim()),
        },
      });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const provided = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
      if (!(await secretMatches(provided, env.TICK_SECRET))) return json({ ok: false }, 401);
      const instance = await env.BUILDER_WORKFLOW.create({
        params: { source: "authenticated_http_tick" },
      });
      return json({ accepted: true, workflow_instance_id: instance.id }, 202);
    }
    if (url.pathname === "/status" && url.searchParams.get("id")) {
      const instance = await env.BUILDER_WORKFLOW.get(url.searchParams.get("id"));
      return json({ id: instance.id, status: await instance.status() });
    }
    if (url.pathname === "/last" && env.RECEIPTS) {
      const raw = await env.RECEIPTS.get("last_receipt");
      return json(raw ? JSON.parse(raw) : { ok: false, error: "no_receipt_yet" });
    }
    if (url.pathname === "/map") return json(circleMap);
    if (url.pathname === "/jobs") {
      return json({
        schema: `${SCHEMA}-jobs`,
        jobs: circleMap.job_catalog || [],
      });
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
