const { chromium } = require('playwright');
(async () => {
  const S = (process.argv[2]||'qa/out')+'/';
  const b = await chromium.launch();
  for (const [name, w, h] of [['mk_desk', 1440, 900], ['mk_mob', 390, 844]]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h } });
    const p = await ctx.newPage();
    const errs = [], reqs = [];
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); }); p.on('pageerror', e => errs.push('PAGEERR ' + e));
    // stub external services: nothing leaves the sandbox
    await p.route('https://s3.tradingview.com/**', r => { reqs.push(r.request().url()); r.fulfill({ status: 200, contentType: 'application/javascript', body: '/*stub*/' }); });
    await p.route('https://api.coingecko.com/**', r => { reqs.push(r.request().url()); r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' },
      body: JSON.stringify([{symbol:'btc',name:'Bitcoin',current_price:70000,market_cap:1.4e12,market_cap_rank:1,price_change_percentage_1h_in_currency:.3,price_change_percentage_24h_in_currency:2.5,price_change_percentage_7d_in_currency:-4},{symbol:'eth',name:'Ethereum',current_price:2100,market_cap:2.5e11,market_cap_rank:2,price_change_percentage_1h_in_currency:-.2,price_change_percentage_24h_in_currency:-1.5,price_change_percentage_7d_in_currency:3},{symbol:'usdt',name:'Tether',current_price:1,market_cap:1.1e11,market_cap_rank:3,price_change_percentage_24h_in_currency:0}]) }); });
    await p.goto('http://127.0.0.1:8099/markets/index.html', { waitUntil: 'networkidle' });
    await p.waitForTimeout(1200);
    const painted = await p.evaluate(() => { const c = document.querySelector('.bstage canvas'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let n = 0; for (let i = 3; i < d.length; i += 4000) if (d[i] > 0) n++; return n; });
    await p.screenshot({ path: S + name + '_bubbles.png', clip: { x: 0, y: (await p.evaluate(() => document.getElementById('bubbles').getBoundingClientRect().top + scrollY)) , width: w, height: Math.min(h, 900) } }).catch(()=>{});
    // click the biggest bubble via page coords: find by scanning center
    const box = await p.locator('.bstage canvas').boundingBox();
    let opened = false;
    for (let i = 0; i < 40 && !opened; i++) { await p.mouse.click(box.x + box.width * (0.2 + 0.6 * (i % 8) / 8), box.y + box.height * (0.2 + 0.6 * Math.floor(i / 8) / 5)); opened = await p.evaluate(() => !document.querySelector('[data-info]').hidden); }
    await p.screenshot({ path: S + name + '_info.png', fullPage: false });
    // tabs
    for (const ds of ['stocks', 'metals', 'crypto']) { await p.click(`[data-seg="ds"] [data-v="${ds}"]`); await p.waitForTimeout(500); }
    // live prices opt-in
    await p.click('[data-live-btn]'); await p.waitForTimeout(800);
    const src = await p.textContent('[data-src]');
    // TV: nothing before click
    const before = reqs.filter(u => u.includes('tradingview')).length;
    await p.click('#chart [data-tv-load]'); await p.waitForTimeout(400);
    const tvReqs = reqs.filter(u => u.includes('tradingview'));
    const cfg = await p.evaluate(() => { const s = document.querySelector('#chart script'); return s ? s.src + ' | ' + s.text.slice(0, 60) : 'no script'; });
    console.log(name, '| errors:', errs.length ? errs : 'none', '| painted samples:', painted, '| info opened:', opened, '| TV requests before click:', before, 'after:', tvReqs.length, '|', cfg, '| source:', src);
    await ctx.close();
  }
  await b.close();
})();
