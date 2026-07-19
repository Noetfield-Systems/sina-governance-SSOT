/**
 * NF Commissioning Specialist v2.1
 * On-demand only: each explicit run advances one named, unfinished or
 * invalidated commissioning job from nf_commissioning_job_queue_v1.
 *
 * Observe → Detect → Critique → Repair(allowlist) → ProposeImprove → ReObserve
 * Models: DeepSeek → GLM → Kimi → Hugging Face
 * HOLD / no enforcement / no unsupervised redesign / no fake fully_commissioned
 */
import mapDoc from "./map.json";
import jobQueue from "./job-queue.json";

const SCHEMA = "nf-commissioning-specialist-tick-v1";
const CURSOR_KEY = jobQueue.cursor_kv_key || "job_queue_cursor";
const PROGRESS_KEY = jobQueue.progress_kv_key || "job_queue_progress";

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" },
  });
}

function providers(env) {
  return {
    deepseek: {
      key: (env.DEEPSEEK_API_KEY || "").trim(),
      url: "https://api.deepseek.com/v1/chat/completions",
      model: "deepseek-chat",
    },
    glm: {
      key: (env.GLM_API_KEY || "").trim(),
      url: "https://open.bigmodel.cn/api/paas/v4/chat/completions",
      model: "glm-4-flash",
    },
    kimi: {
      key: (env.MOONSHOT_API_KEY || "").trim(),
      url: "https://api.moonshot.ai/v1/chat/completions",
      model: "moonshot-v1-8k",
    },
    huggingface: {
      key: (env.HF_TOKEN || "").trim(),
      url: "https://router.huggingface.co/v1/chat/completions",
      model: "Qwen/Qwen2.5-7B-Instruct",
    },
  };
}

async function chatComplete(env, system, user) {
  const order = (mapDoc.model_router && mapDoc.model_router.failover_order) || [
    "deepseek",
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
          temperature: 0.2,
          max_tokens: 500,
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
      return { ok: true, provider: name, model: p.model, content: String(content).slice(0, 2500) };
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

function getByPath(obj, path) {
  let cur = obj;
  for (const part of String(path).split(".")) {
    if (cur === null || typeof cur !== "object") return undefined;
    cur = cur[part];
  }
  return cur;
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
  if (defect.repair === "upsert_loop_liveness" || defect.repair === "rotate_stale_receipt_pointer") {
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
  if (!env.RECEIPTS) return { cursor: 0, jobs: {} };
  const raw = await env.RECEIPTS.get(PROGRESS_KEY);
  if (!raw) return { cursor: 0, jobs: {} };
  try {
    return JSON.parse(raw);
  } catch {
    return { cursor: 0, jobs: {} };
  }
}

function selectNextJob(progress) {
  const jobs = jobQueue.jobs || [];
  if (!jobs.length) return { index: 0, job: null };
  // Prefer execute-class incomplete jobs first
  const executeIdx = [];
  const qualifyIdx = [];
  for (let i = 0; i < jobs.length; i++) {
    const job = jobs[i];
    const prev = progress.jobs?.[job.id];
    if (prev?.status === "pass" && prev?.cycle === progress.cycle) continue;
    if (job.class === "execute") executeIdx.push(i);
    else qualifyIdx.push(i);
  }
  const order = executeIdx.concat(qualifyIdx);
  if (!order.length) {
    const start = Number(progress.cursor || 0) % jobs.length;
    return { index: start, job: jobs[start], wrapped: true };
  }
  const startCursor = Number(progress.cursor || 0);
  const ranked = order.sort((a, b) => {
    const da = (a - startCursor + jobs.length) % jobs.length;
    const db = (b - startCursor + jobs.length) % jobs.length;
    return da - db;
  });
  const idx = ranked[0];
  return { index: idx, job: jobs[idx] };
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
      "X-GitHub-Api-Version": "2022-11-28",
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
      "X-GitHub-Api-Version": "2022-11-28",
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

async function dispatchCommissioningRunway(env, receipt, job) {
  const repo = (env.COMMISSIONING_RUNWAY_REPO || "Noetfield-Systems/NOETFIELD-RUNWAY").trim();
  try {
    const token = await mintMotorInstallationToken(env);
    if (!token) {
      return { ok: false, error: "MOTOR_APP_PRIVATE_KEY missing or mint failed — runway dispatch skipped" };
    }
    const resp = await fetch(`https://api.github.com/repos/${repo}/dispatches`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": SCHEMA,
        "X-GitHub-Api-Version": "2022-11-28",
      },
      body: JSON.stringify({
        event_type: "commissioning_tick",
        client_payload: {
          source: "cf-cron",
          at: receipt.at,
          verdict: receipt.verdict,
          loop_id: receipt.loop_id,
          job_id: job?.id || null,
          job_class: job?.class || null,
          runway_action: job?.runway_action || null,
          map_version: mapDoc.version,
          queue_version: jobQueue.version,
        },
      }),
    });
    return {
      ok: resp.status === 204,
      status: resp.status,
      repo,
      event_type: "commissioning_tick",
      job_id: job?.id || null,
    };
  } catch (err) {
    return { ok: false, error: String(err && err.message ? err.message : err) };
  }
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
  const res = await ghApi(token, path, "POST", { ref, inputs });
  return {
    ok: res.status === 204 || res.ok,
    status: res.status,
    repo,
    workflow: d.workflow,
    ref,
    job_id: job.id,
    dispatched_at: before,
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
  // Give Actions a moment to materialize runs
  await sleep(5_000);
  let runs = await findRecentWorkflowRuns(token, repo, workflow, dispatchedAt, count);
  // Retry discovery briefly
  for (let i = 0; i < 6 && runs.length < count; i++) {
    await sleep(5_000);
    runs = await findRecentWorkflowRuns(token, repo, workflow, dispatchedAt, count);
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
    90_000,
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

async function resumePendingJob(env, progress) {
  const pending = progress.pending;
  if (!pending?.run_ids?.length) return null;
  const token = await mintMotorInstallationToken(env);
  if (!token) return { job_id: pending.job_id, status: "fail", error: "token_mint_failed" };
  const waited = await waitForRuns(token, pending.repo, pending.run_ids, 90_000);
  if (!waited.allDone) {
    return {
      job_id: pending.job_id,
      status: "dispatched_pending",
      proof: pending.proof || null,
      runs: waited.results,
      waited_ms: waited.waited_ms,
      pending,
      resumed: true,
    };
  }
  return {
    job_id: pending.job_id,
    status: waited.allPass ? "pass" : "fail",
    proof: pending.proof || null,
    runs: waited.results,
    waited_ms: waited.waited_ms,
    resumed: true,
    acceptance: pending.acceptance || null,
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
  const queueUrl =
    env.JOB_QUEUE_URL ||
    "https://raw.githubusercontent.com/Noetfield-Systems/sina-governance-SSOT/main/data/nf_commissioning_job_queue_v1.json";

  const observe = {
    at,
    surfaces: {
      sg_shadow: await probe(env.SG_SHADOW_HEALTH_URL),
      runtime_reality: await probe(env.RUNTIME_REALITY_URL),
      key_pointer: await probe(env.KEY_POINTER_URL),
      job_queue: await probe(queueUrl),
    },
  };

  const defects = detect(observe);
  const repairs = defects.map((d) => ({ defect: d.id, ...allowlistedRepair(d, observe) }));

  let lastFiredAt = null;
  if (env.RECEIPTS) lastFiredAt = await env.RECEIPTS.get("last_fired_at");

  const progress = await loadProgress(env);
  if (!progress.cycle) progress.cycle = 1;

  let selected = { index: progress.cursor || 0, job: null };
  let jobResult;

  // Resume in-flight Motor proof runs before starting a new job
  if (progress.pending?.run_ids?.length) {
    jobResult = await resumePendingJob(env, progress);
    const jobId = jobResult?.job_id || progress.pending.job_id;
    selected = {
      index: (jobQueue.jobs || []).findIndex((j) => j.id === jobId),
      job: (jobQueue.jobs || []).find((j) => j.id === jobId) || {
        id: jobId,
        class: "execute",
        runway_action: "dispatch_and_wait",
        acceptance: progress.pending.acceptance,
        proof: progress.pending.proof,
      },
    };
    if (selected.index < 0) selected.index = progress.cursor || 0;
  } else {
    selected = selectNextJob(progress);
    jobResult = await executeSelectedJob(env, selected.job, observe, lastFiredAt);
  }
  const job = selected.job;

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
        content: improve.content,
      };
    }
  }

  // Advance cursor only when job finished (pass/fail/blocked); hold cursor while pending
  const jobsLen = (jobQueue.jobs || []).length || 1;
  if (jobResult.status === "dispatched_pending") {
    progress.pending = {
      ...(jobResult.pending || {}),
      job_id: job?.id,
      proof: job?.proof || jobResult.proof || null,
      acceptance: job?.acceptance || null,
    };
  } else {
    progress.pending = null;
    const nextCursor = (selected.index + 1) % jobsLen;
    if (nextCursor === 0) progress.cycle = (progress.cycle || 1) + 1;
    progress.cursor = nextCursor;
  }
  progress.jobs = progress.jobs || {};
  if (job?.id) {
    progress.jobs[job.id] = {
      status: jobResult.status,
      at,
      cycle: progress.cycle,
      missing_decision: jobResult.missing_decision || null,
      runs: jobResult.runs || null,
      proof: jobResult.proof || job?.proof || null,
    };
  }
  progress.updated_at = at;

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
    source: meta.source || "on_demand",
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
      cursor: progress.cursor,
      cycle: progress.cycle,
      completed_this_cycle: Object.entries(progress.jobs || {})
        .filter(([, v]) => v.cycle === progress.cycle && v.status === "pass")
        .map(([id]) => id),
    },
    observe,
    defects,
    repairs,
    critique,
    propose_improve: proposal,
    model_keys_present: {
      deepseek: Boolean((env.DEEPSEEK_API_KEY || "").trim()),
      glm: Boolean((env.GLM_API_KEY || "").trim()),
      kimi: Boolean((env.MOONSHOT_API_KEY || "").trim()),
      huggingface: Boolean((env.HF_TOKEN || "").trim()),
    },
    verdict,
  };

  const runway_dispatch = await dispatchCommissioningRunway(env, receipt, job);
  receipt.runway_dispatch = runway_dispatch;
  repairs.push({
    defect: "runway_dispatch",
    applied: runway_dispatch.ok === true,
    action: "dispatch_commissioning_runway_job",
    result: runway_dispatch,
  });

  if (env.RECEIPTS) {
    await env.RECEIPTS.put(PROGRESS_KEY, JSON.stringify(progress));
    await env.RECEIPTS.put(CURSOR_KEY, String(progress.cursor));
    const key = `tick:${at}`;
    await env.RECEIPTS.put(key, JSON.stringify(receipt), { expirationTtl: 60 * 60 * 24 * 14 });
    await env.RECEIPTS.put("last_fired_at", at);
    await env.RECEIPTS.put("last_receipt", JSON.stringify(receipt));
    await env.RECEIPTS.put("last_job_id", job?.id || "");
  }

  return receipt;
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
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      let last = null;
      let lastJob = null;
      let cursor = null;
      if (env.RECEIPTS) {
        last = await env.RECEIPTS.get("last_fired_at");
        lastJob = await env.RECEIPTS.get("last_job_id");
        cursor = await env.RECEIPTS.get(CURSOR_KEY);
      }
      return json({
        ok: true,
        schema: SCHEMA + "-health",
        service: "nf-commissioning-specialist-tick-v1",
        trigger_mode: "on_demand",
        cron: null,
        schedule_enabled: false,
        dispatch_path:
          "NOETFIELD-RUNWAY/.github/workflows/commissioning-run.yml (workflow_dispatch or authorized repository_dispatch with job_id)",
        loop_id: env.LOOP_ID,
        last_fired_at: last,
        last_job_id: lastJob,
        job_queue_cursor: cursor,
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
    if (url.pathname === "/tick" && request.method === "POST") {
      return json(
        {
          ok: false,
          error: "perpetual_tick_disabled",
          trigger_mode: "on_demand",
          action:
            "Dispatch an explicit commissioning job through NOETFIELD-RUNWAY commissioning-run workflow.",
        },
        410,
      );
    }
    if (url.pathname === "/map") return json(mapDoc);
    if (url.pathname === "/queue") return json(jobQueue);
    if (url.pathname === "/progress" && env.RECEIPTS) {
      const raw = await env.RECEIPTS.get(PROGRESS_KEY);
      return json(raw ? JSON.parse(raw) : { cursor: 0, jobs: {} });
    }
    if (url.pathname === "/last" && env.RECEIPTS) {
      const raw = await env.RECEIPTS.get("last_receipt");
      return json(raw ? JSON.parse(raw) : { ok: false, error: "no_receipt_yet" });
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
