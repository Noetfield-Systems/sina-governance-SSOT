/**
 * NF Commissioning Specialist Tick v1
 * Cloudflare cron every 5 minutes - closed loop:
 * Observe, Detect, Critique, Repair(allowlist), ProposeImprove, ReObserve
 *
 * Models (failover): DeepSeek, GLM, Kimi(Moonshot), Hugging Face
 * Machine may repair only allowlisted actions.
 * Machine may propose improvements only - founder ratifies architecture.
 * HOLD / no enforcement / no unsupervised redesign.
 */
import mapDoc from "./map.json";

const SCHEMA = "nf-commissioning-specialist-tick-v1";

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
          max_tokens: 400,
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
      return { ok: true, provider: name, model: p.model, content: String(content).slice(0, 2000) };
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
    defects.push({
      id: "shadow_unreachable",
      severity: "P1",
      repair: "reprobe_shadow",
    });
  } else if (shadow.body?.enforcement_enabled === true) {
    defects.push({
      id: "enforcement_unexpectedly_on",
      severity: "P0",
      repair: null,
      note: "HOLD law — flag only, do not auto-enable or disable via this loop",
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

async function runTick(env, meta = {}) {
  const at = new Date().toISOString();
  const observe = {
    at,
    surfaces: {
      sg_shadow: await probe(env.SG_SHADOW_HEALTH_URL),
      runtime_reality: await probe(env.RUNTIME_REALITY_URL),
      key_pointer: await probe(env.KEY_POINTER_URL),
    },
  };

  const defects = detect(observe);
  const repairs = defects.map((d) => ({ defect: d.id, ...allowlistedRepair(d, observe) }));

  let critique = { ok: false, skipped: true, reason: "no_defects_or_t0_only" };
  if (defects.length) {
    critique = await chatComplete(
      env,
      "You are the Noetfield commissioning specialist. Classify defects. Reply JSON only: {summary, severity, next_safe_action}. Never recommend minting new App keys, lifting HOLD, or unsupervised architecture redesign.",
      JSON.stringify({ defects, observe_ok: {
        shadow: observe.surfaces.sg_shadow?.ok,
        reality: observe.surfaces.runtime_reality?.ok,
        pointer: observe.surfaces.key_pointer?.ok,
      } }),
    );
  }

  let proposal = null;
  if (defects.some((d) => d.severity === "P1" || d.severity === "P0")) {
    const improve = await chatComplete(
      env,
      "Propose ONE machine-safe kaizen improvement for commissioning liveness. JSON only: {title, why, machine_safe:true|false, needs_founder:true|false}. No architecture redesign. No HOLD removal.",
      JSON.stringify({ defects: defects.map((d) => d.id), map_version: mapDoc.version }),
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

  const receipt = {
    schema: SCHEMA,
    loop_id: env.LOOP_ID || mapDoc.loop_id,
    at,
    source: meta.source || "cf-cron",
    cron: meta.cron || "*/5 * * * *",
    mode: env.MODE || "COMMISSIONING_SPECIALIST",
    hold: env.AUTONOMOUS_PRODUCTION_MUTATIONS || "HOLD",
    enforcement_enabled: false,
    map_version: mapDoc.version,
    skills: mapDoc.skills,
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
    verdict: defects.some((d) => d.severity === "P0")
      ? "FAIL_P0"
      : defects.length
        ? "DEGRADED_HEALING"
        : "PASS_SCOPED_TICK",
  };

  if (env.RECEIPTS) {
    const key = `tick:${at}`;
    await env.RECEIPTS.put(key, JSON.stringify(receipt), { expirationTtl: 60 * 60 * 24 * 14 });
    await env.RECEIPTS.put("last_fired_at", at);
    await env.RECEIPTS.put("last_receipt", JSON.stringify(receipt));
  }

  return receipt;
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(
      runTick(env, { source: "cf-cron", cron: event?.cron || "*/5 * * * *" }).then((r) => {
        console.log(JSON.stringify({ schema: SCHEMA, ok: true, verdict: r.verdict, at: r.at }));
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
      if (env.RECEIPTS) {
        last = await env.RECEIPTS.get("last_fired_at");
      }
      return json({
        ok: true,
        schema: SCHEMA + "-health",
        service: "nf-commissioning-specialist-tick-v1",
        cron: "*/5 * * * *",
        loop_id: env.LOOP_ID,
        last_fired_at: last,
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
      const receipt = await runTick(env, { source: "http_tick" });
      return json(receipt, receipt.verdict === "FAIL_P0" ? 500 : 200);
    }
    if (url.pathname === "/map") {
      return json(mapDoc);
    }
    if (url.pathname === "/last" && env.RECEIPTS) {
      const raw = await env.RECEIPTS.get("last_receipt");
      return json(raw ? JSON.parse(raw) : { ok: false, error: "no_receipt_yet" });
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
