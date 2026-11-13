// Static server that mimics the production .htaccess: gzip for text, long cache for media/fonts, revalidate html/json/css/js.
const http=require('http'),fs=require('fs'),path=require('path'),zlib=require('zlib');
const root=path.resolve(process.argv[2]),port=+process.argv[3]||8100;
const T={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'application/javascript','.json':'application/json','.webmanifest':'application/manifest+json','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.ico':'image/x-icon','.mp4':'video/mp4','.woff2':'font/woff2','.txt':'text/plain','.svg':'image/svg+xml'};
const GZ=new Set(['.html','.css','.js','.json','.webmanifest','.txt','.svg']);
http.createServer((req,res)=>{
  let u=decodeURIComponent(req.url.split('?')[0]); if(u.endsWith('/'))u+='index.html';
  const f=path.join(root,u); if(!f.startsWith(root)||!fs.existsSync(f)||fs.statSync(f).isDirectory()){res.writeHead(404);return res.end('nf')}
  const ext=path.extname(f),st=fs.statSync(f),h={'Content-Type':T[ext]||'application/octet-stream','X-Content-Type-Options':'nosniff'};
  if(/^\/(index\.html|content\.json|wb3\.css|wb3\.js|sw\.js|manifest\.webmanifest)$/.test(u))h['Cache-Control']='no-cache, must-revalidate';
  else if(ext==='.woff2')h['Cache-Control']='public, max-age=31536000';
  else if(ext==='.mp4')h['Cache-Control']='public, max-age=2592000';
  else if(['.png','.jpg','.webp','.ico'].includes(ext))h['Cache-Control']='public, max-age=604800';
  if(ext==='.mp4'&&req.headers.range){const m=/bytes=(\d*)-(\d*)/.exec(req.headers.range),s=+m[1]||0,e=m[2]?+m[2]:st.size-1;res.writeHead(206,{...h,'Content-Range':`bytes ${s}-${e}/${st.size}`,'Accept-Ranges':'bytes','Content-Length':e-s+1});return fs.createReadStream(f,{start:s,end:e}).pipe(res)}
  if(GZ.has(ext)&&/gzip/.test(req.headers['accept-encoding']||'')){h['Content-Encoding']='gzip';h['Vary']='Accept-Encoding';res.writeHead(200,h);return fs.createReadStream(f).pipe(zlib.createGzip({level:6})).pipe(res)}
  h['Content-Length']=st.size;h['Accept-Ranges']='bytes';res.writeHead(200,h);fs.createReadStream(f).pipe(res);
}).listen(port,'127.0.0.1',()=>console.log('serving',root,'on',port));
