const { chromium } = require('playwright'); const fs=require('fs'); const {spawn}=require('child_process');
// usage: node render.js cfg.json out.mp4 [--samples t1,t2,...]
(async()=>{
  const cfg=JSON.parse(fs.readFileSync(process.argv[2])); const out=process.argv[3]; const si=process.argv.indexOf('--samples');
  const b=await chromium.launch(); const p=await (await b.newContext({viewport:{width:1080,height:1920},deviceScaleFactor:1})).newPage();
  p.on('pageerror',e=>console.log('PAGEERROR',String(e).slice(0,200))); p.on('console',m=>{if(m.type()==='error')console.log('console:',m.text().slice(0,160))});
  await p.goto('file://'+process.cwd()+'/scene.html'); await p.waitForTimeout(500);
  await p.evaluate(c=>init(c),cfg); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
  if(si>0){ const ts=process.argv[si+1].split(',').map(Number); for(const t of ts){ await p.evaluate(t=>render(t),t); await p.waitForTimeout(60); await p.screenshot({path:`samples/${cfg.lang}_${String(t).replace('.','_')}.png`}); } await b.close(); return; }
  const FPS=30, N=Math.ceil(cfg.total*FPS);
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-r',String(FPS),out],{stdio:['pipe','inherit','inherit']});
  for(let i=0;i<N;i++){ const t=i/FPS; await p.evaluate(t=>render(t),t); const buf=await p.screenshot({type:'jpeg',quality:92}); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); if(i%150===0)console.log('frame',i,'/',N); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done',out);
})();
