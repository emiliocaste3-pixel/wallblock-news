# Pruebas de calidad

Requisitos: `npm i -D playwright axe-core` y un servidor local sobre la carpeta `public/`:

```bash
python3 src/build.py --preview --out preview && (cd preview && python3 -m http.server 8099) &
node qa/axe.js         # accesibilidad (axe, WCAG 2.2 AA) en 8 páginas y 2 anchos
node qa/shots.js qa/out   # capturas y desbordes en 3 anchos
node qa/markets.js qa/out # mapa de burbujas y widgets con servicios externos simulados
```

Lighthouse: `npx lighthouse http://127.0.0.1:8098/ --only-categories=performance,accessibility,best-practices,seo --chrome-flags="--headless=new --no-sandbox"` (sirviendo `public/` en 8098).
Imagen social: `qa/og.html` → captura 1200×630 a `public/img/og.png`.
