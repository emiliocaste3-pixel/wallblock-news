/* WallBlock News · progressive enhancement only. The site works without this file. */
(function () {
  var chips = document.querySelectorAll('.chips [data-filter]');
  var cards = document.querySelectorAll('.cards .story');
  var status = document.getElementById('filter-status');
  if (!chips.length || !cards.length) return;

  function apply(cat, announce) {
    var shown = 0;
    cards.forEach(function (c) {
      var ok = cat === '*' || c.getAttribute('data-cat') === cat;
      c.hidden = !ok;
      if (ok) shown++;
    });
    chips.forEach(function (b) {
      var on = b.getAttribute('data-filter') === cat;
      if (on) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
      b.classList.toggle('on', on);
    });
    if (announce && status) status.textContent = shown + ' / ' + cards.length;
  }

  chips.forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.preventDefault();
      var cat = b.getAttribute('data-filter');
      apply(cat, true);
      if (history.replaceState) {
        history.replaceState(null, '', cat === '*' ? location.pathname + '#latest' : '#cat-' + encodeURIComponent(cat));
      }
    });
  });

  var m = location.hash.match(/^#cat-(.+)$/);
  if (m) apply(decodeURIComponent(m[1]), false);
})();

/* Video posters load only when the video is near the viewport (keeps the first paint light). */
(function () {
  var vids = [].slice.call(document.querySelectorAll('video[data-poster]'));
  if (!vids.length) return;
  function set(v) { v.poster = v.getAttribute('data-poster'); v.removeAttribute('data-poster'); }
  if (!('IntersectionObserver' in window)) { vids.forEach(set); return; }
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); set(e.target); } });
  }, { rootMargin: '300px' });
  vids.forEach(function (v) { io.observe(v); });
})();
