/* ===== WallBlock v3 · app layer =====
   Share button on stories, "Install app" button, status-bar colour that follows the theme,
   and the offline service worker. Loads after the main script (defer). */
(function(){
"use strict";

function lang(){try{return typeof LANG!=="undefined"?LANG:"en"}catch(e){return"en"}}
var TX={
  share:{en:"Share",es:"Compartir",fr:"Partager",it:"Condividi",pt:"Partilhar",zh:"分享",ko:"공유"},
  copied:{en:"Link copied",es:"Enlace copiado",fr:"Lien copié",it:"Link copiato",pt:"Ligação copiada",zh:"链接已复制",ko:"링크가 복사되었습니다"}
};
function T(k){var o=TX[k];return o[lang()]||o.en}

/* small toast */
var toastEl=null,toastTimer=0;
function toast(msg){
  if(!toastEl){toastEl=document.createElement("div");toastEl.className="wb3-toast";toastEl.setAttribute("role","status");toastEl.setAttribute("aria-live","polite");document.body.appendChild(toastEl)}
  toastEl.textContent=msg;toastEl.classList.add("on");
  clearTimeout(toastTimer);toastTimer=setTimeout(function(){toastEl.classList.remove("on")},2200);
}

/* ---- story links: every story has its own address, e.g. #n-nasdaq-jumps-1-8-as-the-ai-trade-returns ---- */
function slugOf(i){
  var n=(typeof S!=="undefined"&&S&&S.news)?S.news[+i]:null;
  return n?String(n.title||"").toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"").slice(0,70):"";
}
function storyUrl(slug){return location.href.split("#")[0]+(slug?"#n-"+slug:"")}
var pending=(location.hash.match(/^#n-(.+)$/)||[])[1]||null,resetTried=false;
function openPending(list){
  if(!pending)return;
  var el=list.querySelector('.card.news[data-slug="'+pending.replace(/"/g,"")+'"]');
  if(el){
    pending=null;
    el.scrollIntoView({behavior:"smooth",block:"center"});
    el.classList.add("wb3-flash");setTimeout(function(){el.classList.remove("wb3-flash")},2600);
  }else if(!resetTried&&typeof S!=="undefined"&&S&&S.news&&S.news.some(function(n,i){return slugOf(i)===pending})){
    /* the story exists but a filter hides it: show everything */
    resetTried=true;
    var q=document.getElementById("q");if(q&&q.value){q.value="";q.dispatchEvent(new Event("input",{bubbles:true}))}
    var all=document.querySelector(".tabs .tab");if(all)all.click();
  }
}
window.addEventListener("hashchange",function(){var m=location.hash.match(/^#n-(.+)$/);if(m){pending=m[1];resetTried=false;var l=document.getElementById("list");if(l)openPending(l)}});

/* ---- share button on every story ---- */
var SHARE_SVG='<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="m7 8 5-5 5 5"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg>';
function decorate(){
  var list=document.getElementById("list");if(!list)return;
  list.querySelectorAll(".card.news").forEach(function(c){
    var m=c.querySelector(".meta");if(!m||m.querySelector(".wb3-share"))return;
    var star=m.querySelector(".star"),acts=document.createElement("span"),b=document.createElement("button");
    if(star&&star.dataset.i!==undefined)c.dataset.slug=slugOf(star.dataset.i);
    acts.className="wb3-acts";
    b.type="button";b.className="wb3-share";b.innerHTML=SHARE_SVG;b.setAttribute("aria-label",T("share"));b.title=T("share");
    if(star){m.insertBefore(acts,star);acts.appendChild(b);acts.appendChild(star)}else{acts.appendChild(b);m.appendChild(acts)}
  });
  openPending(list);
}
function copyText(t){
  function fallback(){
    var a=document.createElement("textarea");a.value=t;a.setAttribute("readonly","");a.style.cssText="position:fixed;opacity:0";
    document.body.appendChild(a);a.select();try{document.execCommand("copy");toast(T("copied"))}catch(e){}a.remove();
  }
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(function(){toast(T("copied"))},fallback)}else fallback();
}
document.addEventListener("click",function(e){
  var b=e.target.closest&&e.target.closest(".wb3-share");if(!b)return;
  var h=b.closest(".card.news"),h2=h&&h.querySelector("h2"),title=h2?h2.textContent:document.title,url=storyUrl(h&&h.dataset.slug);
  if(navigator.share){navigator.share({title:title,text:title,url:url}).catch(function(){})}else copyText(url);
});
var listEl=document.getElementById("list");
if(listEl){new MutationObserver(decorate).observe(listEl,{childList:true})}
decorate();

/* ---- status-bar colour follows the selected theme ---- */
function syncThemeColor(){
  var m=document.querySelector('meta[name="theme-color"]');if(!m)return;
  var bg=getComputedStyle(document.documentElement).getPropertyValue("--bg").trim();
  if(bg)m.setAttribute("content",bg);
}
syncThemeColor();
var th=document.getElementById("theme");
if(th)th.addEventListener("change",function(){setTimeout(syncThemeColor,40)});

/* ---- hero video: loads only when it is on screen, after the page finished loading;
        never with data-saver or reduced motion (the poster stays and the controls still work) ---- */
(function(){
  var v=document.getElementById("herov");
  if(!v||!("IntersectionObserver" in window))return;
  var calm=(window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches)||(navigator.connection&&navigator.connection.saveData);
  var visible=false,loaded=document.readyState==="complete";
  function tryPlay(){
    if(calm||!visible||!loaded||!v.getAttribute("src"))return;
    var p=v.play();if(p&&p.catch)p.catch(function(){});
  }
  new IntersectionObserver(function(es){visible=es[0].isIntersecting;if(visible)tryPlay();else v.pause()},{threshold:.25}).observe(v);
  if(!loaded)window.addEventListener("load",function(){
    loaded=true;
    if(window.requestIdleCallback)requestIdleCallback(tryPlay,{timeout:800});else setTimeout(tryPlay,200);
  });
  function flag(){
    var own=false;try{own=!!(typeof S!=="undefined"&&S&&S["heroVideo_"+lang()])}catch(e){}
    document.documentElement.classList.toggle("wb3-hero-specific",own);
  }
  new MutationObserver(function(){flag();tryPlay()}).observe(v,{attributes:true,attributeFilter:["src"]});
  flag();
})();

/* ---- the top bars slide away while you read down and return when you scroll up ---- */
(function(){
  var root=document.documentElement,last=window.scrollY,ticking=false;
  function step(){
    ticking=false;
    var y=window.scrollY,d=y-last;
    if(y<120)root.classList.remove("wb3-compact");
    else if(d>8)root.classList.add("wb3-compact");
    else if(d<-8)root.classList.remove("wb3-compact");
    last=y;
  }
  addEventListener("scroll",function(){if(!ticking){ticking=true;requestAnimationFrame(step)}},{passive:true});
})();

/* ---- haptic tick on taps (Android) ---- */
document.addEventListener("click",function(e){
  if(e.target.closest&&e.target.closest(".tabs .tab,.bnav button,.sec2")){try{navigator.vibrate&&navigator.vibrate(8)}catch(x){}}
},true);

/* ---- pull to refresh inside the installed app (iPhone apps have none of their own) ---- */
var standalone=(window.matchMedia&&matchMedia("(display-mode: standalone)").matches)||navigator.standalone===true;
if(standalone){
  var ind=document.createElement("div");ind.className="wb3-ptr";ind.setAttribute("aria-hidden","true");ind.innerHTML="<span></span>";document.body.appendChild(ind);
  var y0=0,dy=0,active=false,busy=false,TH=72;
  var reset=function(){ind.style.transform="";ind.style.opacity="0";ind.classList.remove("ready")};
  addEventListener("touchstart",function(e){
    if(busy||window.scrollY>0||e.touches.length!==1||document.querySelector(".ov.on"))return;
    y0=e.touches[0].clientY;dy=0;active=true;
  },{passive:true});
  addEventListener("touchmove",function(e){
    if(!active)return;
    dy=e.touches[0].clientY-y0;
    if(dy<=0){active=false;reset();return}
    ind.style.opacity=String(Math.min(dy/TH,1));
    ind.style.transform="translate(-50%,"+Math.min(dy*0.5,60)+"px)";
    ind.classList.toggle("ready",dy>=TH);
  },{passive:true});
  addEventListener("touchend",function(){
    if(!active)return;active=false;
    if(dy>=TH){busy=true;ind.classList.add("spin");ind.style.transform="translate(-50%,56px)";ind.style.opacity="1";setTimeout(function(){location.reload()},350)}
    else reset();
  });
}

/* ---- offline support: the installed app opens even without a connection ---- */
if("serviceWorker" in navigator&&(location.protocol==="https:"||location.hostname==="localhost"||location.hostname==="127.0.0.1")){
  window.addEventListener("load",function(){navigator.serviceWorker.register("sw.js").catch(function(){})});
}

/* ---- v4 · news-terminal front page: main menu and a "Latest" list where every headline shows date • category ---- */
var V4={
  news:{en:"News",es:"Noticias",fr:"Actualités",it:"Notizie",pt:"Notícias",zh:"新闻",ko:"뉴스"},
  markets:{en:"Markets",es:"Mercados",fr:"Marchés",it:"Mercati",pt:"Mercados",zh:"市场",ko:"시장"},
  calendar:{en:"Calendar",es:"Calendario",fr:"Calendrier",it:"Calendario",pt:"Calendário",zh:"日历",ko:"캘린더"},
  videos:{en:"Videos",es:"Vídeos",fr:"Vidéos",it:"Video",pt:"Vídeos",zh:"视频",ko:"동영상"},
  wallie:{en:"Ask Wallie",es:"Pregunta a Wallie",fr:"Demander à Wallie",it:"Chiedi a Wallie",pt:"Pergunta à Wallie",zh:"问 Wallie",ko:"Wallie에게 질문"},
  latest:{en:"Latest news",es:"Últimas noticias",fr:"Dernières actualités",it:"Ultime notizie",pt:"Últimas notícias",zh:"最新消息",ko:"최신 뉴스"},
  all:{en:"See all",es:"Ver todas",fr:"Tout voir",it:"Vedi tutte",pt:"Ver tudo",zh:"查看全部",ko:"전체 보기"},
  week:{en:"Coming up",es:"Próximos eventos",fr:"À venir",it:"In arrivo",pt:"Próximos eventos",zh:"近期事件",ko:"예정 일정"},
  main:{en:"Main menu",es:"Menú principal",fr:"Menu principal",it:"Menu principale",pt:"Menu principal",zh:"主菜单",ko:"메인 메뉴"}
};
function V(k){var o=V4[k];return o[lang()]||o.en}
function escH(s){return String(s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function goTo(g){var b=document.querySelector('#bnav button[data-go="'+g+'"]');if(b)b.click()}
var NAV=[["All","news"],["markets","markets"],["Calendar","calendar"],["Videos","videos"]];
var NEWSCATS=["All","Wall Street","US Politics","Asia","Crypto","ETFs","Macro","Commodities","Companies","Favorites"];
function buildV4(){
  var top=document.querySelector("header.top"),ctl=top&&top.querySelector(".ctl");
  if(top&&ctl&&!top.querySelector(".wb4-nav")){
    var n=document.createElement("nav");n.className="wb4-nav";
    n.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("button");if(b)goTo(b.dataset.go)});
    top.insertBefore(n,ctl);
  }
  var hv=document.getElementById("herov");
  if(hv&&!document.getElementById("wb4week")){
    var w=document.createElement("section");w.id="wb4week";w.className="wb4-week";w.hidden=true;hv.insertAdjacentElement("afterend",w);
  }
  var head=document.getElementById("head");
  if(head&&!document.getElementById("wb4latest")){
    var s=document.createElement("section");s.id="wb4latest";s.className="wb4-latest";head.insertAdjacentElement("afterend",s);
  }
}
function renderNav(){
  var n=document.querySelector(".wb4-nav");if(!n)return;
  var cur="All";try{cur=cat}catch(e){}
  n.setAttribute("aria-label",V("main"));
  n.innerHTML=NAV.map(function(p){
    var on=p[0]===cur||(p[0]==="All"&&NEWSCATS.indexOf(cur)>=0);
    return '<button type="button" data-go="'+p[0]+'"'+(on?' aria-current="true"':"")+'>'+escH(V(p[1]))+'</button>';
  }).join("");
}
function renderLatest(){
  var h=document.getElementById("wb4latest");
  if(!h||typeof S==="undefined"||!S||!S.news||!S.news.length)return;
  h.setAttribute("aria-label",V("latest"));
  var rows=S.news.slice(0,6).map(function(x,i){
    var d=String(x.meta||"").split(" · ")[0],t=typeof LG==="function"?LG(x,"title"):x.title;
    return '<li data-cat="'+escH(x.cat)+'"><a href="#n-'+slugOf(i)+'"><span class="wb4-t">'+escH(t)+'</span><span class="wb4-m">'+escH(d)+' • <b>'+escH(x.cat)+'</b></span></a></li>';
  }).join("");
  h.innerHTML='<div class="wb4-h"><h2>'+escH(V("latest"))+'</h2><button type="button" class="wb4-all">'+escH(V("all"))+' →</button></div><ol>'+rows+'</ol>';
  h.querySelector(".wb4-all").onclick=function(){goTo("All");var f=document.getElementById("feed");if(f)f.scrollIntoView({behavior:"smooth",block:"start"})};
}
function isoToday(){var d=new Date(),m=d.getMonth()+1,k=d.getDate();return d.getFullYear()+"-"+(m<10?"0":"")+m+"-"+(k<10?"0":"")+k}
function renderWeek(){
  var w=document.getElementById("wb4week");if(!w)return;
  var cal=(typeof S!=="undefined"&&S&&S.cal)||[],t=isoToday();
  var up=cal.filter(function(e){return e&&e.date>=t}).sort(function(a,b){return a.date<b.date?-1:a.date>b.date?1:0}).slice(0,5);
  if(!up.length){w.hidden=true;w.innerHTML="";return}
  var loc=({zh:"zh-CN",ko:"ko-KR"})[lang()]||lang();
  var rows=up.map(function(e){
    var d;try{d=new Date(e.date+"T12:00:00").toLocaleDateString(loc,{weekday:"short",day:"numeric",month:"short"})}catch(x){d=e.date}
    var title=typeof LG==="function"?LG(e,"title"):e.title,imp=e.imp==="high"||e.imp==="medium"?e.imp:"low";
    return '<li><a href="#" data-go="Calendar"><span class="wb4-t">'+escH(title)+'</span><span class="wb4-m"><i class="'+imp+'" aria-hidden="true"></i>'+escH(d)+(e.time?" • "+escH(e.time):"")+'</span></a></li>';
  }).join("");
  w.hidden=false;w.setAttribute("aria-label",V("week"));
  w.innerHTML='<div class="wb4-h"><h2>'+escH(V("week"))+'</h2><button type="button" class="wb4-all" data-go="Calendar">'+escH(V("all"))+' →</button></div><ol>'+rows+'</ol>';
  w.onclick=function(e){var a=e.target.closest&&e.target.closest("[data-go]");if(a){e.preventDefault();goTo(a.dataset.go)}};
}
function paintV4(){buildV4();renderNav();renderLatest();renderWeek()}
try{
  if(typeof renderAll==="function"){var _ra=renderAll;renderAll=function(){var r=_ra.apply(this,arguments);paintV4();return r}}
  if(typeof navOn==="function"){var _no=navOn;navOn=function(){var r=_no.apply(this,arguments);renderNav();return r}}
}catch(e){}
paintV4();
})();
