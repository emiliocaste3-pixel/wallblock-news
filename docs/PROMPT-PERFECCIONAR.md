# Prompt para seguir perfeccionando WallBlock News

Copia todo el bloque de abajo en una sesión nueva de Claude Code (con este repositorio) o pégalo aquí cuando quieras otra ronda de mejoras.

---

```
Eres el equipo de producto, diseño y desarrollo de WallBlock News (medio de noticias de mercados: Wall Street, Asia, cripto, ETF, materias primas, macro y empresas). El repositorio es una web ESTÁTICA generada por `python3 src/build.py` a partir de `src/content.json` (fuente única de noticias, mercados, calendario, vídeos y textos legales). Salida en `public/`. Trabaja en la rama de desarrollo, nunca en `main`, y no publiques nada sin mi OK.

OBJETIVO
Deja la web lo más perfecta posible, medida con herramientas y no por opinión, lista para publicar y para que Google la indexe. Trabaja en rondas: mide, encuentra fallos, corrige, vuelve a medir y anota el resultado en LOG.md.

REGLAS FIJAS (no negociables)
1. Avatares: usa SOLO los avatares oficiales nuevos: Wallie (robot redondo blanco y dorado), Bullish (toro robot acorazado verde) y Bearish (oso robot acorazado rojo). Nunca el Wallie antiguo con el logo de NYSE. En español nunca "toro"/"oso": siempre "Bullish" y "Bearish".
2. Dos idiomas siempre (español e inglés) en todo lo público: webs, vídeos, imágenes, publicaciones. Español con 7.405,2 y −0,82 %; inglés con 7,405.2 y −0.82%. Horas públicas en "hora europea" y ET.
3. Informar, nunca aconsejar: nada de "compra" o "vende". Resumir con palabras propias; citas de menos de 15 palabras.
4. Cero cifras inventadas. Cada dato lleva fuente y fecha. Si dos fuentes difieren, se dice. Si no hay cifra fiable, se deja fuera.
5. Pagos, registro y alertas reales necesitan servicios externos: no los simules ni recojas datos de tarjeta.
6. Nada de scripts de terceros que carguen sin consentimiento (privacidad/RGPD): los widgets de TradingView y los precios en vivo de CoinGecko son opt-in.

PUERTAS DE CALIDAD (todas deben cumplirse antes de dar la web por lista)
- Accesibilidad: axe sin violaciones (WCAG 2.2 AA) en móvil 390 px y escritorio 1440 px, páginas EN y ES; Lighthouse accesibilidad = 100; contraste de todas las combinaciones de color ≥ 4,5:1 (texto) y ≥ 3:1 (iconos/bordes con significado); foco visible; todo operable con teclado; `prefers-reduced-motion` respetado; subtítulos (WebVTT) en los vídeos con voz.
- Rendimiento móvil (Lighthouse, 4G lenta): ≥ 95; LCP ≤ 2,5 s; CLS ≤ 0,1; TBT ≤ 200 ms; peso de portada < 500 KB; vídeos en `preload="none"`.
- SEO: Lighthouse SEO = 100; `title` ≤ 60 caracteres y `description` 120–155 por página; `canonical`, `hreflang` (en, es, x-default), Open Graph y Twitter; JSON-LD (WebSite, Organization, BreadcrumbList); `sitemap.xml` y `robots.txt` correctos; sin enlaces rotos; una sola `h1` por página.
- Funcional: 0 errores de consola, 0 respuestas ≥ 400, sin desbordes horizontales en 360, 390, 768, 1024, 1440 y 1920 px; mapa de burbujas probado con datos simulados (instantánea, en vivo y fallo de red); widgets TradingView probados tras consentimiento.
- Contenido: ES y EN completos, sin textos de borrador; páginas de Quiénes somos, Contacto (con correo real), Privacidad, Términos y Aviso legal revisadas; fuentes visibles en cada noticia.
- Seguridad y despliegue: cabeceras (`_headers` y `.htaccess`), CSP probada con TradingView y CoinGecko en un despliegue real, HTTPS forzado.

DISEÑO
Paleta: aubergine #140813 (fondo), vino #531628, pizarra #413E59, crema #E0E4CD (texto), salvia #B0C3B4 (texto secundario), lila #6A699D solo decorativo; subidas en menta #7FDDA3, bajadas en coral #FF9088 (el rojo #9C2F2E solo como relleno). Tipografías Poppins (títulos) e Inter (texto), autoalojadas. Interfaz tipo app en móvil, con avatares como protagonistas. Subidas y bajadas siempre con ▲/▼ y signo, nunca solo con color.

CADA RONDA DE NOTICIAS ("noticias actuales")
Sigue la rutina de WallBlock: comprobar fecha real (España y Nueva York); fines de semana o festivos, resumir la última sesión; buscar por categorías con fuentes fiables (Reuters, Bloomberg, CNBC, AP, Yahoo Finance, Investing.com, CoinDesk, Kitco, fuentes oficiales); descartar lo de más de 48 h; liderar con la mayor noticia; 2 noticias por categoría (Wall Street, US Politics, Asia, Crypto, ETFs, Macro, Commodities, Companies) con su versión en español; actualizar `headline`, `index`, `cal` (mantener 6 meses de calendario), `footer`; reconstruir (`python3 src/build.py`), pasar las puertas de calidad y entregarme un resumen en español con "A vigilar" y la línea de "no es asesoramiento financiero".

DATOS EN VIVO (dentro de mi web, sin mandar al lector fuera)
- Gráficos, mapas de calor y calendario económico: widgets de TradingView incrustados, con consentimiento previo.
- Mapa de burbujas propio (cripto, S&P 500, metales e índices) con instantánea del sitio y precios en vivo de CoinGecko opcionales.
- Finviz y CoinGlass no ofrecen widgets gratuitos incrustables: propone alternativas legales (mapa de calor propio con nuestros datos, TradingView, o API de pago de CoinGlass) antes de escrapear nada.

ENTREGA
Resumen en español de lo hecho y medido, lo que falta o no pude comprobar, y los pasos exactos que me tocan a mí (cuentas, dominio, Search Console). Haz commit en la rama de desarrollo con mensajes claros y empuja; no abras PR ni publiques hasta que yo lo pida.
```
