// Independent contrast audit: hide all text, photograph the real background under each text element,
// and compare the declared text colour (with inherited opacity) against every background pixel.
const { chromium } = require('playwright'); const { PNG }=(()=>{try{return require('pngjs')}catch(e){return {}}})();
const fs=require('fs');
(async()=>{
 if(!PNG){console.log('pngjs missing');process.exit(2)}
 const pals=(process.argv[2]||'gold').split(','), [W,H,mob]=(process.argv[3]||'390x844x1').split('x').map(Number);
 const b=await chromium.launch(); let totalFail=0,totalChecked=0;
 for(const pal of pals){
  const ctx=await b.newContext({viewport:{width:W,height:H},isMobile:!!mob,hasTouch:!!mob,deviceScaleFactor:1}); await ctx.addInitScript(p=>{try{localStorage.setItem('pal',p)}catch(e){}},pal);
  const p=await ctx.newPage(); await p.goto('http://127.0.0.1:8100/',{waitUntil:'networkidle'}); await p.waitForTimeout(1000);
  await p.addStyleTag({content:'*{animation:none!important;transition:none!important;content-visibility:visible!important;scroll-behavior:auto!important}'});
  const docH=await p.evaluate(()=>document.documentElement.scrollHeight);
  const seen=new Set(); const fails=[]; let checked=0;
  for(let y=0;y<docH;y+=Math.floor(H*0.7)){
    await p.evaluate(y=>window.scrollTo(0,y),y); await p.waitForTimeout(120);
    // collect text elements first (with colours), then hide text and shoot
    const items=await p.evaluate(()=>{
      const out=[];const hid=['bnav','wal','tape'];
      document.querySelectorAll('body *').forEach(el=>{
        if(el.closest('#brand,.bnav,.wal,.tape,.wb3-toast,.ov:not(.on),svg,video,select,option,script,style,noscript'))return;
        const own=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim().length>0); if(!own.length)return;
        const cs=getComputedStyle(el); if(cs.visibility==='hidden'||cs.display==='none')return;
        const r=el.getBoundingClientRect(); if(r.width<4||r.height<4||r.top<0||r.bottom>innerHeight||r.left<0||r.right>innerWidth)return;
        let op=1,n=el;while(n&&n!==document.documentElement){op*=parseFloat(getComputedStyle(n).opacity);n=n.parentElement}
        const t=own.map(n=>n.textContent.trim()).join(' ').slice(0,40); if(!/[\p{L}\p{N}]/u.test(t))return;
        const lines=[];own.forEach(n=>{const tr=document.createRange();tr.selectNodeContents(n);[...tr.getClientRects()].forEach(q=>{if(q.width>1&&q.height>1)lines.push([q.left,q.top+q.height*0.2,q.width,q.height*0.6])})});if(!lines.length)return;{let clipped=false;for(let a=el.parentElement;a&&a!==document.body&&a!==document.documentElement;a=a.parentElement){const o=getComputedStyle(a);if(o.overflowX==='visible'&&o.overflowY==='visible')continue;const c=a.getBoundingClientRect();if(lines.some(l=>l[1]<c.top-1||l[1]+l[3]>c.bottom+1||l[0]<c.left-1||l[0]+l[2]>c.right+1)){clipped=true;break}}if(clipped)return}{const l0=lines[0],hit=document.elementFromPoint(Math.min(innerWidth-1,l0[0]+Math.min(l0[2]/2,6)),l0[1]+l0[3]/2);if(!hit||!(el.contains(hit)||hit.contains(el)))return}const rr={left:lines[0][0],top:lines[0][1],width:lines[0][2],height:lines[0][3]};
        out.push({lines,id:(el.id?'#'+el.id:'')+'.'+(String(el.className).split(' ')[0]||el.tagName.toLowerCase()),t,color:cs.color,fs:parseFloat(cs.fontSize),fw:parseInt(cs.fontWeight)||400,op,x:rr.left,y:rr.top,w:rr.width,h:rr.height,sy:scrollY});
      });return out});
    // hide sticky/fixed chrome on non-top chunks, then make text transparent
    await p.addStyleTag({content:`.bnav,.wal,.wb3-toast{visibility:hidden!important}${y>0?'.tape,header.top{visibility:hidden!important}':''}*{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important;caret-color:transparent!important}`});
    const buf=await p.screenshot(); const png=PNG.sync.read(buf);
    for(const it of items){
      const key=it.id+it.t+Math.round(it.y+it.sy); if(seen.has(key))continue; seen.add(key);
      const m=/rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?\)/.exec(it.color); if(!m)continue; const fa=(m[4]===undefined?1:+m[4])*it.op; const fg=[+m[1],+m[2],+m[3]];
      let worst=99,n=0,wpx=null,wpos=null; const lum=c=>{const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2])};
      for(const ln of it.lines){const x0=Math.max(0,Math.floor(ln[0])),y0=Math.max(0,Math.floor(ln[1])),x1=Math.min(png.width,Math.ceil(ln[0]+ln[2])),y1=Math.min(png.height,Math.ceil(ln[1]+ln[3]));for(let yy=y0;yy<y1;yy+=2)for(let xx=x0;xx<x1;xx+=2){const i=(png.width*yy+xx)*4;const bg=[png.data[i],png.data[i+1],png.data[i+2]];const c=[0,1,2].map(k=>fg[k]*fa+bg[k]*(1-fa));const L1=lum(c),L2=lum(bg);const cr=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);if(cr<worst){worst=cr;wpx=bg.join(',');wpos=[xx,yy]}n++}}
      if(!n)continue; checked++; const large=it.fs>=24||(it.fs>=18.66&&it.fw>=700); const need=large?3:4.5;
      if(worst<need-0.001)fails.push({wpx,wpos,line:it.lines.map(l=>l.map(Math.round)).join(' / '),id:it.id,t:it.t,ratio:+worst.toFixed(2),need,fs:it.fs,color:it.color,op:+it.op.toFixed(2)});
    }
    await p.reload({waitUntil:'networkidle'}); await p.waitForTimeout(600); await p.addStyleTag({content:'*{animation:none!important;transition:none!important;content-visibility:visible!important;scroll-behavior:auto!important}'});
  }
  totalChecked+=checked; totalFail+=fails.length;
  console.log(`[${pal} ${W}px] checked ${checked} text elements -> ${fails.length} below threshold`);
  fails.slice(0,40).forEach(f=>console.log(`    ${f.ratio}:1 (need ${f.need}) ${f.id} "${f.t}" ${f.fs}px fg=${f.color} opacity=${f.op} | worst bg px (${f.wpx}) at ${f.wpos} | lines ${f.line}`));
  await ctx.close();
 }
 await b.close(); console.log(totalFail?`TOTAL FAIL ${totalFail}/${totalChecked}`:`ALL ${totalChecked} OK`);
})();
