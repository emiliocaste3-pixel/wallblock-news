/* WallBlock News · live markets page
   1) Bubble map (canvas): draggable bubbles, snapshot data from the site, optional live crypto prices.
   2) Opt-in TradingView widgets: nothing from TradingView loads until the visitor clicks. */
(function () {
  'use strict';

  var TV_JS = 'https://s3.tradingview.com/external-embedding/embed-widget-';
  var KEY_TV = 'wb-tv-consent', KEY_CG = 'wb-cg-live';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } }
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }

  /* ------------------------------------------------------------ TradingView (opt-in) */
  function loadTV(box, type, cfg) {
    if (box.getAttribute('data-loaded')) return;
    box.setAttribute('data-loaded', '1');
    var wrap = el('div', 'tradingview-widget-container');
    var inner = el('div', 'tradingview-widget-container__widget');
    var cp = el('div', 'tradingview-widget-copyright');
    var a = el('a'); a.href = 'https://www.tradingview.com/'; a.rel = 'noopener nofollow'; a.target = '_blank';
    a.appendChild(el('span', '', 'Track all markets on TradingView')); cp.appendChild(a);
    var s = document.createElement('script');
    s.src = TV_JS + type + '.js'; s.async = true; s.text = JSON.stringify(cfg);
    wrap.appendChild(inner); wrap.appendChild(cp); wrap.appendChild(s);
    box.textContent = ''; box.appendChild(wrap); box.classList.add('loaded');
  }
  function loadBox(b) { var cfg; try { cfg = JSON.parse(b.getAttribute('data-cfg')); } catch (e) { return; } loadTV(b, b.getAttribute('data-tv'), cfg); }

  var boxes = [].slice.call(document.querySelectorAll('.tv-box'));
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); loadBox(e.target); } });
  }, { rootMargin: '300px' }) : null;
  function armAll() { boxes.forEach(function (b) { if (b.getAttribute('data-loaded')) return; if (io) io.observe(b); else loadBox(b); }); }

  var forget = document.querySelector('[data-tv-forget]');
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-tv-load],[data-tv-all],[data-tv-forget]');
    if (!t) return;
    if (t.hasAttribute('data-tv-load')) { var b = t.closest('.tv-box'); if (b) loadBox(b); }
    else if (t.hasAttribute('data-tv-all')) { store(KEY_TV, '1'); armAll(); if (forget) forget.hidden = false; }
    else if (t.hasAttribute('data-tv-forget')) { store(KEY_TV, null); store(KEY_CG, null); location.reload(); }
  });
  if (store(KEY_TV) === '1') { armAll(); if (forget) forget.hidden = false; }

  /* ------------------------------------------------------------ Bubble map */
  var root = document.querySelector('[data-bubbles]');
  var dataEl = document.getElementById('bubble-data');
  if (!root || !dataEl) return;
  var DATA; try { DATA = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var T = DATA.t, LOC = DATA.locale, STABLE = {}; DATA.stable.forEach(function (s) { STABLE[s] = 1; });

  var stage = root.querySelector('[data-stage]'), cv = stage.querySelector('canvas'), ctx = cv.getContext('2d');
  var info = stage.querySelector('[data-info]'), dot = root.querySelector('[data-dot]'), srcEl = root.querySelector('[data-src]');
  var hideChk = root.querySelector('[data-hide-stable]'), liveBtn = root.querySelector('[data-live-btn]');
  var st = { ds: 'crypto', tf: 'd1', sz: 'move', hide: true };
  var live = null, bub = [], W = 0, H = 0, DPR = 1, raf = 0, running = false, visible = true, drag = null, down = null, sel = null;
  var css = getComputedStyle(document.documentElement);
  var C = {
    up: [127, 221, 163], down: [255, 144, 136], flat: [176, 195, 180], text: '#E0E4CD', gold: '#E3B341'
  };

  function nf(n, o) { return n.toLocaleString(LOC, o); }
  function fmtP(p) { if (p == null || isNaN(p)) return '–'; return '$' + nf(p, p >= 1 ? { minimumFractionDigits: 2, maximumFractionDigits: 2 } : { maximumSignificantDigits: 4 }); }
  function fmtC(v) { if (!v) return '–'; var u = [[1e12, 'T'], [1e9, 'B'], [1e6, 'M']]; for (var i = 0; i < u.length; i++) if (v >= u[i][0]) return '$' + nf(v / u[i][0], { maximumFractionDigits: 1 }) + u[i][1]; return '$' + nf(v); }
  function fmtPct(d) { if (d == null || isNaN(d)) return '–'; return (d > 0 ? '+' : d < 0 ? '−' : '') + nf(Math.abs(d), { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + (LOC === 'es-ES' ? ' %' : '%'); }
  function rgba(c, a) { return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + a.toFixed(2) + ')'; }
  function kindOf(d) { return Math.abs(d) < 0.05 ? C.flat : (d > 0 ? C.up : C.down); }

  function coins() {
    if (st.ds === 'crypto' && live) return live.coins;
    return DATA.ds[st.ds].coins;
  }
  function hasTf(tf) { return coins().some(function (x) { return typeof x[tf] === 'number'; }); }

  function setSource() {
    var d = DATA.ds[st.ds];
    if (st.ds === 'crypto' && live) {
      dot.className = 'bdot live';
      srcEl.textContent = T.live_src + ' · ' + new Date(live.t).toLocaleTimeString(LOC, { hour: '2-digit', minute: '2-digit' });
    } else {
      dot.className = 'bdot';
      srcEl.textContent = T.snapshot + ' · ' + d.asof + (d.source ? ' · ' + d.source : '') + (d.period ? ' · ' + d.period : '');
    }
  }

  function syncControls() {
    var crypto = st.ds === 'crypto', metals = st.ds === 'metals';
    root.querySelector('[data-seg="tf"]').hidden = !crypto;
    hideChk.parentNode.hidden = !crypto;
    if (liveBtn) liveBtn.hidden = !crypto;
    root.querySelectorAll('[data-seg="tf"] button').forEach(function (b) {
      var ok = hasTf(b.getAttribute('data-v')); b.disabled = !ok;
      if (!ok && b.getAttribute('aria-pressed') === 'true') { st.tf = 'd1'; }
    });
    var cap = root.querySelector('[data-seg="sz"] [data-v="cap"]'); cap.disabled = metals;
    if (metals) st.sz = 'move';
    ['ds', 'tf', 'sz'].forEach(function (g) {
      root.querySelectorAll('[data-seg="' + g + '"] button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-v') === st[g] ? 'true' : 'false'); });
    });
  }

  function build() {
    syncControls();
    var list = coins().filter(function (c) { return !(st.ds === 'crypto' && st.hide && (c.st || STABLE[c.s])); });
    var tf = hasTf(st.tf) ? st.tf : 'd1';
    var w = list.map(function (c) {
      var d = typeof c[tf] === 'number' ? c[tf] : 0;
      return st.sz === 'cap' && st.ds !== 'metals' ? Math.pow(Math.max(c.mc || c.w || 1, 1e-9), 0.5) : Math.pow(Math.abs(d) + 0.35, 0.85);
    });
    var sum = w.reduce(function (a, b) { return a + b; }, 0) || 1, area = W * H * (W < 600 ? 0.5 : 0.56), old = {};
    bub.forEach(function (b) { old[b.c.s] = b; });
    bub = list.map(function (c, i) {
      var r = Math.max(Math.sqrt(area * w[i] / sum / Math.PI), Math.min(W, H) * 0.02), o = old[c.s], d = c[tf];
      return { c: c, d: typeof d === 'number' ? d : 0, r: r, tr: r, rr: o ? o.rr : 0, x: o ? o.x : W / 2 + (Math.random() - .5) * W * .6, y: o ? o.y : H / 2 + (Math.random() - .5) * H * .6, vx: o ? o.vx : (Math.random() - .5) * 2, vy: o ? o.vy : (Math.random() - .5) * 2 };
    });
    var maxR = Math.min(W, H) * 0.24; bub.forEach(function (b) { if (b.tr > maxR) b.tr = maxR; });
    if (sel && !bub.some(function (b) { return b.c.s === sel.c.s; })) hideInfo();
    setSource();
    if (reduce) { for (var i = 0; i < 260; i++) step(); draw(); }
  }

  function size() {
    var r = stage.getBoundingClientRect();
    DPR = Math.min(window.devicePixelRatio || 1, 2); W = Math.max(r.width, 1); H = Math.max(r.height, 1);
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR); ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }

  function step() {
    var n = bub.length, cx = W / 2, cy = H / 2, t = Date.now(), i, j, a, b;
    for (i = 0; i < n; i++) {
      a = bub[i]; a.rr += (a.tr - a.rr) * 0.12; if (a === drag) continue;
      a.vx += (cx - a.x) * 0.00035; a.vy += (cy - a.y) * 0.00035; a.vx *= 0.985; a.vy *= 0.985;
      if (!reduce) { a.vx += Math.sin(t / 3200 + i) * 0.004; a.vy += Math.cos(t / 4100 + i * 1.3) * 0.004; }
      a.x += a.vx; a.y += a.vy;
      if (a.x < a.rr) { a.x = a.rr; a.vx = Math.abs(a.vx) * 0.6; } if (a.x > W - a.rr) { a.x = W - a.rr; a.vx = -Math.abs(a.vx) * 0.6; }
      if (a.y < a.rr) { a.y = a.rr; a.vy = Math.abs(a.vy) * 0.6; } if (a.y > H - a.rr) { a.y = H - a.rr; a.vy = -Math.abs(a.vy) * 0.6; }
    }
    for (var k = 0; k < 2; k++) for (i = 0; i < n; i++) {
      a = bub[i];
      for (j = i + 1; j < n; j++) {
        b = bub[j]; var dx = b.x - a.x, dy = b.y - a.y, m = a.rr + b.rr + 1.5, dd = dx * dx + dy * dy;
        if (dd < m * m && dd > 0.0001) {
          var D = Math.sqrt(dd), o = (m - D) / 2, ux = dx / D, uy = dy / D, wa = a === drag ? 0 : (b === drag ? 1 : 0.5), wb = a === drag ? 1 : 1 - wa;
          a.x -= ux * o * 2 * wa; a.y -= uy * o * 2 * wa; b.x += ux * o * 2 * wb; b.y += uy * o * 2 * wb;
          var rv = (b.vx - a.vx) * ux + (b.vy - a.vy) * uy;
          if (rv < 0) { var imp = rv * 0.5; if (a !== drag) { a.vx += ux * imp; a.vy += uy * imp; } if (b !== drag) { b.vx -= ux * imp; b.vy -= uy * imp; } }
        }
      }
    }
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    var scale = st.ds === 'stocks' ? 3 : st.ds === 'metals' ? 2 : st.tf === 'w1' ? 15 : st.tf === 'h1' ? 2 : 8;
    bub.forEach(function (b) {
      var r = b.rr; if (r < 1) return;
      var c = kindOf(b.d), k = Math.min(Math.abs(b.d) / scale, 1), isSel = sel === b;
      var g = ctx.createRadialGradient(b.x - r * 0.35, b.y - r * 0.4, r * 0.1, b.x, b.y, r);
      g.addColorStop(0, rgba(c, 0.12 + 0.14 * k)); g.addColorStop(1, rgba(c, 0.2 + 0.24 * k));
      ctx.beginPath(); ctx.arc(b.x, b.y, r, 0, 7); ctx.fillStyle = g; ctx.fill();
      ctx.lineWidth = isSel ? 3 : 2; ctx.strokeStyle = isSel ? C.gold : rgba(c, 1); ctx.stroke();
      if (r > 13) {
        var fs = Math.max(9, Math.min(r * 0.42, 30)), sy = b.c.s;
        if (st.ds !== 'metals' && sy.length > 6) sy = sy.slice(0, 6);
        ctx.fillStyle = C.text; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        while (fs > 9) { ctx.font = '700 ' + fs + 'px Inter,system-ui,sans-serif'; if (ctx.measureText(sy).width <= r * 1.7) break; fs -= 1; }
        ctx.font = '700 ' + fs + 'px Inter,system-ui,sans-serif';
        if (r > 20) { ctx.fillText(sy, b.x, b.y - fs * 0.32); ctx.font = '600 ' + (fs * 0.62) + 'px Inter,system-ui,sans-serif'; ctx.fillText(fmtPct(b.d), b.x, b.y + fs * 0.5); }
        else ctx.fillText(sy, b.x, b.y);
      }
    });
  }

  function loop() { if (!running) return; if (visible) { step(); draw(); } raf = requestAnimationFrame(loop); }
  function hit(x, y) { for (var i = bub.length - 1; i >= 0; i--) { var b = bub[i], dx = x - b.x, dy = y - b.y; if (dx * dx + dy * dy <= b.rr * b.rr) return b; } return null; }
  function pos(e) { var r = cv.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; }

  cv.addEventListener('pointerdown', function (e) {
    var p = pos(e), b = hit(p.x, p.y); down = { x: p.x, y: p.y, lx: p.x, ly: p.y };
    if (b && !reduce) { drag = b; cv.classList.add('drag'); cv.setPointerCapture(e.pointerId); }
  });
  cv.addEventListener('pointermove', function (e) {
    if (!down || !drag) return; var p = pos(e);
    drag.vx = p.x - down.lx; drag.vy = p.y - down.ly; drag.x = p.x; drag.y = p.y; down.lx = p.x; down.ly = p.y;
  });
  function release(e) {
    if (!down) return; var p = pos(e), moved = Math.abs(p.x - down.x) + Math.abs(p.y - down.y);
    if (moved < 6) { var b = hit(p.x, p.y); if (b) showInfo(b); else hideInfo(); }
    if (drag) { drag.vx = Math.max(-25, Math.min(25, drag.vx)); drag.vy = Math.max(-25, Math.min(25, drag.vy)); }
    drag = null; down = null; cv.classList.remove('drag'); if (reduce) draw();
  }
  cv.addEventListener('pointerup', release); cv.addEventListener('pointercancel', release);

  function row(dl, label, value, cls) { dl.appendChild(el('dt', '', label)); dl.appendChild(el('dd', cls || '', value)); }
  function showInfo(b) {
    sel = b; var c = b.c, stocks = st.ds === 'stocks', metals = st.ds === 'metals';
    info.textContent = ''; info.hidden = false;
    var head = el('div', 'binfo-h'), h = el('h3', '', c.n || c.s);
    var sub = el('small', '', metals ? (c.note || '') : c.s + (c.r ? ' · #' + c.r : ''));
    h.appendChild(document.createTextNode(' ')); h.appendChild(sub);
    var x = el('button', 'binfo-x', T.close); x.type = 'button'; x.addEventListener('click', hideInfo);
    head.appendChild(h); head.appendChild(x); info.appendChild(head);
    var dl = el('dl');
    if (c.p != null) row(dl, T.price, fmtP(c.p));
    if (!metals) row(dl, stocks ? T.weight : T.cap, stocks ? nf(c.w || 0, { maximumFractionDigits: 2 }) + (LOC === 'es-ES' ? ' %' : '%') : fmtC(c.mc));
    [['h1', T.h1], ['d1', T.d1], ['w1', T.w1]].forEach(function (t) {
      if (typeof c[t[0]] === 'number') row(dl, T.chg + (stocks || metals ? '' : ' ' + t[1]), fmtPct(c[t[0]]), c[t[0]] > 0 ? 'up' : c[t[0]] < 0 ? 'down' : '');
    });
    info.appendChild(dl);
    var sym = tvSymbol(c, stocks, metals);
    if (sym) {
      var box = el('div', 'tv-mini'); box.setAttribute('data-tv', 'mini-symbol-overview');
      box.setAttribute('data-cfg', JSON.stringify({ symbol: sym, width: '100%', height: 220, locale: LOC === 'es-ES' ? 'es' : 'en', dateRange: '12M', colorTheme: 'dark', isTransparent: true, autosize: false, largeChartUrl: '' }));
      var btn = el('button', 'btn ghost', T.tv_chart); btn.type = 'button';
      btn.addEventListener('click', function () { loadBox(box); btn.remove(); });
      box.appendChild(btn); info.appendChild(box);
      if (store(KEY_TV) === '1') { loadBox(box); }
    }
    if (reduce) draw();
  }
  function hideInfo() { sel = null; info.hidden = true; info.textContent = ''; if (reduce) draw(); }
  function tvSymbol(c, stocks, metals) {
    if (metals) return c.tv || '';
    if (stocks) return c.s.replace('.', '-');
    return 'BINANCE:' + c.s + 'USDT';
  }

  /* ---- controls */
  root.querySelectorAll('[data-seg]').forEach(function (g) {
    g.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b || b.disabled) return;
      st[g.getAttribute('data-seg')] = b.getAttribute('data-v'); hideInfo(); build();
    });
  });
  hideChk.addEventListener('change', function () { st.hide = this.checked; build(); });

  /* ---- optional live crypto prices (CoinGecko public API). Opt-in because it sends the visitor's IP to CoinGecko. */
  function fetchLive() {
    if (live && Date.now() - live.t < 120000) return;
    var ctl = window.AbortController ? new AbortController() : null, tm = setTimeout(function () { if (ctl) ctl.abort(); }, 6000);
    fetch('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=120&page=1&price_change_percentage=1h,24h,7d',
      { signal: ctl ? ctl.signal : undefined, referrerPolicy: 'no-referrer' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        clearTimeout(tm); if (!Array.isArray(j) || !j.length) return;
        live = { t: Date.now(), coins: j.map(function (x, i) {
          var s = String(x.symbol || '').toUpperCase(), p = x.current_price;
          return { r: x.market_cap_rank || i + 1, n: x.name, s: s, p: p, mc: x.market_cap, h1: x.price_change_percentage_1h_in_currency,
            d1: x.price_change_percentage_24h_in_currency != null ? x.price_change_percentage_24h_in_currency : x.price_change_percentage_24h,
            w1: x.price_change_percentage_7d_in_currency, st: STABLE[s] ? 1 : 0 };
        }) };
        if (liveBtn) liveBtn.setAttribute('aria-pressed', 'true');
        build();
      }).catch(function () { clearTimeout(tm); });
  }
  if (liveBtn) liveBtn.addEventListener('click', function () { store(KEY_CG, '1'); fetchLive(); });

  /* ---- lifecycle */
  function start() {
    size(); build();
    if (!reduce) { running = true; cancelAnimationFrame(raf); loop(); }
    if (store(KEY_CG) === '1') fetchLive();
  }
  if ('ResizeObserver' in window) {
    var first = true; new ResizeObserver(function () { if (first) { first = false; return; } size(); build(); }).observe(stage);
  } else window.addEventListener('resize', function () { size(); build(); });
  if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(stage);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !info.hidden) hideInfo(); });
  start();
})();
