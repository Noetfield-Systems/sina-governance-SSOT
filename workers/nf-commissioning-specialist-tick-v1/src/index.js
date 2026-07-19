/**
 * NF Commissioning Specialist v2.1
 * On-demand only: each explicit run advances one named, unfinished or
 * invalidated commissioning job from nf_commissioning_job_queue_v1.
 *
 * Observe → Detect → Critique → Repair(allowlist) → ProposeImprove → ReObserve
 * Models: DeepSeek V4 Flash → DeepSeek V4 Pro → GLM → Kimi → Hugging Face
 * HOLD / no enforcement / no unsupervised redesign / no fake fully_commissioned
 */
import { WorkflowEntrypoint } from "cloudflare:workers";

import mapDoc from "./map.json";
import jobQueue from "./job-queue.json";
import {
  authorized,
  readJobRequest,
  RequestError,
  workflowInstanceId,
} from "./control-plane.js";

const SCHEMA = "nf-commissioning-specialist-tick-v1";
const PROGRESS_KEY = jobQueue.progress_kv_key || "job_queue_progress";

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" },
  });
}

function providers(env) {
  return {
    deepseek_flash: {
      key: (env.DEEPSEEK_API_KEY || "").trim(),
      url: "https://api.deepseek.com/v1/chat/completions",
      model: "deepseek-v4-flash",
      thinking: "disabled",
      temperature: 0.2,
      max_tokens: 500,
      input_per_million_usd: 0.14,
      output_per_million_usd: 0.28,
    },
    deepseek_pro: {
      key: (env.DEEPSEEK_API_KEY || "").trim(),
      url: "https://api.deepseek.com/v1/chat/completions",
      model: "deepseek-v4-pro",
      thinking: "enabled",
      max_tokens: 1500,
      input_per_million_usd: 0.435,
      output_per_million_usd: 0.87,
    },
    glm: {
      key: (env.GLM_API_KEY || "").trim(),
      url: "https://api.z.ai/api/paas/v4/chat/completions",
      model: "glm-5.2",
      temperature: 0.2,
    },
    kimi: {
      key: (env.MOONSHOT_API_KEY || "").trim(),
      url: "https://api.moonshot.ai/v1/chat/completions",
      model: "kimi-k2.7-code",
      temperature: 1,
    },
    huggingface: {
      key: (env.HF_TOKEN || "").trim(),
      url: "https://router.huggingface.co/v1/chat/completions",
      model: "Qwen/Qwen2.5-7B-Instruct",
      temperature: 0.2,
    },
  };
}

async function chatComplete(env, system, user) {
  const order = (mapDoc.model_router && mapDoc.model_router.failover_order) || [
    "deepseek_flash",
    "deepseek_pro",
    "glm",
    "kimi",
    "huggingface",
  ];
  const pmap = providers(env);
  const errors = [];
  for (const name of order) {
    const p = pmap[name];
    if (!p || !p.key) {
      errors.push({ provider: name, error: "missing_key" });
      continue;
    }
    try {
      const resp = await fetch(p.url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${p.key}`,
          "Content-Type": "application/json",
          "User-Agent": SCHEMA,
        },
        body: JSON.stringify({
          model: p.model,
          ...(p.temperature !== undefined ? { temperature: p.temperature } : {}),
          ...(p.thinking ? { thinking: { type: p.thinking } } : {}),
          max_tokens: p.max_tokens || 500,
          messages: [
            { role: "system", content: system },
            { role: "user", content: user },
          ],
        }),
      });
      const text = await resp.text();
      let body = null;
      try {
        body = JSON.parse(text);
      } catch {
        body = null;
      }
      if (!resp.ok) {
        errors.push({ provider: name, status: resp.status, error: text.slice(0, 160) });
        continue;
      }
      const content =
        body?.choices?.[0]?.message?.content ||
        body?.choices?.[0]?.text ||
        null;
      if (!content) {
        errors.push({ provider: name, error: "empty_content" });
        continue;
      }
      const promptTokens = Number(body?.usage?.prompt_tokens);
      const completionTokens = Number(body?.usage?.completion_tokens);
      const hasUsage =
        Number.isFinite(promptTokens) &&
        Number.isFinite(completionTokens) &&
        promptTokens + completionTokens > 0;
      const estimatedCost =
        hasUsage &&
        typeof p.input_per_million_usd === "number" &&
        typeof p.output_per_million_usd === "number"
          ? (promptTokens * p.input_per_million_usd +
              completionTokens * p.output_per_million_usd) /
            1_000_000
          : null;
      return {
        ok: true,
        provider: name,
        model: p.model,
        content: String(content).slice(0, 2500),
        usage: hasUsage
          ? { prompt_tokens: promptTokens, completion_tokens: completionTokens }
          : null,
        estimated_cost_usd: estimatedCost === null ? null : Number(estimatedCost.toFixed(8)),
      };
    } catch (err) {
      errors.push({ provider: name, error: String(err && err.message ? err.message : err) });
    }
  }
  return { ok: false, provider: null, content: null, errors };
}

async function probe(url) {
  const started = Date.now();
  try {
    const resp = await fetch(url, {
      headers: { "User-Agent": SCHEMA, Accept: "application/json" },
      redirect: "follow",
    });
    const text = await resp.text();
    let body = null;
    try {
      body = JSON.parse(text);
    } catch {
      body = { raw: text.slice(0, 200) };
    }
    return {
      ok: resp.ok,
      status: resp.status,
      ms: Date.now() - started,
      body,
    };
  } catch (err) {
    return { ok: false, status: 0, ms: Date.now() - started, error: String(err) };
  }
}

function detect(observe) {
  const defects = [];
  const shadow = observe.surfaces.sg_shadow;
  if (!shadow?.ok) {
    defects.push({ id: "shadow_unreachable", severity: "P1", repair: "reprobe_shadow" });
  } else if (shadow.body?.enforcement_enabled === true) {
    defects.push({
      id: "enforcement_unexpectedly_on",
      severity: "P0",
      repair: null,
      note: "HOLD law — flag only",
    });
  }

  const reality = observe.surfaces.runtime_reality;
  if (!reality?.ok) {
    defects.push({ id: "runtime_reality_unreachable", severity: "P2", repair: null });
  } else {
    const hold = reality.body?.authority?.autonomous_production_mutations;
    if (hold && hold !== "HOLD") {
      defects.push({
        id: "hold_lifted_unexpected",
        severity: "P0",
        repair: null,
        note: "Founder-gated; specialist does not lift or restore HOLD autonomously",
      });
    }
    const liveShadow = reality.body?.sg_v2_state?.SG_V2_LIVE_SHADOW;
    if (liveShadow === "RUNNING_CANARY_ONLY" && !shadow?.ok) {
      defects.push({
        id: "false_live_claim",
        severity: "P1",
        repair: "clear_false_live_claim",
      });
    }
  }

  const pointer = observe.surfaces.key_pointer;
  if (!pointer?.ok) {
    defects.push({ id: "key_pointer_missing", severity: "P2", repair: null });
  }

  if (!observe.surfaces.job_queue?.ok) {
    defects.push({ id: "job_queue_unreachable", severity: "P1", repair: null });
  }

  return defects;
}

function allowlistedRepair(defect, observe) {
  const allow = new Set((mapDoc.repair_allowlist || []).map((x) => x.id));
  if (!defect.repair || !allow.has(defect.repair)) {
    return { applied: false, reason: "not_allowlisted_or_none" };
  }
  if (defect.repair === "reprobe_shadow") {
    return { applied: true, action: "reprobe_shadow", result: observe.surfaces.sg_shadow };
  }
  if (defect.repair === "clear_false_live_claim") {
    return {
      applied: true,
      action: "clear_false_live_claim",
      result: "flagged_in_receipt_no_main_mutation",
    };
  }
  if (defect.repair === "upsert_loop_liveness") {
    return { applied: true, action: defect.repair, result: "deferred_to_receipt_write" };
  }
  return { applied: false, reason: "unknown_repair" };
}

function scoreKeyCustody(reality) {
  const kc = reality?.key_custody || {};
  const key2 = kc.SG_COMMISSIONING_KEY_2_CUSTODY;
  const eligible = kc.SG_COMMISSIONING_ELIGIBLE;
  const pass = key2 === "ESTABLISHED" && eligible === true;
  return {
    job_id: "key_custody_score",
    status: pass ? "pass" : "blocked_founder",
    score: {
      SG_KEY_CUSTODY: kc.SG_KEY_CUSTODY || null,
      SG_COMMISSIONING_KEY_2_CUSTODY: key2 || null,
      SG_COMMISSIONING_ELIGIBLE: eligible ?? null,
      SG_BOOTSTRAP_KEY_1_REVOKED: kc.SG_BOOTSTRAP_KEY_1_REVOKED ?? null,
    },
    missing_decision: pass ? null : "establish_key2_custody_then_revoke_bootstrap_key1",
  };
}

function scoreUnifiedCore(reality) {
  const um = reality?.unified_motor || {};
  return {
    job_id: "unified_core_status_score",
    status: um.runtime_status === "COMMISSIONED" && um.active === true ? "pass" : "fail",
    score: {
      architecture_status: um.architecture_status || null,
      implementation_status: um.implementation_status || null,
      runtime_status: um.runtime_status || null,
      active: um.active ?? null,
    },
  };
}

function scoreEventGateway(reality) {
  const eg = reality?.event_gateway || {};
  const commissioned = eg.status === "COMMISSIONED";
  return {
    job_id: "event_gateway_status",
    status: commissioned ? "pass" : "blocked_founder",
    score: { status: eg.status || null, note: eg.note || null },
    missing_decision: commissioned ? null : "redeploy_event_gateway_after_key2_custody",
  };
}

function scoreResidentRoles(reality) {
  const rr = reality?.resident_roles || {};
  const ok = rr.sg_role === "COMMISSIONED" && rr.noos_role === "COMMISSIONED";
  return {
    job_id: "resident_roles_status",
    status: ok ? "pass" : "fail",
    score: { sg_role: rr.sg_role || null, noos_role: rr.noos_role || null },
  };
}

function scoreProofA(reality, observe) {
  const items = [
    { id: "durable_state", status: "unknown", note: "needs cold proof A run evidence" },
    { id: "dependency_graph", status: "unknown", note: "needs cold proof A run evidence" },
    {
      id: "concurrent_jobs",
      status: "unknown",
      note: "needs >=2 concurrent independent jobs evidence",
    },
    {
      id: "deterministic_work",
      status: observe.surfaces.sg_shadow?.ok ? "partial" : "fail",
      note: "shadow probe is T0 only — not full proof A",
    },
    { id: "intel_low_work", status: "unknown", note: "needs COST-T1 binding evidence" },
    {
      id: "real_repo_change",
      status: "partial",
      note: "commissioning runway draft PR path exists; not proof A heading close",
    },
    { id: "ci_independent_recompute", status: "unknown", note: "needs proof A CI evidence" },
    {
      id: "auto_close_empty_queue",
      status: "fail",
      note: "unified_motor.runtime_status still NOT_COMMISSIONED",
    },
    {
      id: "no_session_dependency",
      status: "partial",
      note: "cf cron fires without laptop; proof A not yet delivered",
    },
  ];
  const um = reality?.unified_motor?.runtime_status;
  return {
    job_id: "proof_a_checklist",
    status: um === "COMMISSIONED" ? "pass" : "fail",
    items,
    runtime_status: um || null,
  };
}

function scoreProofB(reality) {
  const items = [
    { id: "deterministic_failure_evidence", status: "unknown" },
    { id: "low_cost_diagnosis", status: "partial", note: "specialist critique path exists" },
    { id: "bounded_repair_execution", status: "partial", note: "allowlisted repair only" },
    { id: "full_reverification", status: "unknown" },
    { id: "waiting_for_founder_reasoning", status: "unknown" },
    { id: "unrelated_jobs_continue", status: "unknown" },
    { id: "reasoning_result_ingest", status: "unknown" },
    { id: "auto_resume", status: "unknown" },
    { id: "lease_recovery", status: "unknown" },
  ];
  return {
    job_id: "proof_b_checklist",
    status: "fail",
    items,
    note: "proof B not delivered while unified core not commissioned",
    runtime_status: reality?.unified_motor?.runtime_status || null,
  };
}

function scoreCredentialBootstrap(reality) {
  const kc = reality?.key_custody || {};
  const revoked = kc.SG_BOOTSTRAP_KEY_1_REVOKED === true;
  return {
    job_id: "credential_bootstrap_gap",
    status: revoked ? "pass" : "blocked_founder",
    score: {
      SG_BOOTSTRAP_KEY_1: kc.SG_BOOTSTRAP_KEY_1 || null,
      SG_BOOTSTRAP_KEY_1_REVOKED: kc.SG_BOOTSTRAP_KEY_1_REVOKED ?? null,
      SG_COMMISSIONING_KEY_2_CUSTODY: kc.SG_COMMISSIONING_KEY_2_CUSTODY || null,
    },
    missing_decision: revoked ? null : "revoke_bootstrap_key1_after_key2_custody",
  };
}

function score48hLiveness(lastFiredAt, intervalMinutes) {
  if (!lastFiredAt) {
    return {
      job_id: "specialist_48h_liveness",
      status: "fail",
      note: "no last_fired_at yet",
    };
  }
  const ageMs = Date.now() - Date.parse(lastFiredAt);
  const limitMs = 2 * (intervalMinutes || 5) * 60 * 1000;
  return {
    job_id: "specialist_48h_liveness",
    status: ageMs <= limitMs ? "pass" : "fail",
    last_fired_at: lastFiredAt,
    age_ms: ageMs,
    limit_ms: limitMs,
  };
}

function rollupDirective(reality) {
  const d = reality?.commissioning_directive || {};
  const fields = {
    event_gateway: d.event_gateway || null,
    sg_role: d.sg_role || null,
    noos_role: d.noos_role || null,
    unified_motor_runtime: d.unified_motor_runtime || null,
    autonomous_production_mutations: d.autonomous_production_mutations || null,
    fully_commissioned_claim: d.fully_commissioned_claim ?? null,
  };
  const anyOpen = Object.values(fields).some(
    (v) => v === "NOT_COMMISSIONED" || v === "HOLD" || v === false,
  );
  return {
    job_id: "commissioning_directive_rollup",
    status: anyOpen ? "fail" : "pass",
    fields,
    refuse_fully_commissioned: true,
  };
}

async function loadProgress(env) {
  if (!env.RECEIPTS) return { jobs: {} };
  const raw = await env.RECEIPTS.get(PROGRESS_KEY);
  if (!raw) return { jobs: {} };
  try {
    return JSON.parse(raw);
  } catch {
    return { jobs: {} };
  }
}

async function mintMotorInstallationToken(env) {
  const appId = String(env.MOTOR_APP_ID || "4275961").trim();
  const pem = (env.MOTOR_APP_PRIVATE_KEY || "").trim();
  if (!pem) return null;
  const now = Math.floor(Date.now() / 1000);
  const enc = new TextEncoder();
  const toB64Url = (buf) => {
    let s = "";
    const bytes = buf instanceof ArrayBuffer ? new Uint8Array(buf) : buf;
    for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
    return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
  };
  const header = toB64Url(enc.encode(JSON.stringify({ alg: "RS256", typ: "JWT" })));
  const payload = toB64Url(
    enc.encode(JSON.stringify({ iat: now - 60, exp: now + 540, iss: Number(appId) })),
  );
  const key = await crypto.subtle.importKey(
    "pkcs8",
    pemToArrayBuffer(pem),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, enc.encode(`${header}.${payload}`));
  const jwt = `${header}.${payload}.${toB64Url(sig)}`;
  const installId = String(env.MOTOR_INSTALLATION_ID || "145975487").trim();
  const tokRes = await fetch(`https://api.github.com/app/installations/${installId}/access_tokens`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${jwt}`,
      Accept: "application/vnd.github+json",
      "User-Agent": SCHEMA,
      "X-GitHub-Api-Version": "2026-03-10",
    },
  });
  if (!tokRes.ok) return null;
  const tok = await tokRes.json();
  return tok.token || null;
}

function pemToArrayBuffer(pem) {
  const b64 = pem
    .replace(/-----BEGIN [^-]+-----/g, "")
    .replace(/-----END [^-]+-----/g, "")
    .replace(/\s+/g, "");
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes.buffer;
}

async function ghApi(token, path, method = "GET", body = null) {
  const resp = await fetch(`https://api.github.com${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": SCHEMA,
      "X-GitHub-Api-Version": "2026-03-10",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await resp.text();
  let jsonBody = null;
  try {
    jsonBody = text ? JSON.parse(text) : null;
  } catch {
    jsonBody = { raw: text.slice(0, 300) };
  }
  return { ok: resp.ok, status: resp.status, body: jsonBody };
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function dispatchWorkflowJob(env, job, tokenOverride = null) {
  const d = job?.dispatch;
  if (!d || !d.workflow) return { ok: false, skipped: true, reason: "no_dispatch" };
  const token = tokenOverride || (await mintMotorInstallationToken(env));
  if (!token) return { ok: false, error: "token_mint_failed" };
  const repo = d.repo || env.COMMISSIONING_RUNWAY_REPO || "Noetfield-Systems/NOETFIELD-RUNWAY";
  const ref = d.ref || "main";
  const inputs = d.inputs || {};
  const before = new Date().toISOString();
  const path = `/repos/${repo}/actions/workflows/${d.workflow}/dispatches`;
  const res = await ghApi(token, path, "POST", {
    ref,
    inputs,
    return_run_details: true,
  });
  return {
    ok: res.status === 200 || res.status === 204 || res.ok,
    status: res.status,
    repo,
    workflow: d.workflow,
    ref,
    job_id: job.id,
    dispatched_at: before,
    workflow_run_id: res.body?.workflow_run_id || null,
    run_url: res.body?.run_url || null,
    html_url: res.body?.html_url || null,
    body: res.body,
  };
}

async function findRecentWorkflowRuns(token, repo, workflow, sinceIso, want = 1) {
  const sinceMs = Date.parse(sinceIso) - 15_000;
  const res = await ghApi(
    token,
    `/repos/${repo}/actions/workflows/${workflow}/runs?event=workflow_dispatch&per_page=20`,
  );
  const runs = (res.body?.workflow_runs || []).filter((r) => Date.parse(r.created_at) >= sinceMs);
  return runs.slice(0, want).map((r) => ({
    id: r.id,
    status: r.status,
    conclusion: r.conclusion,
    html_url: r.html_url,
    created_at: r.created_at,
    head_sha: r.head_sha,
  }));
}

async function waitForRuns(token, repo, runIds, maxWaitMs = 90_000) {
  const started = Date.now();
  const results = [];
  while (Date.now() - started < maxWaitMs) {
    results.length = 0;
    let pending = 0;
    for (const id of runIds) {
      const res = await ghApi(token, `/repos/${repo}/actions/runs/${id}`);
      const r = res.body || {};
      const row = {
        id: r.id || id,
        status: r.status || "unknown",
        conclusion: r.conclusion || null,
        html_url: r.html_url || null,
      };
      results.push(row);
      if (row.status !== "completed") pending += 1;
    }
    if (pending === 0) break;
    await sleep(8_000);
  }
  const allDone = results.length === runIds.length && results.every((r) => r.status === "completed");
  const allPass = allDone && results.every((r) => r.conclusion === "success");
  const anyFail =
    allDone && results.some((r) => r.conclusion && r.conclusion !== "success");
  return {
    allDone,
    allPass,
    anyFail,
    results,
    waited_ms: Date.now() - started,
  };
}

async function executeDispatchAndWait(env, job, count = 1) {
  const token = await mintMotorInstallationToken(env);
  if (!token) {
    return { job_id: job.id, status: "fail", error: "token_mint_failed" };
  }
  const d = job.dispatch || {};
  const repo = d.repo || "Noetfield-Systems/NOETFIELD-RUNWAY";
  const workflow = d.workflow;
  const dispatchedAt = new Date().toISOString();
  const dispatches = [];
  for (let i = 0; i < count; i++) {
    const one = await dispatchWorkflowJob(env, job, token);
    dispatches.push(one);
    if (!one.ok) {
      return {
        job_id: job.id,
        status: "fail",
        proof: job.proof || null,
        error: "dispatch_failed",
        dispatches,
      };
    }
    if (i + 1 < count) await sleep(1_500);
  }
  const returnedRunIds = dispatches
    .map((dispatch) => dispatch.workflow_run_id)
    .filter(Boolean);
  let runs = returnedRunIds.map((id, index) => ({
    id,
    status: "queued",
    conclusion: null,
    html_url: dispatches[index]?.html_url || null,
    created_at: dispatches[index]?.dispatched_at || dispatchedAt,
    head_sha: null,
  }));
  // The 2026-03-10 API returns exact run IDs. Keep discovery only as a
  // compatibility fallback for GitHub installations that still answer 204.
  if (runs.length < count) {
    await sleep(5_000);
    runs = await findRecentWorkflowRuns(token, repo, workflow, dispatchedAt, count);
    for (let i = 0; i < 6 && runs.length < count; i++) {
      await sleep(5_000);
      runs = await findRecentWorkflowRuns(token, repo, workflow, dispatchedAt, count);
    }
  }
  if (runs.length < count) {
    return {
      job_id: job.id,
      status: "dispatched_pending",
      proof: job.proof || null,
      dispatches,
      runs,
      note: "workflow dispatched; runs not visible yet — next tick will poll",
      pending: {
        repo,
        workflow,
        since: dispatchedAt,
        want: count,
        run_ids: runs.map((r) => r.id),
      },
    };
  }
  const waited = await waitForRuns(
    token,
    repo,
    runs.map((r) => r.id),
    20 * 60_000,
  );
  if (!waited.allDone) {
    return {
      job_id: job.id,
      status: "dispatched_pending",
      proof: job.proof || null,
      dispatches,
      runs: waited.results,
      waited_ms: waited.waited_ms,
      pending: {
        repo,
        workflow,
        since: dispatchedAt,
        want: count,
        run_ids: waited.results.map((r) => r.id),
      },
    };
  }
  return {
    job_id: job.id,
    status: waited.allPass ? "pass" : "fail",
    proof: job.proof || null,
    dispatches,
    runs: waited.results,
    waited_ms: waited.waited_ms,
    acceptance: job.acceptance,
  };
}

async function executeSelectedJob(env, job, observe, lastFiredAt) {
  const reality = observe.surfaces.runtime_reality?.body || {};
  const action = job?.runway_action;
  if (!job) return { status: "fail", error: "no_job" };

  if (action === "probe_required_surfaces") {
    const ok =
      observe.surfaces.sg_shadow?.ok &&
      observe.surfaces.runtime_reality?.ok &&
      observe.surfaces.key_pointer?.ok;
    return {
      job_id: job.id,
      status: ok ? "pass" : "fail",
      probes: {
        sg_shadow: observe.surfaces.sg_shadow?.ok,
        runtime_reality: observe.surfaces.runtime_reality?.ok,
        key_pointer: observe.surfaces.key_pointer?.ok,
        job_queue: observe.surfaces.job_queue?.ok,
      },
    };
  }
  if (action === "score_founder_reasoning_ingest_live") {
    const live = await probe(job.live_probe);
    return {
      job_id: job.id,
      status: "blocked_founder",
      live_probe: {
        ok: live.ok,
        status: live.status,
        ms: live.ms,
      },
      missing_decision:
        "submit an authorized founder reasoning result to the staging reasoning-results endpoint and provide its receipt",
      note: "The commissioning Worker probes this founder-gated path but never fabricates or submits founder reasoning.",
    };
  }
  if (action === "score_key_custody") return scoreKeyCustody(reality);
  if (action === "score_unified_core") return scoreUnifiedCore(reality);
  if (action === "score_event_gateway") return scoreEventGateway(reality);
  if (action === "score_resident_roles") return scoreResidentRoles(reality);
  if (action === "score_proof_a") return scoreProofA(reality, observe);
  if (action === "score_proof_b") return scoreProofB(reality);
  if (action === "score_credential_bootstrap") return scoreCredentialBootstrap(reality);
  if (action === "score_48h_liveness") {
    return score48hLiveness(lastFiredAt, Number(env.INTERVAL_MINUTES || mapDoc.interval_minutes || 5));
  }
  if (action === "rollup_commissioning_directive") return rollupDirective(reality);
  if (action === "dispatch_and_wait") {
    return executeDispatchAndWait(env, job, 1);
  }
  if (action === "dispatch_concurrent_and_wait") {
    const count = Number(job.dispatch?.count || 2);
    return executeDispatchAndWait(env, job, count);
  }
  return { job_id: job.id, status: "fail", error: `unknown_runway_action:${action}` };
}

async function runTick(env, meta = {}) {
  const at = new Date().toISOString();
  const requestedJobId = String(meta.jobId || "").trim();
  const selectedIndex = (jobQueue.jobs || []).findIndex((job) => job.id === requestedJobId);
  if (selectedIndex < 0) throw new Error(`unknown commissioning job_id: ${requestedJobId}`);
  const job = jobQueue.jobs[selectedIndex];
  const queueUrl =
    env.JOB_QUEUE_URL ||
    "https://raw.githubusercontent.com/Noetfield-Systems/sina-governance-SSOT/main/data/nf_commissioning_job_queue_v1.json";

  const [sgShadow, runtimeReality, keyPointer, queueProbe] = await Promise.all([
    probe(env.SG_SHADOW_HEALTH_URL),
    probe(env.RUNTIME_REALITY_URL),
    probe(env.KEY_POINTER_URL),
    probe(queueUrl),
  ]);
  const observe = {
    at,
    surfaces: {
      sg_shadow: sgShadow,
      runtime_reality: runtimeReality,
      key_pointer: keyPointer,
      job_queue: queueProbe,
    },
  };

  const defects = detect(observe);
  const repairs = defects.map((d) => ({ defect: d.id, ...allowlistedRepair(d, observe) }));

  let lastFiredAt = null;
  if (env.RECEIPTS) lastFiredAt = await env.RECEIPTS.get("last_fired_at");

  const progress = await loadProgress(env);
  const jobResult = await executeSelectedJob(env, job, observe, lastFiredAt);

  repairs.push({
    defect: `job:${job?.id || "none"}`,
    applied: true,
    action: "execute_or_dispatch_selected_job",
    result: jobResult,
  });

  let critique = { ok: false, skipped: true, reason: "t0_job_execution" };
  if (defects.length || jobResult.status === "fail" || jobResult.status === "blocked_founder") {
    critique = await chatComplete(
      env,
      "You are the Noetfield commissioning specialist. Classify defects and the selected job result. Reply JSON only: {summary, severity, next_safe_action, job_next}. Never recommend minting new App keys, lifting HOLD, unsupervised redesign, or claiming fully_commissioned.",
      JSON.stringify({
        defects,
        job: { id: job?.id, class: job?.class, acceptance: job?.acceptance },
        job_result: jobResult,
        observe_ok: {
          shadow: observe.surfaces.sg_shadow?.ok,
          reality: observe.surfaces.runtime_reality?.ok,
          pointer: observe.surfaces.key_pointer?.ok,
          job_queue: observe.surfaces.job_queue?.ok,
        },
      }),
    );
  }

  let proposal = null;
  if (
    defects.some((d) => d.severity === "P1" || d.severity === "P0") ||
    jobResult.status === "blocked_founder"
  ) {
    const improve = await chatComplete(
      env,
      "Propose ONE machine-safe kaizen improvement for commissioning job delivery. JSON only: {title, why, machine_safe:true|false, needs_founder:true|false, related_job_id}. No architecture redesign. No HOLD removal.",
      JSON.stringify({
        defects: defects.map((d) => d.id),
        job_id: job?.id,
        job_status: jobResult.status,
        map_version: mapDoc.version,
      }),
    );
    if (improve.ok) {
      proposal = {
        schema: "nf.kaizen-proposal.v1",
        status: "PROPOSED_PENDING_FOUNDER",
        provider: improve.provider,
        model: improve.model,
        content: improve.content,
        usage: improve.usage || null,
        estimated_cost_usd: improve.estimated_cost_usd,
      };
    }
  }

  progress.jobs = progress.jobs || {};
  if (job?.id) {
    progress.jobs[job.id] = {
      status: jobResult.status,
      at,
      queue_version: jobQueue.version,
      request_id: meta.requestId || null,
      workflow_instance_id: meta.instanceId || null,
      rerun_reason: meta.rerunReason || null,
      missing_decision: jobResult.missing_decision || null,
      runs: jobResult.runs || null,
      proof: jobResult.proof || job?.proof || null,
    };
  }
  progress.updated_at = at;

  const successfulLlmResults = [critique, proposal].filter(
    (result) => result && result.provider,
  );
  const meteredLlmResults = successfulLlmResults.filter(
    (result) => result && typeof result.estimated_cost_usd === "number",
  );
  const knownLlmEstimatedCostUsd = Number(
    meteredLlmResults
      .reduce((sum, result) => sum + result.estimated_cost_usd, 0)
      .toFixed(8),
  );
  const unmeteredLlmCalls = successfulLlmResults.length - meteredLlmResults.length;

  const verdict = defects.some((d) => d.severity === "P0")
    ? "FAIL_P0"
    : jobResult.status === "dispatched_pending"
      ? "PROOF_PENDING"
      : jobResult.status === "fail" && job?.class === "execute"
        ? "PROOF_FAIL"
        : jobResult.status === "fail" && defects.length
          ? "DEGRADED_HEALING"
          : jobResult.status === "blocked_founder"
            ? "BLOCKED_FOUNDER_JOB"
            : jobResult.status === "pass" && job?.class === "execute"
              ? "PASS_PROOF_TICK"
              : jobResult.status === "pass"
                ? "PASS_JOB_TICK"
                : "PASS_SCOPED_TICK";

  const receipt = {
    schema: SCHEMA,
    loop_id: env.LOOP_ID || mapDoc.loop_id,
    at,
    source: meta.source || "cloudflare_workflow",
    request_id: meta.requestId || null,
    workflow_instance_id: meta.instanceId || null,
    rerun_reason: meta.rerunReason || null,
    cron: null,
    mode: env.MODE || "COMMISSIONING_ON_DEMAND",
    hold: env.AUTONOMOUS_PRODUCTION_MUTATIONS || "HOLD",
    enforcement_enabled: false,
    map_version: mapDoc.version,
    queue_version: jobQueue.version,
    skills: mapDoc.skills,
    selected_job: job
      ? { id: job.id, class: job.class, runway_action: job.runway_action, acceptance: job.acceptance }
      : null,
    job_result: jobResult,
    job_progress: {
      completed_for_queue_version: Object.entries(progress.jobs || {})
        .filter(([, value]) => value.queue_version === jobQueue.version && value.status === "pass")
        .map(([id]) => id),
    },
    observe,
    defects,
    repairs,
    critique,
    propose_improve: proposal,
    llm_cost: {
      calls: successfulLlmResults.length,
      metered_calls: meteredLlmResults.length,
      unmetered_calls: unmeteredLlmCalls,
      estimated_usd: unmeteredLlmCalls === 0 ? knownLlmEstimatedCostUsd : null,
      known_estimated_usd: knownLlmEstimatedCostUsd,
      basis: "provider usage tokens times configured current model rates",
    },
    model_keys_present: {
      deepseek: Boolean((env.DEEPSEEK_API_KEY || "").trim()),
      glm: Boolean((env.GLM_API_KEY || "").trim()),
      kimi: Boolean((env.MOONSHOT_API_KEY || "").trim()),
      huggingface: Boolean((env.HF_TOKEN || "").trim()),
    },
    verdict,
  };

  if (env.RECEIPTS) {
    await env.RECEIPTS.put(PROGRESS_KEY, JSON.stringify(progress));
    const key = meta.instanceId ? `job:${meta.instanceId}` : `job:${at}`;
    await env.RECEIPTS.put(key, JSON.stringify(receipt), { expirationTtl: 60 * 60 * 24 * 14 });
    await env.RECEIPTS.put("last_fired_at", at);
    await env.RECEIPTS.put("last_receipt", JSON.stringify(receipt));
    await env.RECEIPTS.put("last_job_id", job?.id || "");
  }

  return receipt;
}

export class CommissioningJobWorkflow extends WorkflowEntrypoint {
  async run(event, step) {
    const payload = event?.payload || {};
    const jobId = String(payload.jobId || "").trim();
    const job = (jobQueue.jobs || []).find((candidate) => candidate.id === jobId);
    if (!job || job.machine_safe !== true) {
      throw new Error(`invalid or unsafe commissioning job_id: ${jobId || "missing"}`);
    }

    console.log(
      JSON.stringify({
        schema: SCHEMA,
        event: "commissioning_job_started",
        workflow_instance_id: payload.instanceId || null,
        job_id: jobId,
        request_id: payload.requestId || null,
      }),
    );

    const receipt = await step.do(
      `execute ${jobId}`,
      {
        retries: { limit: 1, delay: "1 second", backoff: "constant" },
        timeout: "30 minutes",
      },
      () =>
        runTick(this.env, {
          source: "cloudflare_workflow",
          jobId,
          requestId: payload.requestId,
          instanceId: payload.instanceId,
          rerunReason: payload.rerunReason,
        }),
    );

    console.log(
      JSON.stringify({
        schema: SCHEMA,
        event: "commissioning_job_finished",
        workflow_instance_id: payload.instanceId || null,
        job_id: jobId,
        verdict: receipt.verdict,
      }),
    );
    return receipt;
  }
}

export default {
  async scheduled(event, env, ctx) {
    // Safety stop for any stale Cloudflare schedule event during deployment propagation.
    // Commissioning is finite work and must be explicitly dispatched with a chosen job.
    ctx.waitUntil(
      Promise.resolve().then(() => {
        console.log(
          JSON.stringify({
            schema: SCHEMA,
            ok: true,
            verdict: "SCHEDULE_DISABLED",
            trigger_mode: "on_demand",
            cron: event?.cron || null,
            at: new Date().toISOString(),
          }),
        );
      }),
    );
  },

  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Authorization, Content-Type",
        },
      });
    }
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      let last = null;
      let lastJob = null;
      if (env.RECEIPTS) {
        last = await env.RECEIPTS.get("last_fired_at");
        lastJob = await env.RECEIPTS.get("last_job_id");
      }
      return json({
        ok: true,
        schema: SCHEMA + "-health",
        service: "nf-commissioning-specialist-tick-v1",
        trigger_mode: "on_demand",
        cron: null,
        schedule_enabled: false,
        dispatch_path: "POST /jobs (Bearer auth, explicit job_id and request_id)",
        execution_owner: "Cloudflare Workflow -> one allowlisted GitHub Actions workflow",
        workflow_binding_present: Boolean(env.COMMISSIONING_JOB),
        loop_id: env.LOOP_ID,
        last_fired_at: last,
        last_job_id: lastJob,
        queue_version: jobQueue.version,
        job_count: (jobQueue.jobs || []).length,
        hold: env.AUTONOMOUS_PRODUCTION_MUTATIONS || "HOLD",
        enforcement_enabled: false,
        map_version: mapDoc.version,
        model_keys_present: {
          deepseek: Boolean((env.DEEPSEEK_API_KEY || "").trim()),
          glm: Boolean((env.GLM_API_KEY || "").trim()),
          kimi: Boolean((env.MOONSHOT_API_KEY || "").trim()),
          huggingface: Boolean((env.HF_TOKEN || "").trim()),
        },
      });
    }
    if (url.pathname === "/jobs" && request.method === "POST") {
      const auth = await authorized(request, env.COMMISSIONING_TRIGGER_SECRET);
      if (auth.unavailable) {
        return json({ ok: false, error: "commissioning_trigger_secret_not_configured" }, 503);
      }
      if (!auth.ok) return json({ ok: false, error: "unauthorized" }, 401);
      if (!env.COMMISSIONING_JOB) {
        return json({ ok: false, error: "commissioning_workflow_binding_missing" }, 503);
      }

      try {
        const parsed = await readJobRequest(request, jobQueue.jobs || []);
        const instanceId = await workflowInstanceId(parsed.requestId);
        let existing = null;
        try {
          existing = await env.COMMISSIONING_JOB.get(instanceId);
          const existingStatus = await existing.status();
          const requestRecord = env.RECEIPTS
            ? await env.RECEIPTS.get(`request:${instanceId}`, "json")
            : null;
          if (requestRecord?.job_id && requestRecord.job_id !== parsed.jobId) {
            return json(
              {
                ok: false,
                error: "request_id_payload_conflict",
                instance_id: instanceId,
                original_job_id: requestRecord.job_id,
              },
              409,
            );
          }
          return json(
            {
              ok: true,
              replay: true,
              instance_id: instanceId,
              job_id: requestRecord?.job_id || parsed.jobId,
              details: existingStatus,
            },
            200,
          );
        } catch {
          existing = null;
        }

        const progress = await loadProgress(env);
        const previous = progress.jobs?.[parsed.jobId];
        if (
          previous?.status === "pass" &&
          previous?.queue_version === jobQueue.version &&
          !parsed.rerunReason
        ) {
          return json(
            {
              ok: false,
              error: "completed_job_unchanged",
              job_id: parsed.jobId,
              queue_version: jobQueue.version,
              completed_at: previous.at,
              action: "Provide a new request_id and a 12-500 character rerun_reason to reverify.",
            },
            409,
          );
        }

        let instance;
        let replay = false;
        try {
          instance = await env.COMMISSIONING_JOB.create({
            id: instanceId,
            params: {
              instanceId,
              jobId: parsed.jobId,
              requestId: parsed.requestId,
              rerunReason: parsed.rerunReason,
              requestedAt: new Date().toISOString(),
            },
          });
        } catch (createError) {
          try {
            instance = await env.COMMISSIONING_JOB.get(instanceId);
            await instance.status();
            replay = true;
          } catch {
            throw createError;
          }
        }
        if (env.RECEIPTS) {
          await env.RECEIPTS.put(
            `request:${instanceId}`,
            JSON.stringify({
              job_id: parsed.jobId,
              request_id: parsed.requestId,
              rerun_reason: parsed.rerunReason,
              queue_version: jobQueue.version,
              created_at: new Date().toISOString(),
            }),
            { expirationTtl: 60 * 60 * 24 * 14 },
          );
        }
        return json(
          {
            ok: true,
            replay,
            instance_id: instance.id,
            job_id: parsed.jobId,
            details: await instance.status(),
          },
          replay ? 200 : 202,
        );
      } catch (error) {
        if (error instanceof RequestError) {
          return json({ ok: false, error: error.code, message: error.message }, error.status);
        }
        console.error(
          JSON.stringify({
            schema: SCHEMA,
            event: "commissioning_job_create_failed",
            error: String(error?.message || error),
          }),
        );
        return json({ ok: false, error: "commissioning_job_create_failed" }, 503);
      }
    }
    if (url.pathname.startsWith("/jobs/") && request.method === "GET") {
      const auth = await authorized(request, env.COMMISSIONING_TRIGGER_SECRET);
      if (auth.unavailable) {
        return json({ ok: false, error: "commissioning_trigger_secret_not_configured" }, 503);
      }
      if (!auth.ok) return json({ ok: false, error: "unauthorized" }, 401);
      if (!env.COMMISSIONING_JOB) {
        return json({ ok: false, error: "commissioning_workflow_binding_missing" }, 503);
      }
      const instanceId = decodeURIComponent(url.pathname.slice("/jobs/".length));
      if (!/^commission-[a-f0-9]{48}$/.test(instanceId)) {
        return json({ ok: false, error: "invalid_instance_id" }, 400);
      }
      try {
        const instance = await env.COMMISSIONING_JOB.get(instanceId);
        return json({ ok: true, instance_id: instance.id, details: await instance.status() });
      } catch {
        return json({ ok: false, error: "workflow_instance_not_found" }, 404);
      }
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      return json(
        {
          ok: false,
          error: "perpetual_tick_disabled",
          trigger_mode: "on_demand",
          action: "POST an explicit authenticated request to /jobs.",
        },
        410,
      );
    }
    if (url.pathname === "/map") return json(mapDoc);
    if (url.pathname === "/queue") return json(jobQueue);
    if (url.pathname === "/progress" && env.RECEIPTS) {
      const raw = await env.RECEIPTS.get(PROGRESS_KEY);
      return json(raw ? JSON.parse(raw) : { jobs: {} });
    }
    if (url.pathname === "/last" && env.RECEIPTS) {
      const raw = await env.RECEIPTS.get("last_receipt");
      return json(raw ? JSON.parse(raw) : { ok: false, error: "no_receipt_yet" });
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
