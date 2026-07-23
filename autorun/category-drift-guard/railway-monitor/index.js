// Dead-man's-switch monitor for the category-drift-guard.
//
// This is the ONE role in the architecture no other service can fill: an
// independently-scheduled runtime (Railway, not GHA) that notices when the
// whole pipeline goes SILENT — GHA cron never enabled, Actions outage,
// billing/quota issue, Cloudflare Worker down. Nothing else in this stack
// detects "nothing happened when something should have" from the outside.
//
// Read-only: this service only GETs the Cloudflare Worker's status
// endpoint. It never writes to the registry, the Worker, or Supabase.

import http from "node:http";

const WORKER_URL = process.env.CATEGORY_DRIFT_VERIFIER_URL || "";
const MAX_AGE_HOURS = Number(process.env.MAX_AGE_HOURS || 24 * 9); // weekly job + 2-day buffer
const POLL_INTERVAL_MS = Number(process.env.POLL_INTERVAL_MS || 6 * 60 * 60 * 1000); // every 6h
const ALERT_WEBHOOK_URL = process.env.ALERT_WEBHOOK_URL || ""; // founder wires this in Phase 2

let lastCheck = { ok: null, checked_at: null, detail: null };

async function checkFreshness() {
  const checkedAt = new Date().toISOString();
  if (!WORKER_URL) {
    lastCheck = { ok: null, checked_at: checkedAt, detail: "CATEGORY_DRIFT_VERIFIER_URL not configured" };
    return;
  }
  try {
    const res = await fetch(`${WORKER_URL}/category-drift/latest`, { method: "GET" });
    if (!res.ok) {
      lastCheck = { ok: false, checked_at: checkedAt, detail: `verifier returned HTTP ${res.status}` };
      await maybeAlert(`category-drift-verifier unreachable or unhealthy: HTTP ${res.status}`);
      return;
    }
    const body = await res.json();
    const submittedCheckedAt = body?.submitted_receipt?.checked_at;
    if (!submittedCheckedAt) {
      lastCheck = { ok: false, checked_at: checkedAt, detail: "no submitted_receipt.checked_at in latest verified receipt" };
      await maybeAlert("category-drift-verifier has no valid latest receipt");
      return;
    }
    const ageHours = (Date.now() - new Date(submittedCheckedAt).getTime()) / 3_600_000;
    const stale = ageHours > MAX_AGE_HOURS;
    lastCheck = {
      ok: !stale,
      checked_at: checkedAt,
      detail: stale
        ? `STALE: last drift-check receipt is ${ageHours.toFixed(1)}h old (max ${MAX_AGE_HOURS}h) — the whole pipeline may be silent`
        : `fresh: last receipt ${ageHours.toFixed(1)}h old`,
    };
    if (stale) await maybeAlert(lastCheck.detail);
  } catch (err) {
    lastCheck = { ok: false, checked_at: checkedAt, detail: `fetch failed: ${err.message}` };
    await maybeAlert(`category-drift-verifier fetch failed: ${err.message}`);
  }
}

async function maybeAlert(message) {
  if (!ALERT_WEBHOOK_URL) {
    console.error(`[ALERT, no webhook configured] ${message}`);
    return;
  }
  try {
    await fetch(ALERT_WEBHOOK_URL, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ source: "category-drift-guard-railway-monitor", message, at: new Date().toISOString() }),
    });
  } catch (err) {
    console.error(`alert webhook delivery failed: ${err.message}`);
  }
}

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ service: "category-drift-guard-railway-monitor", status: "up" }));
    return;
  }
  if (req.url === "/status") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify(lastCheck));
    return;
  }
  res.writeHead(404, { "content-type": "application/json" });
  res.end(JSON.stringify({ error: "not found", endpoints: ["/health", "/status"] }));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`category-drift-guard-railway-monitor listening on :${PORT}`);
  checkFreshness();
  setInterval(checkFreshness, POLL_INTERVAL_MS);
});
