/*
 * web/scripts/build-skin-contact-sheet.cjs
 *
 * Compose the five per-skin crops into a single contact sheet.
 * Embeds crops as base64 data URIs so the page renders without
 * needing file:// access.
 */

const { chromium } = require('/home/opencode/tools/browser-qa/node_modules/playwright');
const fs = require('fs');

const OUT = '/tmp/sol-stage1b-skins-contact-sheet.png';
const SKINS = ['green', 'amber', 'cyan', 'red', 'violet'];

function b64(path) {
  return 'data:image/png;base64,' + fs.readFileSync(path).toString('base64');
}

const html = `<!doctype html><html><head><style>
html,body { margin:0; padding:0; background:#050705; }
body { display:grid; grid-template-columns: repeat(5, 1fr); gap:8px; padding:8px; }
figure { margin:0; display:flex; flex-direction:column; align-items:center; }
figcaption { color:#c9c3b0; font: 11px ui-monospace, "SFMono-Regular", Consolas, monospace;
            text-transform: uppercase; letter-spacing:.15em; padding:8px 0; }
img { width:100%; display:block; border:1px solid #36352c; }
</style></head><body>
${SKINS.map(
  (s) => `<figure><figcaption>${s}</figcaption><img src="${b64(`/tmp/sol-stage1b-skins-${s}-crop.png`)}"/></figure>`,
).join('\n')}
</body></html>`;

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/home/opencode/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome',
    args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars'],
  });
  const ctx = await browser.newContext({ viewport: { width: 1600, height: 720 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.setContent(html, { waitUntil: 'load' });
  await page.waitForTimeout(200);
  await page.screenshot({ path: OUT, fullPage: true });
  const stat = fs.statSync(OUT);
  console.log(`contact sheet: ${OUT} (${stat.size} bytes)`);
  await ctx.close();
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });