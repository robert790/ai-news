/*
 * web/scripts/capture-skin-proof.cjs
 *
 * Capture a compact 5-skin contact sheet proving each of the five
 * accent presets visibly changes the radar/CTA/status region. The
 * data-skin attribute is injected client-side via page.evaluate()
 * after navigation — the production code is untouched. No temporary
 * app route or debug UI is required.
 *
 * Output:
 *   /tmp/sol-stage1b-skins-<skin>-<region>.png
 *   /tmp/sol-stage1b-skins-contact-sheet.png
 *
 * Where <region> is one of:
 *   - "desktop" (1440x1378, full page, no crop)
 *   - "crop"    (single radar+CTA+status crop)
 *
 * Usage:
 *   1. Build + serve:  cd web && npx next build && npx next start -p 3173
 *   2. Run:            node web/scripts/capture-skin-proof.cjs
 */

const playwright = require('/home/opencode/tools/browser-qa/node_modules/playwright');
const fs = require('fs');

const BASE = process.env.BASE || 'http://127.0.0.1:3184';
const CHROME = '/home/opencode/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome';
const OUT = '/tmp';

const SKINS = ['green', 'amber', 'cyan', 'red', 'violet'];

(async () => {
  const browser = await playwright.chromium.launch({
    headless: true,
    executablePath: CHROME,
    args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars'],
  });
  for (const skin of SKINS) {
    const ctx = await browser.newContext({
      viewport: { width: 1440, height: 1378 },
      deviceScaleFactor: 2,
      reducedMotion: 'reduce',
    });
    const page = await ctx.newPage();
    const cdp = await ctx.newCDPSession(page);
    await cdp.send('Animation.enable');
    await cdp.send('Animation.setPlaybackRate', { playbackRate: 0 });
    await page.goto(BASE + '/', { waitUntil: 'networkidle' });
    // Inject data-skin on <html> so the cascade re-targets accents
    // without touching the production HTML.
    await page.evaluate((skin) => {
      document.documentElement.setAttribute('data-skin', skin);
    }, skin);
    await page.waitForTimeout(150);
    await page.screenshot({ path: `${OUT}/sol-stage1b-skins-${skin}-desktop.png`, fullPage: false });
    // Crop: radar rig + primary CTA + status rail (single composite proof region)
    const cropPath = `${OUT}/sol-stage1b-skins-${skin}-crop.png`;
    // CSS coords from freeze analysis: hero deck spans full width below top-deck.
    // Top deck ~95px, hero-deck ~430px, status-rail ~68px. Crop a generous band.
    await page.screenshot({
      path: cropPath,
      clip: { x: 0, y: 95, width: 1440, height: 600 },
    });
    const desktopStat = fs.statSync(`${OUT}/sol-stage1b-skins-${skin}-desktop.png`);
    const cropStat = fs.statSync(cropPath);
    console.log(`${skin}: desktop=${desktopStat.size} bytes, crop=${cropStat.size} bytes`);
    await ctx.close();
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });