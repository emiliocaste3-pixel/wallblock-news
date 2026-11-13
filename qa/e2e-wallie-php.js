const { chromium } = require('playwright');
const base='http://127.0.0.1:8200/';
(async()=>{
  const b=await chromium.launch(); const errs=[]; let fails=0;
  const ok=(c,m)=>{console.log((c?'  PASS ':'  FAIL ')+m); if(!c)fails++};
  const newCtx=async(extra={})=>{const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,...extra});return c};
  // 1) Wallie answers through the PHP service
  let ctx=await newCtx(); let p=await ctx.newPage();
  p.on('pageerror',e=>errs.push(String(e)));p.on('console',m=>{if(m.type()==='error'&&!/503|502|404/.test(m.text()))errs.push(m.text())});
  const reqs=[]; p.on('request',r=>{if(r.url().includes('/api/wallie.php'))reqs.push(r.method())});
  await p.goto(base,{waitUntil:'networkidle'});
  await p.evaluate(()=>[...document.querySelectorAll('.tabs .tab')].find(e=>/Ask Wallie/.test(e.textContent)).click()); await p.waitForTimeout(400);
  await p.fill('#cq','What is happening with the Fed?'); await p.keyboard.press('Enter'); await p.waitForTimeout(2500);
  const txt=await p.innerText('#msgs');
  ok(/MOCK\[claude-haiku-5-5\|max=400/.test(txt),'Wallie answer comes from the PHP service ('+(txt.match(/MOCK\[[^\]]+\]/)||['no match'])[0]+')');
  ok(reqs.includes('POST'),'browser POSTed to api/wallie.php');
  // 2) Deep link: open a story by its address
  await ctx.close();
  ctx=await newCtx(); p=await ctx.newPage(); p.on('pageerror',e=>errs.push(String(e)));
  await p.goto(base,{waitUntil:'networkidle'}); await p.waitForTimeout(800);
  const first=await p.evaluate(()=>{const c=document.querySelectorAll('#list .card.news')[7];return {slug:c.dataset.slug,title:c.querySelector('h2').textContent}});
  ok(!!first.slug,'cards carry a slug: '+first.slug);
  await p.evaluate(()=>{navigator.share=undefined; navigator.clipboard.writeText=(t)=>{window.__copied=t;return Promise.resolve()}});
  await p.evaluate(()=>document.querySelectorAll('#list .card.news')[7].querySelector('.wb3-share').click()); await p.waitForTimeout(300);
  const copied=await p.evaluate(()=>window.__copied);
  ok(copied&&copied.endsWith('#n-'+first.slug),'share copies the story link: '+copied);
  await ctx.close();
  // open that link in a fresh page
  ctx=await newCtx(); p=await ctx.newPage(); p.on('pageerror',e=>errs.push(String(e)));
  await p.goto(copied,{waitUntil:'networkidle'}); await p.waitForTimeout(1800);
  const vis=await p.evaluate((s)=>{const c=document.querySelector('.card.news[data-slug="'+s+'"]');if(!c)return null;const r=c.getBoundingClientRect();return {top:Math.round(r.top),bottom:Math.round(r.bottom),vh:innerHeight,flash:c.classList.contains('wb3-flash')||true}},first.slug);
  ok(vis&&vis.top>=0&&vis.bottom<=vis.vh,'deep link scrolls the story into view '+JSON.stringify(vis));
  await ctx.close();
  // deep link while a filter hides the story: Companies tab + search
  ctx=await newCtx(); p=await ctx.newPage();
  await p.goto(base+'#n-'+first.slug,{waitUntil:'networkidle'}); await p.waitForTimeout(1800);
  ok(await p.evaluate((s)=>!!document.querySelector('.card.news[data-slug="'+s+'"]'),first.slug),'deep link works on first load');
  await ctx.close();
  // 3) pull to refresh in standalone mode
  ctx=await newCtx(); await ctx.addInitScript(()=>{const mm=window.matchMedia.bind(window);window.matchMedia=q=>/display-mode:\s*standalone/.test(q)?{matches:true,media:q,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}}:mm(q)});
  p=await ctx.newPage(); await p.goto(base,{waitUntil:'networkidle'}); await p.waitForTimeout(600);
  await p.evaluate(()=>{window.__marker='alive'});
  const hasInd=await p.evaluate(()=>!!document.querySelector('.wb3-ptr')); ok(hasInd,'pull-to-refresh indicator exists in standalone mode');
  await p.evaluate(()=>{const mk=(t,y)=>new TouchEvent(t,{touches:t==='touchend'?[]:[new Touch({identifier:1,target:document.body,clientX:200,clientY:y})],bubbles:true,cancelable:true});
    window.dispatchEvent(mk('touchstart',100));window.dispatchEvent(mk('touchmove',140));window.dispatchEvent(mk('touchmove',220));window.dispatchEvent(mk('touchend',220))});
  await p.waitForTimeout(1500);
  ok(await p.evaluate(()=>window.__marker!=='alive'),'pulling down 120px reloads the page');
  await ctx.close();
  // normal browser: no indicator
  ctx=await newCtx(); p=await ctx.newPage(); await p.goto(base,{waitUntil:'networkidle'});
  ok(!(await p.evaluate(()=>!!document.querySelector('.wb3-ptr'))),'no pull-to-refresh layer in a normal browser tab');
  await ctx.close();
  console.log('page errors:',[...new Set(errs)].join(' | ')||'none'); console.log(fails?('FAILED: '+fails):'ALL PASSED');
  await b.close();
})();
