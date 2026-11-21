# Publicar WallBlock News

La web es **estática**: carpeta `public/` (HTML, CSS, JS, imágenes y vídeos). Sirve en Netlify, Hostinger o cualquier hosting.

## 0. Construir y empaquetar

```bash
# La dirección pública se usa en canonical, sitemap y hreflang. Cámbiala cuando tengas dominio.
SITE_URL=https://tu-dominio.com python3 src/build.py
mkdir -p dist && (cd public && zip -r ../dist/wallblock-news-site.zip . -x '.DS_Store')
```

Sin `SITE_URL` se usa `https://remarkable-flan-83896d.netlify.app`.

## A. Netlify (ahora, sin dominio propio)

1. En Netlify abre el sitio `remarkable-flan-83896d` → **Deploys**.
2. Arrastra la carpeta `public/` (o el contenido del ZIP descomprimido) a la zona "Drag and drop".
3. Espera a "Published" y abre la dirección. Netlify lee `_headers` solo.
4. Si prefieres terminal: `npx netlify deploy --dir=public --prod --site <id-del-sitio>`.

## B. Hostinger (cuenta nueva)

Pasos de memoria; la interfaz de Hostinger cambia, así que si algún botón se llama distinto, busca el equivalente.

1. Entra en hostinger.es (también desde el móvil) → **Hosting web** → elige un plan compartido. Para esta web estática vale el más básico que incluya SSL gratuito; compara el precio de **renovación**, no solo el del primer periodo.
2. Crea la cuenta con tu correo (o Google) y paga en la página de Hostinger. **Nunca pongas datos de tarjeta en el chat.**
3. Elige dominio: si el plan incluye uno gratis, reclámalo; si no, compra uno (por ejemplo `wallblocknews.com`) con protección de privacidad WHOIS activada.
4. En **hPanel → Sitios web → Añadir sitio web**, elige subir/crear un sitio vacío. No instales WordPress.
5. **Archivos → Administrador de archivos → `public_html`**: borra `default.php` o `index.php` si existen.
6. Pulsa **Subir**, elige `wallblock-news-site.zip`, y luego clic derecho → **Extraer** dentro de `public_html` (el `index.html` debe quedar directamente en `public_html`, no en una subcarpeta). Activa "mostrar archivos ocultos" para ver `.htaccess`.
7. **Seguridad → SSL**: instala el certificado gratuito y activa **Forzar HTTPS**.
8. Abre tu dominio en el móvil y en el ordenador y comprueba: portada, cambio EN/ES, una categoría, Calendario, Mercados en vivo (el botón de cargar widget) y un vídeo.
9. Dime el dominio: reconstruyo con `SITE_URL` y regenero el ZIP (el `canonical` debe apuntar a tu dominio final).

## C. Google Search Console

1. Entra en https://search.google.com/search-console con tu cuenta de Google.
2. **Añadir propiedad → Prefijo de URL** y escribe la dirección exacta con `https://` (por ejemplo `https://tu-dominio.com/`).
3. Verificación por **Etiqueta HTML**: copia la línea `<meta name="google-site-verification" content="...">`, dímela y la dejo en el `<head>` (o añade tú el archivo HTML que te dan a `public/`). Publica de nuevo y pulsa Verificar.
4. **Sitemaps** → escribe `sitemap.xml` → Enviar.
5. **Inspección de URL** → pega la portada → **Solicitar indexación**. Repite con `/markets/` y `/es/`.
6. Tarda de días a semanas. Comprueba con `site:tu-dominio.com` en Google.

## D. Antes de pedir indexación

- Sustituye el correo/contacto: la página Contacto solo enlaza a Telegram; añade un correo real.
- Revisa Privacidad: menciona TradingView y CoinGecko (solo se cargan con tu clic).
- Subtítulos (WebVTT) en los vídeos con voz.
- Cambia la imagen social `public/img/og.png` si quieres otra (1200×630).
