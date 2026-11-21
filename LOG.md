# Registro de calidad · WallBlock News

## Ronda 1 · 21 nov 2026 (rediseño y primera ronda de noticias)

**Qué se hizo**
- Web estática nueva (aubergine/crema/salvia), avatares oficiales Wallie, Bullish y Bearish, EN + ES, 34 páginas.
- Contenido al cierre del viernes 20 nov (2 noticias por categoría, EN y ES, con fuentes). Datos sin verificar se dejaron fuera (FTSE, Shanghái, divisas, ether del viernes).
- Mercados en vivo: mapa de burbujas propio (canvas) y widgets de TradingView con consentimiento; precios cripto en vivo (CoinGecko) opcionales.
- Cabeceras de seguridad (`_headers`, `.htaccess`), sitemap con hreflang, robots, manifest, imagen social.

**Medición** (Lighthouse móvil simulado 4G lenta; axe WCAG 2.2 AA)
| Puerta | Resultado |
|---|---|
| axe: 8 páginas × 390 y 1440 px | 0 violaciones |
| Lighthouse portada EN y ES | rendimiento 97, accesibilidad 100, buenas prácticas 100, SEO 100 |
| Lighthouse /markets/ | rendimiento 99, accesibilidad 100, buenas prácticas 100, SEO 100 |
| CLS / TBT | 0 / 0–10 ms |
| LCP | 2,6 s simulado (el navegador mide ~0,2 s reales); objetivo 2,5 s |
| Peso portada | 287 KB |
| Errores de consola / respuestas ≥ 400 | 0 / 0 |
| Desbordes horizontales (390, 820, 1440 px) | ninguno |

**Pendiente / no comprobado**
- Widgets de TradingView y precios de CoinGecko: probados con servicios simulados; falta verlos en un despliegue real (el entorno no llega a esos dominios). Revisar la CSP en ese momento.
- Subtítulos (WebVTT) de los vídeos con voz.
- Contacto con correo real; revisar Privacidad (menciona favoritos/temas/voz de la web anterior).
- Instantánea de acciones del S&P 500 (30 valores) es del 20 nov a la 1:45 pm ET; ether y 7 valores de cripto no verificados con segunda fuente.
- Otros idiomas (fr, it, pt, zh, ko) no incluidos en esta versión.
