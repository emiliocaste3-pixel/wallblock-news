/* WallBlock News service worker.
   Network first: visitors always get the latest page and news. The cache is only a fallback
   when the device is offline, so the installed app still opens with the last data it saw.
   Videos are never cached. Bump CACHE when this file's strategy changes. */
var CACHE="wb-v1";

self.addEventListener("install",function(){self.skipWaiting()});

self.addEventListener("activate",function(e){
  e.waitUntil((async function(){
    var keys=await caches.keys();
    await Promise.all(keys.filter(function(k){return k!==CACHE}).map(function(k){return caches.delete(k)}));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch",function(e){
  var r=e.request;
  if(r.method!=="GET")return;
  var u=new URL(r.url);
  if(u.origin!==location.origin)return;
  if(/\.(mp4|webm|mov)$/i.test(u.pathname)||r.headers.has("range"))return;
  e.respondWith((async function(){
    try{
      var res=await fetch(r);
      if(res&&res.ok&&res.type==="basic"){var c=await caches.open(CACHE);c.put(r,res.clone())}
      return res;
    }catch(err){
      var hit=await caches.match(r,{ignoreSearch:true});
      if(hit)return hit;
      if(r.mode==="navigate"){var shell=await caches.match("index.html",{ignoreSearch:true})||await caches.match("./",{ignoreSearch:true});if(shell)return shell}
      throw err;
    }
  })());
});
