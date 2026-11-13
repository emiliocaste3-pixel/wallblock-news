const { chromium } = require('playwright');
(async()=>{ const b=await chromium.launch(); const [w,h,mob]=(process.argv[3]||'1350x940x0').split('x').map(Number);
 const ctx=await b.newContext({viewport:{width:w,height:h},isMobile:!!mob,hasTouch:!!mob}); const p=await ctx.newPage();
 await p.addInitScript(()=>{window.__ls=[];new PerformanceObserver(l=>{for(const e of l.getEntries()){if(e.hadRecentInput)continue;window.__ls.push({v:+e.value.toFixed(4),t:Math.round(e.startTime),src:(e.sources||[]).map(s=>({n:(s.node&&(s.node.id?'#'+s.node.id:'')+(s.node.className&&typeof s.node.className==='string'?'.'+s.node.className.split(' ')[0]:'')+'<'+s.node.nodeName+'>'),from:[Math.round(s.previousRect.x),Math.round(s.previousRect.y),Math.round(s.previousRect.width),Math.round(s.previousRect.height)],to:[Math.round(s.currentRect.x),Math.round(s.currentRect.y),Math.round(s.currentRect.width),Math.round(s.currentRect.height)]}))})}}).observe({type:'layout-shift',buffered:true})});
 await p.goto(process.argv[2]||'http://127.0.0.1:8100/',{waitUntil:'networkidle'}); await p.waitForTimeout(2500);
 const r=await p.evaluate(()=>window.__ls); const tot=r.reduce((a,x)=>a+x.v,0);
 console.log(`${w}x${h} total CLS ${tot.toFixed(4)} in ${r.length} shifts`); r.forEach(x=>{console.log(`  t=${x.t}ms value=${x.v}`); x.src.forEach(s=>console.log(`     ${s.n}  ${JSON.stringify(s.from)} -> ${JSON.stringify(s.to)}`))});
 await b.close(); })();
