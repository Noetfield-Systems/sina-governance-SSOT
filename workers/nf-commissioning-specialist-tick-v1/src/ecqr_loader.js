const fs = require('fs').promises;
const path = require('path');

// loadECQRPortfolio: attempts in order to load a JSON portfolio (array)
// - explicit options.portfolioPath
// - environment NF_PORTFOLIO_PATH
// - deterministic repo-local candidate: ../ecqr_portfolio.json
// - fallback: existing static map.json in same directory
// Returns an array sorted by ECQR ascending (lower ECQR = preferred).
async function loadECQRPortfolio(options = {}) {
  const tried = [];
  const candidates = [];
  if (options.portfolioPath) candidates.push(options.portfolioPath);
  if (process.env.NF_PORTFOLIO_PATH) candidates.push(process.env.NF_PORTFOLIO_PATH);
  // deterministic local candidate (composable artifact location)
  candidates.push(path.join(__dirname, '..', 'ecqr_portfolio.json'));
  // final fallback: the repo-local static map.json that currently exists
  candidates.push(path.join(__dirname, 'map.json'));

  for (const candidate of candidates) {
    try {
      const raw = await fs.readFile(candidate, 'utf8');
      const parsed = JSON.parse(raw);
      // Accept either an array or object containing an array under common keys.
      const items = Array.isArray(parsed)
        ? parsed
        : parsed.items || parsed.portfolio || parsed.jobs || null;
      if (!items || !Array.isArray(items)) {
        // Not a portfolio array — continue searching.
        tried.push(candidate + ' -> not-array');
        continue;
      }
      return sortByECQR(items);
    } catch (err) {
      tried.push(candidate + ' -> ' + err.message);
      continue;
    }
  }
  // No portfolio found; return empty array (caller must handle no-op).
  return [];
}

function sortByECQR(items) {
  // Defensive: copy input and normalize ecqr field; lower is better
  return items.slice().sort((a, b) => {
    const aScore = typeof a.ecqr === 'number' ? a.ecqr : (typeof a.ECQR === 'number' ? a.ECQR : Number.POSITIVE_INFINITY);
    const bScore = typeof b.ecqr === 'number' ? b.ecqr : (typeof b.ECQR === 'number' ? b.ECQR : Number.POSITIVE_INFINITY);
    // stable numeric ascending
    if (aScore === bScore) return 0;
    return aScore < bScore ? -1 : 1;
  });
}

module.exports = { loadECQRPortfolio };
