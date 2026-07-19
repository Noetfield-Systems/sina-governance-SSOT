/**
 * NF SG Loop Tick v1 — Cloudflare cron motor.
 *
 * Cloud-first replacement for two former GitHub-Actions cron loops:
 *   1. key2-custody watch (was hourly GHA)
 *   2. 48h living-system liveness closeout (was hourly GHA)
 *
 * Each cron tick:
 *   Observe  -> probe every registered loop /health
 *   Detect   -> stale-loop + key2-custody detection
 *   Act      -> when key1 bootstrap key is finally dead + key2 alive, fire a
 *               one-shot repository_dispatch (key2_custody_established) so the
 *               apply job runs; when 48h window closes, fire liveness_48h_close.
 *   Record   -> upsert last_fired_at + full snapshot to KV; expose /status.
 *
 * GitHub is NEVER the recurring motor here — Cloudflare cron is. GHA only runs
 * one-shot apply jobs triggered by these dispatches.
 *
 * HOLD preserved. Never mints keys. Never claims FULLY_COMMISSIONED.
 */
import loopsDoc from "./loops.json";

const SCHEMA = "nf-sg-loop-tick-v1";
const APP_ID = 4330805; // noetfield-sg-authority
const KEY1_FP = "5d75d4e187747d65f459bd1d15ec8005c4477f65c0ccb9d8431599a35f4c436b";
const KEY2_FP = "22a9513a3aaee95266538a5fc49c94a4591119d14fe9332f2964fd603817c3a8";

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" },
  });
}

function nowIso() {
  return new Date().toISOString();
}

/* ---------- crypto / github helpers (WebCrypto RS256) ---------- */

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

function toB64Url(buf) {
  let s = "";
  const bytes = buf instanceof ArrayBuffer ? new Uint8Array(buf) : buf;
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

async function importSigningKey(pem) {
  return crypto.subtle.importKey(
    "pkcs8",
    pemToArrayBuffer(pem),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
}

async function mintAppJwt(pem) {
  const now = Math.floor(Date.now() / 1000);
  const enc = new TextEncoder();
  const header = toB64Url(enc.encode(JSON.stringify({ alg: "RS256", typ: "JWT" })));
  const payload = toB64Url(
    enc.encode(JSON.stringify({ iat: now - 60, exp: now + 540, iss: APP_ID })),
  );
  const key = await importSigningKey(pem);
  const sig = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    key,
    enc.encode(`${header}.${payload}`),
  );
  return `${header}.${payload}.${toB64Url(sig)}`;
}

async function appAuthOk(pem) {
  if (!pem) return { present: false, ok: false };
  try {
    const jwt = await mintAppJwt(pem);
    const resp = await fetch("https://api.github.com/app", {
      headers: {
        Authorization: `Bearer ${jwt}`,
        Accept: "application/vnd.github+json",
        "User-Agent": SCHEMA,
        "X-GitHub-Api-Version": "2022-11-28",
      },
    });
    return { present: true, ok: resp.status === 200, status: resp.status };
  } catch (err) {
    return { present: true, ok: false, error: String(err && err.message ? err.message : err) };
  }
}

async function mintMotorInstallationToken(env) {
  const pem = (env.MOTOR_APP_PRIVATE_KEY || "").trim();
  if (!pem) return null;
  const appId = String(env.MOTOR_APP_ID || "4275961").trim();
  const now = Math.floor(Date.now() / 1000);
  const enc = new TextEncoder();
  const header = toB64Url(enc.encode(JSON.stringify({ alg: "RS256", typ: "JWT" })));
  const payload = toB64Url(
    enc.encode(JSON.stringify({ iat: now - 60, exp: now + 540, iss: Number(appId) })),
  );
  const key = await importSigningKey(pem);
  const sig = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    key,
    enc.encode(`${header}.${payload}`),
  );
  const jwt = `${header}.${payload}.${toB64Url(sig)}`;
  const installId = String(env.MOTOR_INSTALLATION_ID || "145975487").trim();
  const tokRes = await fetch(
    `https://api.github.com/app/installations/${installId}/access_tokens`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${jwt}`,
        Accept: "application/vnd.github+json",
        "User-Agent": SCHEMA,
        "X-GitHub-Api-Version": "2022-11-28",
      },
    },
  );
  if (!tokRes.ok) return null;
  const tok = await tokRes.json();
  return tok.token || null;
}

async function repositoryDispatch(env, eventType, clientPayload) {
  const repo = (env.SG_REPO || "Noetfield-Systems/sina-governance-SSOT").trim();
  const token = await mintMotorInstallationToken(env);
  if (!token) return { ok: false, error: "motor token mint failed — dispatch skipped" };
  const resp = await fetch(`https://api.github.com/repos/${repo}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": SCHEMA,
      "X-GitHub-Api-Version": "2022-11-28",
    },
    body: JSON.stringify({ event_type: eventType, client_payload: clientPayload || {} }),
  });
  return { ok: resp.status === 204, status: resp.status, repo, event_type: eventType };
}

/* ---------- probes ---------- */

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
    // CF worker mesh glitch (1042) is treated as transient-ok
    const meshGlitch = String(body?.raw || "").includes("1042");
    return { ok: (resp.ok && body?.ok !== false) || meshGlitch, status: resp.status, body };
  } catch (err) {
    return { ok: false, error: String(err && err.message ? err.message : err) };
  }
}

function staleness(lastFiredAt, intervalMinutes) {
  if (!lastFiredAt) return { stale: null, note: "no last_fired_at exposed" };
  const last = Date.parse(lastFiredAt);
  if (Number.isNaN(last)) return { stale: null, note: "unparseable last_fired_at" };
  const ageMin = (Date.now() - last) / 60000;
  const limit = intervalMinutes * 2;
  return { stale: ageMin > limit, age_minutes: Math.round(ageMin * 10) / 10, limit_minutes: limit };
}

/* ---------- key2 custody ---------- */

async function key2Custody(env) {
  const key1 = await appAuthOk((env.SG_BOOTSTRAP_KEY_1_PEM || "").trim());
  const key2 = await appAuthOk((env.SG_AUTHORITY_PRIVATE_KEY || "").trim());
  const ready = key1.present && !key1.ok && key2.present && key2.ok;
  return {
    key1_present: key1.present,
    key1_auth_ok: key1.ok,
    key2_present: key2.present,
    key2_auth_ok: key2.ok,
    ready,
    verdict: !key2.present
      ? "KEY2_SECRET_MISSING"
      : ready
        ? "KEY2_READY"
        : key1.ok
          ? "BLOCKED_FOUNDER"
          : "KEY2_GAP",
    key1_fp: KEY1_FP.slice(0, 12),
    key2_fp: KEY2_FP.slice(0, 12),
  };
}

/* ---------- 48h liveness window ---------- */

async function liveness48h(env, loopResults) {
  const startedAt = (env.LIVENESS_48H_STARTED_AT || "").trim();
  if (!startedAt) return { tracked: false, note: "LIVENESS_48H_STARTED_AT not set" };
  const started = Date.parse(startedAt);
  if (Number.isNaN(started)) return { tracked: false, note: "unparseable start" };
  const elapsedH = (Date.now() - started) / 3600000;
  const allOk = loopResults.every((l) => l.health_ok);
  const windowClosed = elapsedH >= 48;
  return {
    tracked: true,
    started_at: startedAt,
    elapsed_hours: Math.round(elapsedH * 100) / 100,
    window_closed: windowClosed,
    all_loops_ok: allOk,
    verdict: windowClosed ? (allOk ? "PASS" : "FAIL") : "WINDOW_OPEN",
  };
}

/* ---------- tick ---------- */

async function runTick(env, source) {
  const at = nowIso();
  const loops = loopsDoc.loops || [];
  const loopResults = [];
  for (const loop of loops) {
    const p = await probe(loop.health);
    const lastKey = loop.last_fired_key;
    const lastFired = lastKey && p.body ? p.body[lastKey] : null;
    const stale = lastFired ? staleness(lastFired, loop.interval_minutes) : { stale: null };
    loopResults.push({
      loop_id: loop.loop_id,
      health: loop.health,
      health_ok: p.ok,
      status: p.status || null,
      last_fired_at: lastFired || null,
      interval_minutes: loop.interval_minutes,
      staleness: stale,
    });
  }

  const custody = await key2Custody(env);
  const liveness = await liveness48h(env, loopResults);

  const actions = [];

  // One-shot: key2 established -> dispatch apply job (GitHub is NOT a recurring
  // tick here; this fires exactly once when key1 dies).
  if (custody.ready && env.RECEIPTS) {
    const alreadyFired = await env.RECEIPTS.get("key2_dispatch_fired");
    if (!alreadyFired) {
      const d = await repositoryDispatch(env, "key2_custody_established", {
        source: "cf-cron",
        at,
        key2_fp: custody.key2_fp,
      });
      actions.push({ action: "dispatch_key2_established", ...d });
      if (d.ok) await env.RECEIPTS.put("key2_dispatch_fired", at);
    } else {
      actions.push({ action: "dispatch_key2_established", skipped: "already_fired", at: alreadyFired });
    }
  }

  // One-shot: 48h window closed -> dispatch closeout apply job.
  if (liveness.tracked && liveness.window_closed && env.RECEIPTS) {
    const alreadyFired = await env.RECEIPTS.get("liveness_48h_dispatch_fired");
    if (!alreadyFired) {
      const d = await repositoryDispatch(env, "liveness_48h_close", {
        source: "cf-cron",
        at,
        verdict: liveness.verdict,
      });
      actions.push({ action: "dispatch_liveness_48h_close", ...d });
      if (d.ok) await env.RECEIPTS.put("liveness_48h_dispatch_fired", at);
    }
  }

  const staleLoops = loopResults.filter((l) => l.staleness && l.staleness.stale === true);
  const allHealthy = loopResults.every((l) => l.health_ok);

  const receipt = {
    schema: SCHEMA,
    loop_id: env.LOOP_ID || SCHEMA,
    at,
    source,
    trigger_host: "cloud",
    hold: env.AUTONOMOUS_PRODUCTION_MUTATIONS || "HOLD",
    all_loops_healthy: allHealthy,
    stale_loop_ids: staleLoops.map((l) => l.loop_id),
    key2_custody: custody,
    liveness_48h: liveness,
    actions,
    loops: loopResults,
  };

  if (env.RECEIPTS) {
    await env.RECEIPTS.put("last_fired_at", at);
    await env.RECEIPTS.put("last_receipt", JSON.stringify(receipt));
    await env.RECEIPTS.put(
      `receipt:${at}`,
      JSON.stringify(receipt),
      { expirationTtl: 60 * 60 * 24 * 14 },
    );
  }
  return receipt;
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runTick(env, "cf-cron"));
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      let last = null;
      if (env.RECEIPTS) last = await env.RECEIPTS.get("last_fired_at");
      return json({
        ok: true,
        schema: `${SCHEMA}-health`,
        service: SCHEMA,
        loop_id: env.LOOP_ID || SCHEMA,
        cron: env.CRON || "*/10 * * * *",
        interval_minutes: Number(env.INTERVAL_MINUTES || 10),
        last_fired_at: last,
        trigger_host: "cloud",
        hold: env.AUTONOMOUS_PRODUCTION_MUTATIONS || "HOLD",
        watches: (loopsDoc.loops || []).map((l) => l.loop_id),
        motor_key_secrets_present: {
          key1_bootstrap: Boolean((env.SG_BOOTSTRAP_KEY_1_PEM || "").trim()),
          key2_authority: Boolean((env.SG_AUTHORITY_PRIVATE_KEY || "").trim()),
          motor_app: Boolean((env.MOTOR_APP_PRIVATE_KEY || "").trim()),
        },
      });
    }
    if (url.pathname === "/status") {
      let last = null;
      if (env.RECEIPTS) last = await env.RECEIPTS.get("last_receipt");
      return json(last ? JSON.parse(last) : { ok: false, note: "no tick yet" });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const receipt = await runTick(env, "http");
      return json(receipt);
    }
    return json({ ok: true, service: SCHEMA, endpoints: ["/health", "/status", "POST /tick"] });
  },
};
