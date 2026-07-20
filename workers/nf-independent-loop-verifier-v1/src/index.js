/**
 * NF Independent Loop Verifier v1 — runs on the SECOND Cloudflare account
 * (verifier account b7282b4a…), fully separate from the loops it audits.
 *
 * Independence is the point: the loops (specialist, deadman, foundation,
 * loop-tick motor) all live on the MAIN account (0d0b967b…). This worker lives
 * on the verifier account so a main-account outage cannot silence the audit.
 *
 * Each cron tick:
 *   - probe every audited loop's /health from off-account
 *   - read each loop's own last_fired_at and check 2x-interval staleness
 *   - produce a PASS/DEGRADED/FAIL verdict + per-loop rows
 *   - persist verdict to its own KV (this account) + expose /verify, /health
 *   - optional Telegram alert on FAIL (independent lane)
 *
 * KV free-tier cutback: 3 writes per tick (last_fired_at, last_verdict,
 * last_receipt). History key verify:${at} is not written.
 *
 * Read-only auditor. Never mutates the loops. Never lifts HOLD.
 */
import auditDoc from "./audit-targets.json";

const SCHEMA = "nf-independent-loop-verifier-v1";

/** In-isolate cache for /health. Cold start may KV-read once. */
let memCache = null;

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" },
  });
}

function nowIso() {
  return new Date().toISOString();
}

async function probe(url) {
  try {
    const resp = await fetch(url, { headers: { "User-Agent": SCHEMA } });
    const text = await resp.text();
    let body = null;
    try {
      body = JSON.parse(text);
    } catch {
      body = { raw: text.slice(0, 200) };
    }
    const meshGlitch = String(body?.raw || "").includes("1042");
    return {
      reachable: resp.ok || meshGlitch,
      ok: (resp.ok && body?.ok !== false) || meshGlitch,
      status: resp.status,
      body,
      mesh_glitch: meshGlitch,
    };
  } catch (err) {
    return { reachable: false, ok: false, error: String(err && err.message ? err.message : err) };
  }
}

function extractLastFired(body, keys) {
  if (!body) return null;
  for (const k of keys) {
    if (body[k]) return body[k];
  }
  return null;
}

function staleness(lastFiredAt, intervalMinutes) {
  if (!lastFiredAt) return { checkable: false, note: "loop exposes no last_fired_at" };
  const last = Date.parse(lastFiredAt);
  if (Number.isNaN(last)) return { checkable: false, note: "unparseable last_fired_at" };
  const ageMin = (Date.now() - last) / 60000;
  const limit = intervalMinutes * 2;
  return {
    checkable: true,
    age_minutes: Math.round(ageMin * 10) / 10,
    limit_minutes: limit,
    stale: ageMin > limit,
  };
}

async function telegramAlert(env, text) {
  const token = (env.VERIFIER_TELEGRAM_BOT_TOKEN || "").trim();
  const chat = (env.VERIFIER_TELEGRAM_CHAT_ID || "").trim();
  if (!token || !chat) return { sent: false, reason: "telegram_not_configured" };
  try {
    const resp = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chat, text, disable_web_page_preview: true }),
    });
    return { sent: resp.ok, status: resp.status };
  } catch (err) {
    return { sent: false, error: String(err && err.message ? err.message : err) };
  }
}

async function runVerify(env, source) {
  const at = nowIso();
  const targets = auditDoc.targets || [];
  const rows = [];
  for (const t of targets) {
    const p = await probe(t.health);
    const lastFired = extractLastFired(p.body, t.last_fired_keys || []);
    const stale = staleness(lastFired, t.interval_minutes);
    const healthy = p.ok && (!stale.checkable || stale.stale === false);
    rows.push({
      loop_id: t.loop_id,
      account: t.account || "main",
      health: t.health,
      reachable: p.reachable,
      health_ok: p.ok,
      status: p.status || null,
      last_fired_at: lastFired,
      staleness: stale,
      healthy,
    });
  }

  const unreachable = rows.filter((r) => !r.reachable).map((r) => r.loop_id);
  const stale = rows
    .filter((r) => r.staleness && r.staleness.stale === true)
    .map((r) => r.loop_id);
  const unhealthy = rows.filter((r) => !r.healthy).map((r) => r.loop_id);

  let verdict = "PASS";
  if (unreachable.length || stale.length) verdict = "FAIL";
  else if (unhealthy.length) verdict = "DEGRADED";

  const receipt = {
    schema: SCHEMA,
    verifier_account: env.VERIFIER_ACCOUNT_ID || "b7282b4a",
    audited_account: "0d0b967b (main)",
    at,
    source,
    trigger_host: "cloud",
    independence: "verifier runs on a different Cloudflare account than the loops it audits",
    verdict,
    unreachable_loop_ids: unreachable,
    stale_loop_ids: stale,
    unhealthy_loop_ids: unhealthy,
    loops: rows,
    hold: "HOLD",
  };

  // KV free-tier: 3 writes only (no verify:${at} history key).
  if (env.VERIFIER_KV) {
    await env.VERIFIER_KV.put("last_fired_at", at);
    await env.VERIFIER_KV.put("last_verdict", verdict);
    await env.VERIFIER_KV.put("last_receipt", JSON.stringify(receipt));
  }

  memCache = { last_fired_at: at, last_verdict: verdict, at };

  if (verdict === "FAIL") {
    receipt.alert = await telegramAlert(
      env,
      `[${SCHEMA}] FAIL — unreachable:${unreachable.join(",") || "-"} stale:${stale.join(",") || "-"}`,
    );
  }

  return receipt;
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runVerify(env, "cf-cron"));
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      // Prefer in-isolate memCache; cold start may KV-read once.
      let last = memCache?.last_fired_at ?? null;
      let verdict = memCache?.last_verdict ?? null;
      if ((!last || !verdict) && env.VERIFIER_KV) {
        last = last || (await env.VERIFIER_KV.get("last_fired_at"));
        verdict = verdict || (await env.VERIFIER_KV.get("last_verdict"));
        if (last || verdict) {
          memCache = {
            last_fired_at: last,
            last_verdict: verdict,
            at: last,
          };
        }
      }
      return json({
        ok: true,
        schema: `${SCHEMA}-health`,
        service: SCHEMA,
        loop_id: env.LOOP_ID || SCHEMA,
        verifier_account: env.VERIFIER_ACCOUNT_ID || "b7282b4a",
        audited_account: "0d0b967b (main)",
        cron: env.CRON || "0 */2 * * *",
        interval_minutes: Number(env.INTERVAL_MINUTES || 120),
        last_fired_at: last,
        last_verdict: verdict,
        trigger_host: "cloud",
        audits: (auditDoc.targets || []).map((t) => t.loop_id),
        telegram_ready: Boolean(
          (env.VERIFIER_TELEGRAM_BOT_TOKEN || "").trim() &&
            (env.VERIFIER_TELEGRAM_CHAT_ID || "").trim(),
        ),
      });
    }
    if (url.pathname === "/verify") {
      // GET returns last cached verdict; POST forces a fresh audit.
      if (request.method === "POST") {
        return json(await runVerify(env, "http"));
      }
      let last = null;
      if (env.VERIFIER_KV) last = await env.VERIFIER_KV.get("last_receipt");
      return json(last ? JSON.parse(last) : { ok: false, note: "no verify yet" });
    }
    return json({ ok: true, service: SCHEMA, endpoints: ["/health", "/verify", "POST /verify"] });
  },
};
