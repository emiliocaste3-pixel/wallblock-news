# WallBlock News

Web de noticias de mercados (Wall Street, Asia, cripto, ETF, materias primas, macro y empresas), en inglés y español, con los agentes **Wallie**, **Bullish** y **Bearish**.

Es una web **estática**: no necesita servidor ni base de datos.

```
src/content.json   ← fuente única: noticias, mercados, calendario, vídeos, textos legales
src/build.py       ← generador (solo librería estándar de Python)
src/site.css, site.js, markets.js
public/            ← salida lista para subir (HTML, CSS, JS, imágenes, vídeos, sitemap, robots, cabeceras)
docs/              ← DEPLOY.md (publicar), DATOS-EN-VIVO.md, PROMPT-PERFECCIONAR.md
qa/                ← pruebas: accesibilidad (axe), capturas, mapa de burbujas y widgets
LOG.md             ← registro de mediciones
```

## Uso rápido

```bash
python3 src/build.py                                   # genera public/ (URLs limpias)
SITE_URL=https://tu-dominio.com python3 src/build.py   # con tu dominio (canonical, sitemap, hreflang)
python3 src/build.py --preview --out preview           # enlaces terminados en index.html, para visores sin servidor
```

Para actualizar noticias: edita `src/content.json` (o pide una ronda de noticias), reconstruye y sube `public/`. Guía completa en `docs/DEPLOY.md`.

Páginas: portada, 8 secciones, Mercados en vivo (mapa de burbujas + widgets de TradingView con consentimiento), Calendario, Vídeos, Quiénes somos, Privacidad, Términos, Aviso legal y Contacto, en `/` (EN) y `/es/` (ES).

> Informativo. No es asesoramiento financiero.
