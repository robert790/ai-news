#!/usr/bin/env node
/*
 * web/scripts/capture-visual-baseline.cjs
 *
 * Deterministic visual-regression capture for the OpenRadar Home
 * freeze. Produces byte-identical PNGs across runs by:
 *   - forcing prefers-reduced-motion: reduce on the browser context
 *   - setting CDP Animation.playbackRate to 0 (belt-and-braces)
 *   - waiting for networkidle + a fixed 250 ms paint settle
 *   - using deviceScaleFactor: 2 to match the committed baseline PNGs
 *
 * Usage (from repo root):
 *   1. Build + serve the Home on a local port:
 *        cd web && npx next build && npx next start -p 3085
 *   2. In another shell:
 *        node web/scripts/capture-visual-baseline.cjs \
 *          --base http://127.0.0.1:3085 \
 *          --out  /tmp/sol-component \
 *          --viewport 1440x1378 \
 *          --name 1440
 *        node web/scripts/capture-visual-baseline.cjs \
 *          --base http://127.0.0.1:3085 \
 *          --out  /tmp/sol-component \
 *          --viewport 393x939 \
 *          --name 393
 *   3. Compare to the frozen baseline:
 *        python3 web/scripts/png-diff.py \
 *          /tmp/sol-frozen-1440.png /tmp/sol-component-1440.png \
 *          /tmp/sol-frozen-393.png  /tmp/sol-component-393.png
 *
 * Required env / deps (not declared in web/package.json so this
 * script never ends up in a production bundle):
 *   - /home/opencode/tools/browser-qa/node_modules/playwright
 *   - /home/opencode/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome
 * Override either with env vars PLAYWRIGHT_PATH and CHROME_PATH.
 */

const path = require('path');
const fs = require('fs');

function parseArgs(argv) {
  const out = {
    base: 'http://127.0.0.1:3085',
    out: '/tmp/sol-component',
    viewport: '1440x1378',
    name: '1440',
    chrome: process.env.CHROME_PATH ||
      '/home/opencode/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome',
    playwright: process.env.PLAYWRIGHT_PATH ||
      '/home/opencode/tools/browser-qa/node_modules/playwright',
    settleMs: 250,
  };
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (!arg.startsWith('--')) continue;
    const eq = arg.indexOf('=');
    let key, v;
    if (eq >= 0) {
      key = arg.slice(0, eq);
      v = arg.slice(eq + 1);
    } else {
      key = arg;
      v = argv[i + 1];
      i++;
    }
    key = key.slice(2);
    if (key === 'base' && v) out.base = v;
    else if (key === 'out' && v) out.out = v;
    else if (key === 'viewport' && v) out.viewport = v;
    else if (key === 'name' && v) out.name = v;
    else if (key === 'chrome' && v) out.chrome = v;
    else if (key === 'settleMs' && v) out.settleMs = parseInt(v, 10);
  }
  return out;
}

async function main() {
  const cfg = parseArgs(process.argv);
  const [width, height] = cfg.viewport.split('x').map(Number);
  if (!width || !height) {
    console.error(`bad --viewport: ${cfg.viewport}`);
    process.exit(1);
  }

  const playwright = require(cfg.playwright);
  const out = `${cfg.out}-${cfg.name}.png`;

  const browser = await playwright.chromium.launch({
    headless: true,
    executablePath: cfg.chrome,
    args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars'],
  });
  const ctx = await browser.newContext({
    viewport: { width, height },
    deviceScaleFactor: 2,
    reducedMotion: 'reduce',
  });
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Animation.enable');
  await cdp.send('Animation.setPlaybackRate', { playbackRate: 0 });
  await page.goto(`${cfg.base}/`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(cfg.settleMs);
  await page.screenshot({ path: out, fullPage: false });
  await ctx.close();
  await browser.close();

  const stat = fs.statSync(out);
  console.log(`${cfg.name} ${width}x${height} -> ${out} (${stat.size} bytes)`);
}

main().catch((e) => { console.error(e); process.exit(1); });