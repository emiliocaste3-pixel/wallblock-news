const fs=require('fs');
for(const f of process.argv.slice(2)){
  const j=JSON.parse(fs.readFileSync(f)); const c=j.categories, a=j.audits;
  const s=k=>Math.round((c[k].score||0)*100);
  console.log(`\n${f.split('/').pop()} ${j.configSettings.formFactor}: perf ${s('performance')} | a11y ${s('accessibility')} | best-practices ${s('best-practices')} | seo ${s('seo')}`);
  const m=k=>a[k]&&a[k].displayValue;
  console.log(`  FCP ${m('first-contentful-paint')} | LCP ${m('largest-contentful-paint')} | TBT ${m('total-blocking-time')} | CLS ${m('cumulative-layout-shift')} | SI ${m('speed-index')} | transfer ${m('total-byte-weight')}`);
  const fails=Object.values(a).filter(x=>x.score!==null&&x.score<0.9&&x.scoreDisplayMode!=='informative'&&x.scoreDisplayMode!=='notApplicable'&&x.scoreDisplayMode!=='manual');
  fails.sort((x,y)=>x.score-y.score).slice(0,14).forEach(x=>console.log(`  - [${Math.round(x.score*100)}] ${x.id}: ${x.title}${x.displayValue?' ('+x.displayValue+')':''}`));
}
