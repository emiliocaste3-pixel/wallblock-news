# Pruebas de calidad (no se suben a Hostinger)

Estos scripts son los que usó `LOG.md`. Necesitan Node 20+, `playwright` (Chromium), `lighthouse`, `axe-core` y `pngjs`:

```bash
cd qa && npm init -y && npm i playwright lighthouse axe-core pngjs && npx playwright install chromium
```

1. Genera el paquete y sírvelo como lo haría Hostinger (gzip + caché):
   ```bash
   ../build-hostinger.sh && mkdir -p /tmp/site && cd /tmp/site && unzip -oq ../path/to/wallblock-hostinger.zip
   node qa/serve.js /tmp/site 8100
   ```
2. Rendimiento (Lighthouse móvil y escritorio): `npx lighthouse http://127.0.0.1:8100/ --only-categories=performance,accessibility,best-practices,seo --output=json --output-path=lh.json` y `node qa/lhsum.js lh.json`.
3. Accesibilidad con axe: `node qa/axe.js` (temas oscuro y claro, móvil y escritorio).
4. Contraste por píxeles, independiente de axe, en los 7 temas: `node qa/pixelcontrast.js blue,emerald,gold,violet,cobalt,fuchsia,orange 390x844x1` (y `1350x940x0`).
5. Saltos de maquetación: `node qa/cls.js http://127.0.0.1:8100/ 1350x940x0`.
6. Servicio de Wallie, enlaces por noticia y app (necesita `php`): `qa/e2e-wallie-php.js`.
