/* Real browser interaction/layout checks. Run npm run test:browser (see QA.md). */
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const AxeBuilder = require('@axe-core/playwright').default;
const root = path.join(__dirname, '..');
const output = path.join(root, '.qa-ui');
const articleCount = JSON.parse(fs.readFileSync(path.join(root, 'public/articles.json'), 'utf8')).length;
fs.mkdirSync(output, {recursive: true});
const checks = [], errors = [], audits = [];
const server = spawn('python3', ['scripts/preview.py', '--port', '0'], {cwd: root, stdio: ['ignore', 'pipe', 'pipe']});
let browser;
const check = (name, condition) => { assert.ok(condition, name); checks.push(name); };
const loaded = async page => {
  await page.locator('#reader-sheet [data-article-id]').waitFor();
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
};
const noOverflow = async (page, label) => check(label, await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
async function capture(page, name) {
  await page.locator('img:visible').evaluateAll(images => Promise.all(images.filter(image => {
    const rect = image.getBoundingClientRect();
    return rect.bottom > 0 && rect.top < innerHeight;
  }).map(image => image.decode().catch(() => {}))));
  await page.screenshot({path: path.join(output, name)});
}
async function audit(page, label) {
  const result = await new AxeBuilder({page}).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  const failures = result.violations.map(v => ({id: v.id, impact: v.impact, nodes: v.nodes.map(n => ({target: n.target, summary: n.failureSummary}))}));
  audits.push({label, violations: failures});
  fs.writeFileSync(path.join(output, 'accessibility.json'), JSON.stringify(audits, null, 2));
  check(`${label}: no automated WCAG violations`, failures.length === 0);
}
(async () => {
  const base = await new Promise((resolve, reject) => {
    let text = '';
    const timer = setTimeout(() => reject(new Error('Preview did not start')), 10000);
    server.once('error', reject);
    server.stdout.on('data', data => { text += data; const match = text.match(/XNEWS_PREVIEW_URL::(http:\/\/[^\s]+)/); if (match) {clearTimeout(timer); resolve(match[1]);} });
  });
  browser = await chromium.launch({headless: true, ...(process.env.XNEWS_BROWSER_CHANNEL ? {channel: process.env.XNEWS_BROWSER_CHANNEL} : {}), args: ['--disable-gpu']});
  const context = await browser.newContext({viewport: {width: 1440, height: 1000}, reducedMotion: 'reduce'});
  // External media is not a dependency of UI verification; actual playback is out of scope.
  await context.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin ? route.continue() : route.abort());
  const page = await context.newPage(); page.on('pageerror', error => errors.push(error.message));
  await page.goto(base);
  check('Lead headline is visible in the first screen', (await page.locator('.is-featured .card-title').boundingBox()).y < 600);
  await capture(page, 'desktop-light.png');
  await noOverflow(page, '1440px home fits');
  await audit(page, 'Desktop light home');
  await page.locator('#theme-btn').click();
  await capture(page, 'desktop-dark.png');
  await audit(page, 'Desktop dark home');
  await page.reload();
  check('Theme survives reload', await page.locator('html').getAttribute('data-theme') === 'dark');
  await page.locator('#theme-btn').click();
  await page.locator('#story-search').fill('CuRsOr');
  check('Search finds the correct story', await page.locator('.news-card:visible').count() === 1 && await page.locator('#story-cursor-live-apps').isVisible());
  await page.locator('[data-filter="text"]').click();
  check('Combined filters show a recoverable empty state', await page.locator('[data-search-empty]').isVisible());
  await capture(page, 'empty-search.png');
  await page.locator('[data-reset-filters]').click();
  check('Reset restores all published articles', await page.locator('.news-card:visible').count() === articleCount);
  check('Reset restores search focus', await page.locator('#story-search').evaluate(el => el === document.activeElement));
  await page.locator('[data-layout="list"]').click();
  await capture(page, 'list.png');
  await page.locator('#story-search').fill('Amjad');
  await page.waitForURL(url => url.searchParams.get('q') === 'Amjad');
  const listURL = page.url();
  await page.locator('#read-amasad-managed-cloud-agents').focus();
  await page.keyboard.press('Enter'); await loaded(page);
  await audit(page, 'Article reader');
  check('Reader starts in rewritten version', await page.locator('#rewrite').isVisible() && !await page.locator('#original').isVisible());
  await page.locator('[data-view="rewrite"]').focus();
  await page.locator('.sheet-scroll').evaluate(el => el.scrollTop = 700);
  await page.waitForFunction(() => document.querySelector('.reading-position progress').value > 0);
  await capture(page, 'reader.png');
  await page.keyboard.press('ArrowRight'); await page.keyboard.press('Space');
  check('Keyboard switches to original', await page.locator('#original').isVisible());
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await page.locator('.sheet-scroll').evaluate(el => el.scrollTop = 300);
  await page.locator('[data-view="rewrite"]').click();
  await page.waitForFunction(() => Math.abs(document.querySelector('.sheet-scroll').scrollTop - 700) < 2);
  check('Tabs preserve separate scroll positions', true);
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => !document.querySelector('#reader-sheet').open);
  check('Escape restores filtered list URL', page.url() === listURL);
  await page.waitForFunction(() => document.activeElement.id === 'read-amasad-managed-cloud-agents');
  check('Close restores originating keyboard focus', true);
  await page.goForward(); await loaded(page);
  check('Forward reopens the same article', await page.locator('#reader-sheet [data-article-id]').getAttribute('data-article-id') === 'amasad-managed-cloud-agents');
  await page.locator('.sheet-scroll').evaluate(el => el.scrollTop = el.scrollHeight);
  await page.waitForFunction(() => document.querySelector('.reading-position progress').value === 100);
  check('Reading progress reaches 100 at end', true);
  await page.keyboard.press('Escape'); await page.waitForFunction(() => !document.querySelector('#reader-sheet').open);
  for (const width of [320, 390, 768, 1920]) {
    await page.setViewportSize({width, height: 900}); await page.goto(base);
    await noOverflow(page, `${width}px home fits`);
    const outside = await page.locator('button:visible, input:visible, .site-nav a').evaluateAll(els => els.filter(el => {const r = el.getBoundingClientRect(); return r.left < 0 || r.right > innerWidth + 1;}).map(el => el.outerHTML));
    check(`${width}px controls remain in viewport`, outside.length === 0);
    if (width === 390) await capture(page, 'mobile.png');
    if (width === 320) await audit(page, '320px home');
    await page.locator('#read-amasad-managed-cloud-agents').click(); await loaded(page);
    check(`${width}px reader fits`, await page.locator('.sheet-scroll').evaluate(el => el.scrollWidth <= el.clientWidth));
    if (width === 320) { await audit(page, '320px reader'); await capture(page, 'reader-320.png'); }
    await page.keyboard.press('Escape'); await page.waitForFunction(() => !document.querySelector('#reader-sheet').open);
  }
  await page.setViewportSize({width: 720, height: 500}); await page.goto(base);
  await noOverflow(page, '200% zoom equivalent CSS viewport fits (1440 → 720)');
  await page.evaluate(() => document.documentElement.style.fontSize = '200%');
  await noOverflow(page, '200% root font size fits');
  await page.goto(base + 'archive');
  check('Archive opens in list view', await page.locator('[data-news-grid]').getAttribute('data-layout') === 'list');
  await page.goto(base);
  await page.route('**/a/cursor-live-apps', route => route.fulfill({status:503,body:'Unavailable'}));
  await page.locator('#read-cursor-live-apps').click(); await page.locator('.retry-button').waitFor();
  check('Fetch failure offers a retry and original source', await page.locator('.sheet-status').innerText().then(s => s.includes('重试') && s.includes('去原文')));
  await page.unroute('**/a/cursor-live-apps'); await page.locator('.retry-button').click(); await loaded(page);
  check('Retry recovers the reader', true);
  const nojs = await browser.newContext({javaScriptEnabled: false, viewport:{width:390,height:844}});
  const direct = await nojs.newPage();
  await direct.goto(base + 'a/amasad-managed-cloud-agents');
  check('No-JS direct article preserves both full versions', await direct.locator('#rewrite').isVisible() && await direct.locator('#original').isVisible());
  await direct.goto(base);
  check('No-JS homepage has all native article links and no inert search controls', await direct.locator('[data-open-reader]').count() === articleCount && !await direct.locator('[data-discovery]').isVisible());
  await nojs.close();
  check('No JavaScript runtime exceptions', errors.length === 0);
  fs.writeFileSync(path.join(output, 'verification.json'), JSON.stringify({date: '2026-11-06', browser: await browser.version(), checks, errors, limitations: ['External media blocked in this test; no playback claim.', 'No VoiceOver or real iOS/Safari validation.', 'Zoom uses equivalent CSS viewport and root font size, not browser chrome zoom.']}, null, 2));
  console.log(`${checks.length} browser checks passed. Evidence: ${output}`);
})().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => { await browser?.close(); server.kill(); });
