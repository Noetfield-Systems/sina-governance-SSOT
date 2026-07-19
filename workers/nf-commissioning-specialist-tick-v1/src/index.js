// Commissioning specialist tick worker — ECQR-aware
// This file preserves previous behavior but replaces static map usage
// with an ECQR-preferred portfolio loader. Falls back to map.json unchanged.

const path = require('path');
const fs = require('fs');
const { loadECQRPortfolio } = require('./ecqr_loader');

// existing job-queue/dispatch helpers (lightweight, contained)
function dispatchJob(job) {
  // Minimal dispatch stub: in production this integrates with Motor/NOETFIELD-RUNWAY dispatch.
  // Keep intentionally simple and side-effect free for review; callers may replace wiring.
  console.log('[commissioning_tick] dispatching job:', job && job.id ? job.id : JSON.stringify(job));
}

async function mainTick() {
  // Try to load ECQR-ranked portfolio. Provide option to override path.
  const configuredPath = process.env.NF_PORTFOLIO_PATH || null;
  const portfolio = await loadECQRPortfolio({ portfolioPath: configuredPath });

  if (!portfolio || portfolio.length === 0) {
    console.warn('[commissioning_tick] no ECQR portfolio found; no-op. (map.json preserved as fallback)');
    return;
  }

  // Portfolio is sorted by ECQR ascending (lower is better). Select highest priority entry.
  const next = portfolio[0];
  if (!next) {
    console.warn('[commissioning_tick] portfolio empty after load; nothing to dispatch');
    return;
  }

  // Minimal validation of next item shape to avoid surprising dispatches.
  if (!next.id && !next.job) {
    console.warn('[commissioning_tick] portfolio item missing id/job; skipping:', next);
    return;
  }

  // Dispatch the selected job. In the full system this would mint a Motor token and call NOETFIELD-RUNWAY.
  dispatchJob(next);
}

// Export mainTick for unit testing and for the repository's existing cron wiring to call.
module.exports = { mainTick };

// If invoked directly, run one tick.
if (require.main === module) {
  mainTick().catch(err => {
    console.error('[commissioning_tick] tick failed:', err && err.stack ? err.stack : String(err));
    process.exit(1);
  });
}
