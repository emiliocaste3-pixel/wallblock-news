require('fs').mkdirSync(process.argv[2]||'qa/out',{recursive:true});
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const S = (process.argv[2]||'qa/out')+'/';
  const base = (process.env.BASE||'http://127.0.0.1:8099/');
  for (const [name, w, h, path] of [['desk', 1440, 900, 'index.html'], ['mob', 390, 844, 'index.html'], ['es_tab', 820, 1100, 'es/index.html']]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    const p = await ctx.newPage();
    const errs = []; p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); }); p.on('pageerror', e => errs.push(String(e)));
    p.on('response', r => { if (r.status() >= 400) errs.push(r.status() + ' ' + r.url()); });
    await p.goto(base + path, { waitUntil: 'networkidle' });
    await p.screenshot({ path: S + name + '_top.png' });
    await p.screenshot({ path: S + name + '_full.png', fullPage: true });
    console.log(name, 'errors:', errs.length ? errs : 'none', 'scrollW', await p.evaluate(() => document.documentElement.scrollWidth), 'vs', w);
    await ctx.close();
  }
  await b.close();
})();
