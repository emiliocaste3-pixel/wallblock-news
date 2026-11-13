# WallBlock News · subir a Hostinger

La web es 100 % estática (HTML + JSON + imágenes + vídeos). No necesita PHP ni base de datos.

## 1. Subir la web

1. En el repositorio, ejecuta `./build-hostinger.sh` (o usa el `wallblock-hostinger.zip` ya generado).
2. En **hPanel → Archivos → Administrador de archivos**, abre `public_html`.
   Si hay un `default.php` o `index.php` de Hostinger, bórralo para que mande `index.html`.
3. Sube el `.zip` a `public_html` y pulsa **Extraer**. Deben quedar `index.html`, `content.json`,
   `.htaccess`, `assets/`, `img/`, `fonts/` directamente dentro de `public_html` (no dentro de otra carpeta).
   El `.htaccess` es un archivo oculto: activa "mostrar archivos ocultos" para verlo.
4. En **hPanel → Seguridad → SSL**, activa **Forzar HTTPS**.
5. Abre tu dominio y comprueba que carga, que cambia el idioma y que se ven los vídeos.

## 2. Actualizar noticias, precios y datos

Todo el contenido está en `content.json` (noticias, calendario, paneles, mapa de calor, vídeos, planes, textos legales).
Edítalo y vuelve a subir solo ese archivo. El navegador siempre pide la versión más reciente
(el `.htaccess` desactiva su caché).

Cada noticia admite, además de título y texto, una **foto opcional**:

```json
{
  "cat": "Wall Street",
  "title": "...",
  "text": "...",
  "image": "assets/mi-foto.jpg",
  "image_alt": "Descripción de la foto",
  "image_credit": "Foto: Agencia / Autor"
}
```

Sin `image`, la noticia se ve igual que antes. Usa solo fotos con licencia o propias y pon el crédito.

## 3. Vídeos

Cada vídeo `assets/xxxx.mp4` usa como miniatura `assets/xxxx.jpg` (mismo nombre). Si añades un vídeo nuevo,
crea su miniatura, por ejemplo: `ffmpeg -ss 3 -i xxxx.mp4 -frames:v 1 -vf scale=960:-2 -q:v 6 xxxx.jpg`.

## 3b. Vídeo principal por idioma

`content.json` tiene `heroVideo` (el vídeo de la cabecera para todos los idiomas). Puedes poner uno distinto por idioma
con `heroVideo_es`, `heroVideo_fr`, `heroVideo_it`, `heroVideo_pt`, `heroVideo_zh`, `heroVideo_ko`.
Ahora mismo `heroVideo_es` apunta a `assets/wallblock-intro-es.mp4` (intro con voz y subtítulos en español).

## 3c. App móvil (instalable)

La web incluye `manifest.webmanifest` e iconos (192, 512 y maskable), así que en el móvil se puede instalar:
- **Android (Chrome):** menú ⋮ → "Instalar app" / "Añadir a pantalla de inicio".
- **iPhone (Safari):** Compartir → "Añadir a pantalla de inicio".

Se abre a pantalla completa, con el icono de WallBlock. En Android y en Chrome de escritorio aparece además un botón
**"Install app"** en la cabecera. La app instalada **abre sin conexión** con las últimas noticias que vio
(`sw.js`: siempre pide primero la versión nueva a la red y solo usa la copia guardada si no hay conexión;
los vídeos no se guardan). Si algún día cambias la estrategia de `sw.js`, cambia `CACHE` ("wb-v1" → "wb-v2").

Capa visual y de app: `wb3.css` (cristal, brillos, barra inferior flotante, hojas inferiores en móvil) y
`wb3.js` (botón de compartir en cada noticia, botón de instalar, color de la barra de estado según el tema).
Las rutas `wb3.css?v=1` y `wb3.js?v=1` van en `index.html`: si los cambias, sube el número (`?v=2`). En móvil la página prioriza las noticias (titular, secciones,
búsqueda y noticias primero; vídeos, paneles, mapa de calor, calendario y relojes después).

## 4. Lo que NO funciona en Hostinger (y por qué)

- **Botón "Editar web" y subida de vídeos desde la página:** solo existen dentro de Claude. En Hostinger se edita `content.json`.
- **Chat de Wallie con IA:** por defecto responde con las noticias de la página (respuestas locales). Para activar la IA real
  mira la sección 4b.
- **Textos legales:** `site.privacy` menciona que, si el lector está conectado a Claude, su pregunta se procesa con Claude.
  En Hostinger eso no ocurre; conviene revisar ese párrafo en `content.json` (los 7 idiomas) y añadir un contacto en `site.contact`.

## 4b. Wallie con IA real (opcional)

La carpeta `api/` trae `wallie.php`. Para activarlo:
1. En el Administrador de archivos, entra en `public_html/api/`, copia `config.sample.php` como `config.php`
   y pon tu clave de Anthropic en `api_key` (la clave solo vive en tu servidor; `config.php` no va en el zip ni en el repositorio).
2. Ajusta los límites si quieres (`limit_per_hour` = preguntas por visitante y hora, `limit_per_day` = total diario de la web).
3. Prueba la pestaña "Ask Wallie". Si algo falla, la web sigue respondiendo con las respuestas locales.

Qué hace el servicio: lee las noticias él mismo desde `content.json` (el navegador no puede colarle texto), valida cada pregunta
(máx. 500 caracteres), limita el uso por visitante y por día, no guarda las preguntas (solo contadores, en `api/_data/`)
y bloquea peticiones de otros sitios. Los modelos (`model_wallie`, `model_chat`) y los límites se cambian en `config.php`.
Necesita PHP 7.4 o superior con cURL (lo normal en Hostinger; se elige en hPanel → Avanzado → Configuración de PHP).
**Importante:** no se ha podido probar contra la API real de Anthropic desde aquí (solo contra un servidor que imita su
formato); haz una pregunta de prueba tras activarlo. El gasto depende de tu plan de API: con los límites por defecto
el máximo es de 500 preguntas al día en toda la web.

## 4c. Enlace propio por noticia

Cada noticia tiene su dirección, por ejemplo `https://tudominio.com/#n-nasdaq-jumps-1-8-as-the-ai-trade-returns`
(se forma con el título en inglés). El botón de compartir de cada noticia usa ese enlace y, al abrirlo, la web se desplaza
hasta la noticia y la resalta. Si cambias el título en inglés de una noticia, su enlace cambia.

## 5. Pendiente de tu dominio

Para previsualizaciones al compartir enlaces (Open Graph con imagen) y para el `canonical` hace falta la URL final del dominio.
Cuando la tengas, se añaden en `index.html`.
