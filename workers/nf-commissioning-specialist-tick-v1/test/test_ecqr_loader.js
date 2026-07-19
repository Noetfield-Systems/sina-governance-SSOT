// Simple unit test for ecqr_loader.loadECQRPortfolio
// Usage: run with `node test_ecqr_loader.js` from this directory or have CI run it.

const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { loadECQRPortfolio } = require('../src/ecqr_loader');

async function run() {
  const tmpPath = path.join(__dirname, 'tmp_portfolio.json');
  const sample = [
    { id: 'job-a', ecqr: 12.5 },
    { id: 'job-b', ecqr: 3.1 },
    { id: 'job-c', ecqr: 8.0 }
  ];
  fs.writeFileSync(tmpPath, JSON.stringify(sample), 'utf8');

  try {
    const loaded = await loadECQRPortfolio({ portfolioPath: tmpPath });
    assert(Array.isArray(loaded), 'loaded should be array');
    // After sorting ascending by ecqr, job-b (3.1) should be first
    assert.strictEqual(loaded[0].id, 'job-b', 'expected job-b first after ECQR sort');
    assert.strictEqual(loaded[1].id, 'job-c');
    assert.strictEqual(loaded[2].id, 'job-a');

    console.log('[test_ecqr_loader] PASS');
  } catch (err) {
    console.error('[test_ecqr_loader] FAIL', err && err.stack ? err.stack : err);
    process.exit(2);
  } finally {
    try { fs.unlinkSync(tmpPath); } catch (_) {}
  }
}

if (require.main === module) run();
