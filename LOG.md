# Registro de mejoras · WallBlock News para Hostinger

**Regla acordada:** la web no se sube hasta cumplir todas las puertas de calidad de abajo, medidas con herramientas
y no por opinión. Cada ronda anota qué se midió, qué se encontró, qué se cambió y cómo se comprobó.

## Estado actual

**✅ Cumple las puertas medibles. Lista para subir**, con los puntos que dependen de ti anotados al final.
Última medición: 13 nov 2026, sobre el contenido exacto del zip, servido con compresión y caché como en Hostinger.

## Puertas de calidad y resultado

| # | Puerta | Umbral | Antes | Ahora |
|---|---|---|---|---|
| P1 | Funcional: sin desbordes en 6 anchos, 18 pestañas, 7 idiomas, 0 errores de consola, 0 respuestas ≥400, 0 peticiones externas | todo a 0 | 1 error de consola (mío), 1 petición externa (Google Fonts) | **0 / 0 / 0** |
| P2 | Accesibilidad (Lighthouse + axe + contraste por píxeles en los 7 temas) | Lighthouse ≥ 95, 0 violaciones axe, 0 fallos de contraste | Lighthouse 96, 4 violaciones axe | **100, 0 violaciones, 0 fallos en 1.617 controles de contraste** |
| P3 | Rendimiento móvil (Lighthouse, 4G lenta, CPU 4× más lenta, mediana de 3) | ≥ 90, LCP ≤ 2,5 s, CLS ≤ 0,1, TBT ≤ 200 ms | 79, LCP 3,0 s, CLS 0,143, TBT 420 ms | **95, LCP 2,48 s, CLS 0,007, TBT 150–180 ms** |
| P3b | Rendimiento escritorio | ≥ 90, CLS ≤ 0,1 | 76, CLS 0,697 | **100, CLS 0,003** |
| P4 | Buenas prácticas y SEO (Lighthouse) | ≥ 95 | 100 / 100 | **100 / 100** |
| P5 | Visual: revisión de capturas en móvil, tablet, escritorio, tema oscuro y claro, coreano y francés | sin texto cortado, solapado ni enlaces rotos | 3 enlaces rotos, texto cortado en mapa de calor | **cumplido (ver ronda 4)** |
| P6 | Contenido: 7 idiomas completos, sin textos de borrador | 0 huecos | 56 traducciones que faltaban | **0 que faltan** |
| P7 | Apto para Hostinger: sin claves ni archivos privados, `.htaccess` seguro, PHP sin errores, sin contenido mixto | todo limpio | n/a | **limpio** |

Peso de la página en móvil: **3,4 MB → 403 KB**. Zip: 55 MB iniciales → 18,6 MB.

## Rondas

### Ronda 0 · Línea base (13 nov)
Se midió la web tal como estaba: Lighthouse móvil 79 y escritorio 76, accesibilidad 96, CLS 0,143 móvil y 0,697 escritorio.
Hallazgos: la página se dibujaba **tres veces** al abrir (datos incrustados, datos de `content.json` y capa v2), 134 KB de contenido
duplicado dentro del HTML, el vídeo principal (1,9 MB) se descargaba aunque no se viera, tres avatares de 520 KB pintados a 60 px,
fuentes desde Google, y cuatro fallos de accesibilidad (contraste del botón de Telegram, etiquetas de las fichas de mercado,
pie fuera de zona de navegación, fila de vídeos con scroll sin teclado).

### Ronda 1 · Dibujar una sola vez y adelgazar
- La página carga `content.json` una sola vez (con precarga), se dibuja una vez y se muestra ya completa. **CLS móvil 0,143 → 0,004.**
  Se eliminó la copia de 114 KB de datos que iba dentro del HTML.
- Vídeo principal: no descarga nada hasta que se ve, tras cargar la página, y nunca con ahorro de datos o movimiento reducido.
- Imágenes: iconos de 542 KB a 76 KB, avatares de 520 KB a 18 KB (WebP 160 px), carteles de vídeo de 500 a 220 KB.
- Móvil: el navegador se salta estilo, maquetación y pintado de lo que está fuera de pantalla (`content-visibility`).
- Cabecera: la marca no se encoge (causa del CLS de escritorio) y las fuentes de reserva tienen las medidas de las reales.
- Se quitó mi botón «Install app» duplicado (la página ya traía uno) y los degradados de las tarjetas.
- **Resultado:** móvil 79 → 96, escritorio 76 → 99.
- Probado y descartado por no aportar nada medible: incrustar el CSS en el HTML, quitar la precarga de Inter (empeoraba TBT),
  quitar el desenfoque de la barra inferior. El LCP móvil queda marcado por red + CPU en el laboratorio (~2,5 s).

### Ronda 2 · Accesibilidad y contraste, con un método propio
axe no puede medir texto sobre degradados, así que se escribió una comprobación independiente (`qa/pixelcontrast.js`): borra el texto,
fotografía el fondo real bajo cada letra y calcula el contraste píxel a píxel, con la opacidad heredada.
Encontró y se corrigió: mapa de calor en tema claro (verde pastel con texto blanco), etiqueta «MARKET OPEN» (3,2:1), nombre «Bearish» (3,6:1),
etiquetas de categoría (4,1–4,3:1), líneas «Fuente» de los paneles (3,7:1 por una opacidad del 80 %), gris de los temas claros,
fecha de la franja de última hora, botón activo de la barra inferior en el tema fucsia, texto de botones del fucsia.
Dos falsos positivos del propio medidor se afinaron (texto tapado por la barra fija; etiquetas con icono).
**Resultado: 0 fallos en 7 temas × 2 tamaños.**

### Ronda 3 · Experiencia de app
- Las barras de arriba se esconden al leer hacia abajo y vuelven al subir (móvil y escritorio): se recupera ~25 % de pantalla.
- En móvil el vídeo principal ya no repite el clip que aparece justo debajo en «Featured videos» (solo se muestra si hay intro propia del idioma).
- Instalable como app, funciona sin conexión (service worker «red primero»), tirar para recargar en la app instalada.

### Ronda 4 · Diseño y enlaces
- **3 enlaces rotos eliminados** del pie (`registro.html`, `app.html`, `pago.html`: esas páginas no existen en el paquete).
- Cuatro botones de redes sociales sin enlace (TikTok, Instagram, YouTube, Facebook) eliminados: ahora solo se muestran las que
  tengan enlace en `content.json` (`site.socials`). Telegram ya no aparece duplicado.
- «SUBSCRIBE / FOLLOW US!!» (igual en los 7 idiomas) → «Follow us» traducido.
- Casillas del mapa de calor cortadas en móvil («Russell 2000», «STOXX 600»): ahora crecen.
- Valor de panel «−104 M$» ya no se parte en dos líneas. Nombres del equipo legibles en los temas claros.

### Ronda 5 · Contenido, traducciones y privacidad
- 56 traducciones que faltaban (5 paneles de datos y la intro en español para francés, italiano, portugués, chino y coreano).
- Textos de bolsa con inglés dentro del dato («Wed close», «intraday», «premarket») → traducidos.
- **Política de privacidad:** decía que, si el lector está conectado a Claude, su pregunta la procesa Claude. En Hostinger eso no ocurre.
  Se sustituyó, en los 7 idiomas, por una frase exacta y neutra. **Revísala tú** (es texto legal).

### Ronda 6 · Verificación final y un error propio cazado
Se repitió toda la batería con el contenido exacto del zip. La batería detectó una **regresión mía**: una función auxiliar usada
fuera de su alcance dejaba la página sin ninguna noticia. Se corrigió y se repitió todo desde cero. Sin esa repetición habría salido a producción.
Resultado final: ver la tabla de arriba. Además: 9 pruebas de extremo a extremo (servicio PHP de Wallie, enlace por noticia, tirar para recargar),
modo sin conexión, 87 archivos en el zip sin claves ni archivos privados.

## Lo que no se pudo comprobar y lo que depende de ti

1. **Servicio de Wallie con IA contra la API real de Anthropic:** solo se probó contra un servidor que imita su formato. Hazle una pregunta
   tras activarlo (necesita tu clave en `api/config.php`). Sin clave, la web funciona con respuestas locales.
2. **Dominio:** sin él no se puede añadir `canonical`, imagen para compartir en redes ni `sitemap`, y no se puede probar la instalación como app
   ni el modo sin conexión con HTTPS real.
3. **Textos legales:** revisa la privacidad (ronda 5) y añade un contacto en `site.contact`.
4. **Contenido de noticias:** los datos son del 11–12 de noviembre. Los actualizas editando `content.json`.
5. **Dribbble:** no se pudo abrir (protección anti-bots). El estilo sigue las líneas habituales del diseño fintech moderno, no un shot concreto.
6. **LCP móvil 2,48 s en laboratorio:** cumple el umbral por muy poco. En un móvil real con Hostinger (HTTP/2, Brotli) debería ser mejor, pero no se ha medido.
7. **GitHub:** los commits están en la rama `claude/hostinger-redesign` del contenedor; la subida a GitHub sigue bloqueada por permisos de la app de Claude.
