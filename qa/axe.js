const { chromium } = require('playwright');
const axe = require('fs').readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
(async () => {
  const b = await chromium.launch();
  const pages = ['index.html','es/index.html','markets/index.html','es/markets/index.html','wall-street/index.html','calendar/index.html','videos/index.html','about/index.html','contact/index.html','es/calendar/index.html'];
  let total = 0;
  for (const w of [390, 1440]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 } });
    const p = await ctx.newPage();
    for (const path of pages) {
      await p.goto((process.env.BASE||'http://127.0.0.1:8099/') + path, { waitUntil: 'networkidle' });
      await p.evaluate(axe);
      const r = await p.evaluate(async () => await axe.run(document, { runOnly: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice'] }));
      const v = r.violations;
      total += v.length;
      console.log(w, path.padEnd(28), v.length ? v.map(x => x.id + '(' + x.nodes.length + ')').join(', ') : 'OK');
      v.forEach(x => x.nodes.slice(0, 2).forEach(n => console.log('    ', x.id, n.target.join(' '), '|', (n.failureSummary || '').split('\n')[1] || '')));
    }
    await ctx.close();
  }
  console.log('TOTAL violations:', total);
  await b.close();
})();
