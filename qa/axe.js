const { chromium } = require('playwright'); const fs=require('fs');
const axeSrc=fs.readFileSync(__dirname+'/node_modules/axe-core/axe.min.js','utf8');
(async()=>{ const b=await chromium.launch(); const out=[];
 for(const pal of ['gold','blue']) for(const [name,vp,mob] of [['m390',{width:390,height:844},true],['d1280',{width:1280,height:900},false]]){
  const ctx=await b.newContext({viewport:vp,isMobile:mob,hasTouch:mob}); await ctx.addInitScript(p=>{try{localStorage.setItem('pal',p)}catch(e){}},pal);
  const p=await ctx.newPage(); await p.goto(process.argv[2]||'http://127.0.0.1:8100/',{waitUntil:'networkidle'}); await p.waitForTimeout(1200);
  await p.addScriptTag({content:axeSrc});
  const r=await p.evaluate(async()=>{const x=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']},resultTypes:['violations']});return x.violations.map(v=>({id:v.id,impact:v.impact,n:v.nodes.length,help:v.help,ex:v.nodes.slice(0,3).map(n=>n.target.join(' ')+' :: '+((n.any[0]||n.all[0]||n.none[0]||{}).message||'').slice(0,120))}))});
  console.log(`\n[${pal} ${name}] violations: ${r.length}`); r.forEach(v=>{console.log(`  ${v.impact.padEnd(8)} ${v.id} x${v.n} — ${v.help}`); v.ex.forEach(e=>console.log('       ·',e.slice(0,170)))});
  await ctx.close(); }
 await b.close(); })();
