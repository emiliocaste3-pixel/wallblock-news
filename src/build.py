#!/usr/bin/env python3
"""WallBlock News static site generator.

Reads src/content.json (the single source of truth for news, markets, calendar,
videos and legal text) and writes a fully static, crawlable site into an output
folder.  No dependencies beyond the Python standard library.

  python3 src/build.py                 -> public/        (production URLs: /calendar/)
  python3 src/build.py --preview       -> public/        (links end with index.html)
  python3 src/build.py --out DIR       -> custom output folder (assets are copied in)

Environment:
  SITE_URL     public address used for canonical / sitemap / hreflang
  BUILD_DATE   YYYY-MM-DD, defaults to today
"""
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
ARGS = sys.argv[1:]
PREVIEW = "--preview" in ARGS
OUT = ROOT / (ARGS[ARGS.index("--out") + 1] if "--out" in ARGS else "public")
STATIC = ROOT / "public"          # binary assets (fonts, img, assets) live here
SITE_URL = os.environ.get("SITE_URL", "https://remarkable-flan-83896d.netlify.app").rstrip("/")
TODAY = dt.date.fromisoformat(os.environ.get("BUILD_DATE", dt.date.today().isoformat()))
LANGS = ["en", "es"]
LOCALE = {"en": "en_US", "es": "es_ES"}

D = json.loads((SRC / "content.json").read_text(encoding="utf-8"))
E = lambda s: html.escape(str(s), quote=True)

# --------------------------------------------------------------------------- i18n
UI = {
    "en": {
        "skip": "Skip to content", "main_nav": "Main", "latest": "Latest", "calendar": "Calendar", "videos": "Videos",
        "about": "About", "sections": "Sections", "language": "Language", "home": "Home",
        "markets": "Markets", "markets_sub": "Prices from the latest update. Levels keep changing; not a quote service.",
        "bb_title": "Two views of the market", "bb_sub": "Bullish and Bearish read the same screen. Here is what moved most in our tracked list.",
        "bull": "Bullish", "bear": "Bearish", "bull_tag": "The bull case", "bear_tag": "The bear case",
        "risers": "Biggest risers", "fallers": "Biggest fallers", "wallie_tag": "Your market guide",
        "wallie_cta": "Ask Wallie on Telegram", "read_latest": "Read the latest",
        "wallie_text": "Wallie is our guide through the day's news. Bullish and Bearish show both sides of every move.",
        "stories": "Latest stories", "stories_sub": "Every story links its sources. We summarize; we do not give advice.",
        "all": "All", "sources": "Sources", "top_story": "Top story", "updated": "Updated",
        "coming_up": "Coming up", "coming_sub": "Data releases, central banks, earnings and market holidays. Times in US Eastern (ET).",
        "full_calendar": "Full calendar", "all_videos": "All videos", "watch": "Watch",
        "videos_title": "Videos", "videos_sub": "Short market explainers and intros from the WallBlock team.",
        "videos_desc": "Short market explainers, intros and Wall Street open videos from the WallBlock News team with Wallie, Bullish and Bearish.",
        "team_title": "Meet the team", "team_sub": "Three guides, one goal: make the market easier to read.",
        "importance": {"high": "High impact", "medium": "Medium impact", "low": "Low impact"},
        "footer_sections": "Sections", "footer_info": "Information", "footer_follow": "Follow",
        "disclaimer_short": "For information only. Not investment advice.",
        "contact": "Contact", "privacy": "Privacy", "terms": "Terms", "disclaimer": "Disclaimer",
        "no_stories": "No stories in this section yet.", "back_home": "Back to the latest news",
        "cal_title": "Economic calendar", "cal_sub": "US data, central banks, earnings and market holidays. Times in US Eastern (ET).",
        "pre_close": "pre-close", "of": "of",
        "home_title": "WallBlock News: Wall Street, Asia & crypto market news",
        "home_desc_tail": "Free daily market news.",
        "cat_title": "{c} news", "cat_desc": "Latest {c} stories from WallBlock News, with sources. Not financial advice.",
        "contact_body": "Questions, corrections or feedback? Message us on Telegram. We read every note and fix errors quickly.",
        "contact_cta": "Open Telegram",
        "live": "Live markets", "live_title": "Live markets: charts, heat maps and calendar",
        "live_desc": "Live charts, stock and crypto heat maps, a bubble map and the economic calendar, all inside WallBlock News.",
        "live_sub": "Charts, heat maps and the economic calendar, without leaving WallBlock.",
        "live_teaser": "Bubble map, live charts, heat maps and the economic calendar in one place. Tap a bubble and see the price and chart right here.",
        "live_open": "Open live markets", "live_points": ["Bubble map: crypto, S&P 500, metals and indices", "Live TradingView charts", "Stock and crypto heat maps", "Live economic calendar"],
        "bubble_h": "Bubble map", "bubble_sub": "Green is up, red is down. Drag the bubbles and tap one for details.",
        "ds_crypto": "Crypto", "ds_stocks": "S&P 500", "ds_metals": "Metals & indices", "size": "Size", "size_move": "By move", "size_cap": "By market cap",
        "tf": "Change over", "hide_stable": "Hide stablecoins", "snapshot": "Snapshot", "live_src": "Live · CoinGecko", "price": "Price",
        "chg": "Change", "cap": "Market cap", "weight": "S&P 500 weight", "close": "Close", "data_table": "Data table",
        "bubble_alt": "Bubble heat map of price changes. The data table below has the same numbers.", "no_data": "No data yet.",
        "tv_h": "Live charts and heat maps", "tv_sub": "Interactive widgets by TradingView, shown inside this page.",
        "tv_consent": "This block loads a live widget from TradingView, which may set cookies. Nothing is loaded until you click.",
        "tv_load": "Load live widget", "tv_load_all": "Load all live widgets", "tv_forget": "Forget my choice", "tv_chart": "View live chart",
        "chart_h": "Interactive chart", "overview_h": "Market overview", "heat_stocks_h": "Stock heat map (S&P 500)", "heat_crypto_h": "Crypto heat map",
        "calendar_h": "Live economic calendar", "calendar_sub": "Updated by TradingView. Our curated calendar is on the Calendar page.",
        "attrib": "Charts, heat maps and calendar widgets by TradingView. Crypto prices by CoinGecko. Snapshot data from the latest WallBlock update.",
        "tf1h": "1h", "tf24": "24h", "tf7d": "7d", "jump": "On this page",
        "live_btn": "Use live prices (CoinGecko)", "live_note": "Loading live prices sends your IP address to CoinGecko.",
    },
    "es": {
        "skip": "Saltar al contenido", "main_nav": "Principal", "latest": "Última hora", "calendar": "Calendario", "videos": "Vídeos",
        "about": "Quiénes somos", "sections": "Secciones", "language": "Idioma", "home": "Inicio",
        "markets": "Mercados", "markets_sub": "Precios de la última actualización. Los niveles cambian; no es un servicio de cotizaciones.",
        "bb_title": "Dos miradas al mercado", "bb_sub": "Bullish y Bearish leen la misma pantalla. Esto es lo que más se movió en nuestra lista.",
        "bull": "Bullish", "bear": "Bearish", "bull_tag": "La visión alcista", "bear_tag": "La visión bajista",
        "risers": "Mayores subidas", "fallers": "Mayores caídas", "wallie_tag": "Tu guía del mercado",
        "wallie_cta": "Pregunta a Wallie en Telegram", "read_latest": "Leer las últimas noticias",
        "wallie_text": "Wallie es nuestra guía en las noticias del día. Bullish y Bearish muestran las dos caras de cada movimiento.",
        "stories": "Últimas noticias", "stories_sub": "Cada noticia enlaza sus fuentes. Resumimos; no damos consejos.",
        "all": "Todo", "sources": "Fuentes", "top_story": "Noticia principal", "updated": "Actualizado",
        "coming_up": "Próximamente", "coming_sub": "Datos, bancos centrales, resultados y festivos. Horas en hora del Este de EE. UU. (ET).",
        "full_calendar": "Calendario completo", "all_videos": "Todos los vídeos", "watch": "Ver",
        "videos_title": "Vídeos", "videos_sub": "Explicaciones breves e intros del equipo de WallBlock.",
        "videos_desc": "Vídeos breves de explicación del mercado, intros y aperturas de Wall Street del equipo de WallBlock News con Wallie, Bullish y Bearish.",
        "team_title": "Conoce al equipo", "team_sub": "Tres guías, un objetivo: que el mercado sea más fácil de leer.",
        "importance": {"high": "Impacto alto", "medium": "Impacto medio", "low": "Impacto bajo"},
        "footer_sections": "Secciones", "footer_info": "Información", "footer_follow": "Síguenos",
        "disclaimer_short": "Solo informativo. No es asesoramiento de inversión.",
        "contact": "Contacto", "privacy": "Privacidad", "terms": "Términos", "disclaimer": "Aviso legal",
        "no_stories": "Todavía no hay noticias en esta sección.", "back_home": "Volver a las últimas noticias",
        "cal_title": "Calendario económico", "cal_sub": "Datos de EE. UU., bancos centrales, resultados y festivos. Horas en hora del Este (ET).",
        "pre_close": "antes del cierre", "of": "de",
        "home_title": "WallBlock News: noticias de Wall Street, Asia y cripto",
        "home_desc_tail": "Noticias diarias del mercado, gratis.",
        "cat_title": "Noticias de {c}", "cat_desc": "Últimas noticias de {c} en WallBlock News, con sus fuentes. No es asesoramiento financiero.",
        "contact_body": "¿Dudas, correcciones o comentarios? Escríbenos por Telegram. Leemos todos los mensajes y corregimos los errores rápido.",
        "contact_cta": "Abrir Telegram",
        "live": "Mercados en vivo", "live_title": "Mercados en vivo: gráficos, mapas de calor y calendario",
        "live_desc": "Gráficos en vivo, mapas de calor de acciones y cripto, mapa de burbujas y calendario económico, todo dentro de WallBlock News.",
        "live_sub": "Gráficos, mapas de calor y calendario económico, sin salir de WallBlock.",
        "live_teaser": "Mapa de burbujas, gráficos en vivo, mapas de calor y calendario económico en un solo sitio. Toca una burbuja y ve el precio y el gráfico aquí mismo.",
        "live_open": "Abrir mercados en vivo", "live_points": ["Mapa de burbujas: cripto, S&P 500, metales e índices", "Gráficos de TradingView en vivo", "Mapas de calor de acciones y cripto", "Calendario económico en vivo"],
        "bubble_h": "Mapa de burbujas", "bubble_sub": "Verde sube, rojo baja. Arrastra las burbujas y toca una para ver detalles.",
        "ds_crypto": "Cripto", "ds_stocks": "S&P 500", "ds_metals": "Metales e índices", "size": "Tamaño", "size_move": "Por movimiento", "size_cap": "Por capitalización",
        "tf": "Variación en", "hide_stable": "Ocultar stablecoins", "snapshot": "Copia guardada", "live_src": "En vivo · CoinGecko", "price": "Precio",
        "chg": "Variación", "cap": "Capitalización", "weight": "Peso en el S&P 500", "close": "Cerrar", "data_table": "Tabla de datos",
        "bubble_alt": "Mapa de burbujas de variaciones de precio. La tabla de datos de abajo tiene los mismos números.", "no_data": "Todavía no hay datos.",
        "tv_h": "Gráficos y mapas de calor en vivo", "tv_sub": "Widgets interactivos de TradingView, mostrados dentro de esta página.",
        "tv_consent": "Este bloque carga un widget en vivo de TradingView, que puede instalar cookies. No se carga nada hasta que pulses.",
        "tv_load": "Cargar widget en vivo", "tv_load_all": "Cargar todos los widgets en vivo", "tv_forget": "Olvidar mi elección", "tv_chart": "Ver gráfico en vivo",
        "chart_h": "Gráfico interactivo", "overview_h": "Resumen de mercados", "heat_stocks_h": "Mapa de calor de acciones (S&P 500)", "heat_crypto_h": "Mapa de calor cripto",
        "calendar_h": "Calendario económico en vivo", "calendar_sub": "Actualizado por TradingView. Nuestro calendario seleccionado está en la página Calendario.",
        "attrib": "Gráficos, mapas de calor y calendario de TradingView. Precios cripto de CoinGecko. Datos guardados de la última actualización de WallBlock.",
        "tf1h": "1 h", "tf24": "24 h", "tf7d": "7 d", "jump": "En esta página",
        "live_btn": "Usar precios en vivo (CoinGecko)", "live_note": "Cargar precios en vivo envía tu dirección IP a CoinGecko.",
    },
}
MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
}
MONTHS_LONG = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
}
WEEKDAYS = {
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "es": ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"],
}

# category key, slug, icon, accent colour (checked for contrast in qa), labels
CATS = [
    ("Wall Street", "wall-street", "ic_ws.png", "#E3B341", {"en": "Wall Street", "es": "Wall Street"}),
    ("US Politics", "us-politics", "tb_politics.png", "#9DB8FF", {"en": "US Politics", "es": "Política de EE. UU."}),
    ("Asia", "asia", "tb_asia.png", "#FF9BAA", {"en": "Asia", "es": "Asia"}),
    ("Crypto", "crypto", "ic_crypto.png", "#F7A23B", {"en": "Crypto", "es": "Cripto"}),
    ("ETFs", "etfs", "tb_etfs.png", "#5ED8C3", {"en": "ETFs", "es": "ETF"}),
    ("Macro", "macro", "tb_macro.png", "#B5B4F5", {"en": "Macro", "es": "Macro"}),
    ("Commodities", "commodities", "cm_oro.png", "#E3BD83", {"en": "Commodities", "es": "Materias primas"}),
    ("Companies", "companies", "tb_companies.png", "#A5E6BC", {"en": "Companies", "es": "Empresas"}),
]
CAT = {c[0]: c for c in CATS}

STATIC_PAGES = ["about", "privacy", "terms", "disclaimer", "contact"]
VERTICAL = {"9d3e7ea5a34d48847fd84ae5339091e0", "e9a146e0e7fb29d63192df5d1072e3c0"}   # 9:16 videos
TITLE_FIX = {
    "wallblock_cpi_2026-11-10_EN (1)": {"en": "US CPI inflation · Nov 10", "es": "Inflación (IPC) de EE. UU. · 10 nov"},
    "Meet the team · Wallie, Bullish & Bearish": {"es": "Conoce al equipo · Wallie, Bullish y Bearish"},
    "Market open · Wed Nov 11 (chart lesson)": {"es": "Apertura del mercado · miércoles 11 nov (lección de gráficos)"},
    "WallBlock News intro · Breaking News": {"es": "Intro de WallBlock News · Última hora"},
    "Wall Street open · Bell + upbeat music": {"es": "Apertura de Wall Street · campana y música alegre"},
    "Wall Street open · Bell + breaking news": {"es": "Apertura de Wall Street · campana y última hora"},
    "Wall Street open · Trading floor": {"es": "Apertura de Wall Street · parqué"},
    "WallBlock News intro": {"es": "Intro de WallBlock News"},
    "WallBlock intro · Opening Bell": {"es": "Intro de WallBlock · campana de apertura"},
    "WallBlock intro · Market Pulse": {"es": "Intro de WallBlock · pulso del mercado"},
    "WallBlock intro · Calm Ticker": {"es": "Intro de WallBlock · ticker tranquilo"},
}
TELEGRAM = next((s["url"] for s in D["site"].get("socials", []) if "t.me" in s["url"]), "")
SIZES = {"wallie": (507, 400), "bullish": (308, 460), "bearish": (339, 460)}


# --------------------------------------------------------------------------- helpers
def tr(obj, key, lang):
    """Translated field with English fallback."""
    if lang != "en" and obj.get(f"{key}_{lang}"):
        return obj[f"{key}_{lang}"]
    return obj.get(key, "")


def out_rel(lang, slug):
    parts = ([lang] if lang != "en" else []) + ([slug] if slug else []) + ["index.html"]
    return "/".join(parts)


def link(frm, to):
    """Relative link between two pages (lang, slug)."""
    fdir = os.path.dirname(out_rel(*frm)) or "."
    r = os.path.relpath(out_rel(*to), fdir)
    if not PREVIEW:
        r = r[: -len("index.html")] or "./"
    return r


def asset(frm, path):
    fdir = os.path.dirname(out_rel(*frm)) or "."
    return os.path.relpath(path, fdir)


def canon(lang, slug):
    p = "/".join(([lang] if lang != "en" else []) + ([slug] if slug else []))
    return f"{SITE_URL}/{p}/" if p else f"{SITE_URL}/"


def parse_meta(meta):
    m = re.match(r"^([A-Z][a-z]{2}) (\d{1,2}), (\d{4}) · (.*)$", meta.strip())
    if not m:
        return None, meta
    mon = MONTHS["en"].index(m.group(1)) + 1
    return dt.date(int(m.group(3)), mon, int(m.group(2))), m.group(4)


def fmt_date(d, lang, weekday=False, year=True):
    day, mon = d.day, MONTHS[lang][d.month - 1]
    wd = f"{WEEKDAYS[lang][d.weekday()]}, " if weekday else ""
    if lang == "es":
        return f"{wd}{day} {mon}" + (f" {d.year}" if year else "")
    return f"{wd}{mon} {day}" + (f", {d.year}" if year else "")


def fmt_long(d, lang):
    if lang == "es":
        return f"{d.day} de {MONTHS_LONG['es'][d.month - 1]} de {d.year}"
    return f"{MONTHS_LONG['en'][d.month - 1]} {d.day}, {d.year}"


def loc_num(s, lang):
    """Convert 6,913.94 style numbers to Spanish 6.913,94."""
    s = s.replace("(pre-close)", f"({UI[lang]['pre_close']})")
    if lang != "es":
        return s
    def sw(m):
        return m.group(0).replace(",", "§").replace(".", ",").replace("§", ".")
    return re.sub(r"\d[\d,]*(?:\.\d+)?", sw, s)


NOTE_ES = [("Fri close", "cierre vie"), ("just above", "justo por encima de"), ("IPO price", "precio de salida a bolsa"), ("Sat 10:40 am ET", "sáb 10:40 ET"), ("spot, 5 pm ET", "spot, 17:00 ET"),
           ("Dec settle", "cierre dic"), ("Jan settle", "cierre ene"), ("(close)", "(cierre)"), ("early Wed", "a primera hora del mié"), ("early Thu", "a primera hora del jue"), ("Thu morning", "jue por la mañana"),
           ("Wed morning", "mié por la mañana"), ("Dec futures", "futuros dic"), ("futures", "futuros"), ("pre-close", "antes del cierre"),
           ("morning", "por la mañana"), ("early", "a primera hora"), ("Mon", "lun"), ("Tue", "mar"), ("Wed", "mié"), ("Thu", "jue"),
           ("Fri", "vie"), (" vs ", " frente a "), ("IPO", "salida a bolsa"), ("close", "cierre")]


def split_value(v, lang):
    """Split '6,913.94 (pre-close)' into the figure and its qualifier, localised."""
    m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", v.strip())
    main, note = (m.group(1), m.group(2)) if m else (v.strip(), "")
    if lang == "es":
        for a, b in NOTE_ES:
            main, note = main.replace(a, b), note.replace(a, b)
        main = loc_num(main, "es")
        note = loc_num(note, "es")
    if re.fullmatch(r"[+\-−]?\d+(\.\d+)?%", main):   # value column repeated the % change
        main = ""
    return main, note


def value_html(v, lang):
    main, note = split_value(v, lang)
    n = f' <small>({E(note)})</small>' if note else ""
    return (E(main) if main else "–") + n


def fmt_pct(p, lang):
    sign = "+" if p > 0 else ("−" if p < 0 else "")
    n = f"{abs(p):.2f}".rstrip("0").rstrip(".") if abs(p) != int(abs(p)) else f"{abs(p):.1f}"
    if lang == "es":
        n = n.replace(".", ",")
        return f"{sign}{n} %"
    return f"{sign}{n}%"


def pct_html(p, lang):
    cls = "up" if p > 0 else ("down" if p < 0 else "flat")
    arrow = "▲" if p > 0 else ("▼" if p < 0 else "■")
    return f'<span class="pct {cls}"><span aria-hidden="true">{arrow}</span> {fmt_pct(p, lang)}</span>'


def trim(s, n=155):
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:.–-")
    return cut + "…"


def paragraphs(text):
    return "".join(f"<p>{E(p)}</p>" for p in re.split(r"\n\s*\n", text.strip()) if p.strip())


# --------------------------------------------------------------------------- derived data
NEWS = D["news"]
for n in NEWS:
    n["_date"], n["_src"] = parse_meta(n["meta"])
LAST_UPDATE = max((n["_date"] for n in NEWS if n["_date"]), default=TODAY)
LEAD, FEED = NEWS[0], NEWS[1:]
INDEX = D["index"]
GROUP_ORDER = ["Indices", "Asia", "Commodities", "Crypto", "Forex", "Stocks"]
GROUP_LABEL = {
    "en": {"Indices": "US & Europe indices", "Asia": "Asia", "Commodities": "Commodities", "Crypto": "Crypto", "Forex": "Forex", "Stocks": "Stocks"},
    "es": {"Indices": "Índices EE. UU. y Europa", "Asia": "Asia", "Commodities": "Materias primas", "Crypto": "Cripto", "Forex": "Divisas", "Stocks": "Acciones"},
}
UPCOMING = [e for e in D["cal"] if dt.date.fromisoformat(e["date"]) >= TODAY]
STRIP = [n for n in ("S&P 500", "Nasdaq", "Dow Jones", "Bitcoin", "Gold", "WTI Oil") if any(i["name"] == n for i in INDEX)]


# --------------------------------------------------------------------------- page shell
CSS_NAME = JS_NAME = MK_JS_NAME = ""


def head(frm, title, desc, lang, slug, jsonld=None, og_type="website"):
    alts = "".join(
        f'<link rel="alternate" hreflang="{l}" href="{canon(l, slug)}">' for l in LANGS
    ) + f'<link rel="alternate" hreflang="x-default" href="{canon("en", slug)}">'
    og_img = f"{SITE_URL}/img/og.jpg"
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False, separators=(",", ":"))}</script>' if jsonld else ""
    fonts = "".join(
        f'<link rel="preload" href="{asset(frm, f)}" as="font" type="font/woff2" crossorigin>'
        for f in ("fonts/inter-latin-wght-normal.woff2", "fonts/poppins-latin-800-normal.woff2")
    )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#140813">
<meta name="color-scheme" content="dark">
<link rel="canonical" href="{canon(lang, slug)}">
{alts}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="WallBlock News">
<meta property="og:locale" content="{LOCALE[lang]}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon(lang, slug)}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{og_img}">
<link rel="icon" href="{asset(frm, 'favicon.ico')}" sizes="48x48">
<link rel="icon" href="{asset(frm, 'icon-192.png')}" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="{asset(frm, 'apple-touch-icon.png')}">
<link rel="manifest" href="{asset(frm, 'manifest.webmanifest')}">
{fonts}
<link rel="stylesheet" href="{asset(frm, CSS_NAME)}">
{ld}
</head>
"""


def header(frm, lang, slug):
    t = UI[lang]
    home = link(frm, (lang, ""))
    langs = "".join(
        f'<a href="{link(frm, (l, slug))}" lang="{l}" hreflang="{l}"'
        + (' aria-current="true"' if l == lang else "")
        + f'>{l.upper()}</a>'
        for l in LANGS
    )
    strip = "".join(
        '<li><span class="n">{n}</span> <span class="v">{v}</span> {p}</li>'.format(
            n=E(i["name"]), v=E(split_value(i["value"], lang)[0] or ""), p=pct_html(i["pct"], lang)
        )
        for name in STRIP for i in INDEX if i["name"] == name
    )
    nav_items = [(t["latest"], (lang, ""), "")] + [
        (c[4][lang], (lang, c[1]), c[1]) for c in CATS[:5]
    ] + [(t["live"], (lang, "markets"), "markets"), (t["calendar"], (lang, "calendar"), "calendar"), (t["videos"], (lang, "videos"), "videos")]
    nav = "".join(
        f'<li><a href="{link(frm, to)}"' + (' aria-current="page"' if s == slug else "") + f">{E(lbl)}</a></li>"
        for lbl, to, s in nav_items
    )
    return f"""<body>
<a class="skip" href="#main">{t['skip']}</a>
<header class="site-header">
  <ul class="strip" aria-hidden="true"><li class="strip-lbl">{fmt_date(LAST_UPDATE, lang, year=False)}</li>{strip}</ul>
  <div class="bar wrap">
    <a class="brand" href="{home}"><img src="{asset(frm, 'img/logo.png')}" width="40" height="40" alt=""><span class="brand-t">WallBlock <b>News</b></span></a>
    <nav class="lang" aria-label="{t['language']}">{langs}</nav>
  </div>
  <nav class="nav" aria-label="{t['main_nav']}"><ul class="wrap">{nav}</ul></nav>
</header>
<main id="main">
"""


def footer(frm, lang, extra_js=()):
    t = UI[lang]
    cats = "".join(f'<li><a href="{link(frm, (lang, c[1]))}">{E(c[4][lang])}</a></li>' for c in CATS) + f'<li><a href="{link(frm, (lang, "markets"))}">{E(t["live"])}</a></li>'
    info = "".join(
        f'<li><a href="{link(frm, (lang, s))}">{E(t[s])}</a></li>' for s in ("about", "privacy", "terms", "disclaimer", "contact")
    )
    tg = f'<li><a href="{E(TELEGRAM)}" rel="noopener noreferrer">Telegram</a></li>' if TELEGRAM else ""
    about = trim(tr(D["site"], "about", lang), 190)
    return f"""</main>
<footer class="site-footer">
  <div class="wrap grid">
    <div class="f-brand">
      <a class="brand" href="{link(frm, (lang, ''))}"><img src="{asset(frm, 'img/logo.png')}" width="40" height="40" alt=""><span class="brand-t">WallBlock <b>News</b></span></a>
      <p>{E(about)}</p>
    </div>
    <nav aria-label="{t['footer_sections']}"><h2>{t['footer_sections']}</h2><ul>{cats}</ul></nav>
    <nav aria-label="{t['footer_info']}"><h2>{t['footer_info']}</h2><ul>{info}</ul></nav>
    <nav aria-label="{t['footer_follow']}"><h2>{t['footer_follow']}</h2><ul>{tg}</ul></nav>
  </div>
  <div class="wrap legal"><p>{E(tr(D, 'footer', lang))}</p><p>© {TODAY.year} WallBlock News · {t['disclaimer_short']}</p></div>
</footer>
<script src="{asset(frm, JS_NAME)}" defer></script>{"".join(f'<script src="{asset(frm, j)}" defer></script>' for j in extra_js)}
</body>
</html>
"""


def webpage(lang, slug, title, desc, body, jsonld=None, crumbs=None, extra_js=()):
    frm = (lang, slug)
    ld = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": "WallBlock News", "url": canon(lang, ""), "inLanguage": lang},
        {"@context": "https://schema.org", "@type": "Organization", "name": "WallBlock News", "url": canon("en", ""),
         "logo": f"{SITE_URL}/icon-512.png", "sameAs": [TELEGRAM] if TELEGRAM else []},
    ] if not slug else []
    if crumbs:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]})
    if jsonld:
        ld.append(jsonld)
    return head(frm, title, desc, lang, slug, ld or None) + header(frm, lang, slug) + body + footer(frm, lang, extra_js)


# --------------------------------------------------------------------------- components
def story_card(frm, lang, n, level=3):
    c = CAT.get(n["cat"], CATS[0])
    t = UI[lang]
    d = n["_date"]
    time = f'<time datetime="{d.isoformat()}">{fmt_date(d, lang)}</time>' if d else ""
    src = f'<p class="src"><span>{t["sources"]}:</span> {E(n["_src"])}</p>' if n["_src"] else ""
    return f"""<article class="card story" data-cat="{E(n['cat'])}" style="--cc:{c[3]}">
  <header><a class="chip" href="{link(frm, (lang, c[1]))}"><img src="{asset(frm, 'img/' + c[2])}" width="20" height="20" alt="">{E(c[4][lang])}</a>{time}</header>
  <h{level}>{E(tr(n, 'title', lang))}</h{level}>
  <p>{E(tr(n, 'text', lang))}</p>
  {src}
</article>"""


def market_tables(frm, lang):
    t = UI[lang]
    out = []
    for g in GROUP_ORDER:
        rows = [i for i in INDEX if i["group"] == g]
        if not rows:
            continue
        body = "".join(
            f'<tr><th scope="row"><a href="{E(i["link"])}" rel="noopener noreferrer">{E(i["name"])}</a></th>'
            f'<td class="v">{value_html(i["value"], lang)}</td><td>{pct_html(i["pct"], lang)}</td></tr>'
            for i in rows
        )
        out.append(f'<div class="mkt-box"><table class="mkt"><caption>{E(GROUP_LABEL[lang][g])}</caption><tbody>{body}</tbody></table></div>')
    return "".join(out)


def movers(lang):
    ranked = sorted(INDEX, key=lambda i: i["pct"])
    return list(reversed(ranked[-3:])), ranked[:3]


def mover_list(items, lang):
    return "".join(
        f'<li><span class="n">{E(i["name"])}</span>{pct_html(i["pct"], lang)}</li>' for i in items
    )


def event_row(lang, e, compact=False):
    t = UI[lang]
    d = dt.date.fromisoformat(e["date"])
    imp = e.get("imp", "low")
    text = "" if compact else f'<p>{E(tr(e, "text", lang))}</p>'
    return f"""<li class="ev imp-{imp}">
  <time class="when" datetime="{e['date']}"><span class="d">{d.day}</span><span class="m">{MONTHS[lang][d.month - 1]}</span><span class="w">{WEEKDAYS[lang][d.weekday()]}</span></time>
  <div class="what"><h3>{E(tr(e, 'title', lang))}</h3>{text}<p class="tags"><span class="time">{E(e.get('time', ''))}</span><span class="imp"><i aria-hidden="true"></i>{t['importance'][imp]}</span></p></div>
</li>"""


def video_title(v, lang):
    return TITLE_FIX.get(v["title"], {}).get(lang) or v["title"]


def video_id(v):
    return v["url"].rsplit("/", 1)[-1]


def video_card(frm, lang, v, featured=False):
    vid = video_id(v)
    cls = "vert" if vid in VERTICAL else ""
    return f"""<figure class="video {cls}">
  <video controls preload="none" playsinline data-poster="{asset(frm, f'assets/{vid}.jpg')}"><source src="{asset(frm, f'assets/{vid}.mp4')}" type="video/mp4"></video>
  <figcaption>{E(video_title(v, lang))}</figcaption>
</figure>"""


# --------------------------------------------------------------------------- pages
def home(lang):
    frm = (lang, "")
    t = UI[lang]
    label = re.sub(r"^[^\w]+", "", tr(D["headline"], "label", lang))
    lede = tr(D["headline"], "text", lang)
    chips = f'<a class="chip on" href="#latest" data-filter="*" aria-current="true">{t["all"]}</a>' + "".join(
        f'<a class="chip" href="{link(frm, (lang, c[1]))}" data-filter="{E(c[0])}" style="--cc:{c[3]}"><img src="{asset(frm, "img/" + c[2])}" width="20" height="20" alt="">{E(c[4][lang])}</a>'
        for c in CATS
    )
    risers, fallers = movers(lang)
    ev = "".join(event_row(lang, e, compact=True) for e in UPCOMING[:6])
    vids = "".join(video_card(frm, lang, v) for v in D["videos"][:3])
    sz = SIZES
    body = f"""
<section class="hero wrap" aria-labelledby="h1">
  <div class="hero-copy">
    <p class="eyebrow"><span class="live" aria-hidden="true"></span>{E(label)} · {t['updated']} {fmt_date(LAST_UPDATE, lang)}</p>
    <h1 id="h1">{E(tr(LEAD, 'title', lang))}</h1>
    <p class="lede">{E(lede)}</p>
    <p class="cta"><a class="btn" href="#latest">{t['read_latest']}</a>{f'<a class="btn ghost" href="{E(TELEGRAM)}" rel="noopener noreferrer">{t["wallie_cta"]}</a>' if TELEGRAM else ''}</p>
  </div>
  <div class="stage" role="img" aria-label="Wallie, Bullish and Bearish">
    <img class="a bull" src="{asset(frm, 'img/bullish.webp')}" width="{sz['bullish'][0]}" height="{sz['bullish'][1]}" alt="">
    <img class="a bear" src="{asset(frm, 'img/bearish.webp')}" width="{sz['bearish'][0]}" height="{sz['bearish'][1]}" alt="">
    <img class="a wal" src="{asset(frm, 'img/wallie.webp')}" width="{sz['wallie'][0]}" height="{sz['wallie'][1]}" alt="" fetchpriority="high">
  </div>
</section>

<section class="wrap block" id="markets" aria-labelledby="mk-h">
  <div class="block-h"><h2 id="mk-h">{t['markets']}</h2><p>{t['markets_sub']}</p></div>
  <div class="mkt-grid">{market_tables(frm, lang)}</div>
</section>

<section class="wrap block" id="bulls-bears" aria-labelledby="bb-h">
  <div class="block-h"><h2 id="bb-h">{t['bb_title']}</h2><p>{t['bb_sub']}</p></div>
  <div class="bb">
    <article class="side bull-c"><img src="{asset(frm, 'img/bullish.webp')}" width="{sz['bullish'][0]}" height="{sz['bullish'][1]}" alt="" loading="lazy">
      <div><p class="tag">{t['bull_tag']}</p><h3>{t['bull']}</h3><h4>{t['risers']}</h4><ul>{mover_list(risers, lang)}</ul></div></article>
    <article class="side wal-c"><img src="{asset(frm, 'img/wallie.webp')}" width="{sz['wallie'][0]}" height="{sz['wallie'][1]}" alt="" loading="lazy">
      <div><p class="tag">{t['wallie_tag']}</p><h3>Wallie</h3><p>{t['wallie_text']}</p>{f'<a class="btn" href="{E(TELEGRAM)}" rel="noopener noreferrer">{t["wallie_cta"]}</a>' if TELEGRAM else ''}</div></article>
    <article class="side bear-c"><img src="{asset(frm, 'img/bearish.webp')}" width="{sz['bearish'][0]}" height="{sz['bearish'][1]}" alt="" loading="lazy">
      <div><p class="tag">{t['bear_tag']}</p><h3>{t['bear']}</h3><h4>{t['fallers']}</h4><ul>{mover_list(fallers, lang)}</ul></div></article>
  </div>
</section>

<section class="wrap block" id="latest" aria-labelledby="st-h">
  <div class="block-h"><h2 id="st-h">{t['stories']}</h2><p>{t['stories_sub']}</p></div>
  <div class="chips" role="group" aria-label="{t['sections']}">{chips}</div>
  <p class="sr" id="filter-status" role="status" aria-live="polite"></p>
  <div class="cards">{''.join(story_card(frm, lang, n) for n in FEED)}</div>
</section>

{live_teaser(frm, lang)}
<section class="wrap block" id="calendar" aria-labelledby="cal-h">
  <div class="block-h"><h2 id="cal-h">{t['coming_up']}</h2><p>{t['coming_sub']}</p></div>
  <ol class="events">{ev}</ol>
  <p class="more"><a class="btn ghost" href="{link(frm, (lang, 'calendar'))}">{t['full_calendar']}</a></p>
</section>

<section class="wrap block" id="videos" aria-labelledby="vd-h">
  <div class="block-h"><h2 id="vd-h">{t['videos_title']}</h2><p>{t['videos_sub']}</p></div>
  <div class="videos">{vids}</div>
  <p class="more"><a class="btn ghost" href="{link(frm, (lang, 'videos'))}">{t['all_videos']}</a></p>
</section>
"""
    return webpage(
        lang, "", t["home_title"], trim(lede, 150 - len(t["home_desc_tail"])) + " " + t["home_desc_tail"], body
    )


def category(lang, c):
    frm = (lang, c[1])
    t = UI[lang]
    items = [n for n in NEWS if n["cat"] == c[0]]
    label = c[4][lang]
    cards = "".join(story_card(frm, lang, n, 2) for n in items) or f"<p>{t['no_stories']}</p>"
    body = f"""
<section class="wrap page" aria-labelledby="h1">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{link(frm, (lang, ''))}">{t['home']}</a> <span aria-hidden="true">/</span> <span>{E(label)}</span></nav>
  <h1 id="h1"><img src="{asset(frm, 'img/' + c[2])}" width="44" height="44" alt="">{E(label)}</h1>
  <p class="lede">{t['stories_sub']}</p>
  <div class="cards">{cards}</div>
  <p class="more"><a class="btn ghost" href="{link(frm, (lang, ''))}">{t['back_home']}</a></p>
</section>"""
    return webpage(
        lang, c[1], t["cat_title"].format(c=label) + " · WallBlock News", t["cat_desc"].format(c=label), body,
        crumbs=[(t["home"], canon(lang, "")), (label, canon(lang, c[1]))],
    )


def calendar_page(lang):
    frm = (lang, "calendar")
    t = UI[lang]
    groups = {}
    for e in D["cal"]:
        d = dt.date.fromisoformat(e["date"])
        groups.setdefault((d.year, d.month), []).append(e)
    secs = ""
    for (y, m), evs in sorted(groups.items()):
        secs += f'<section aria-labelledby="m{y}{m}"><h2 id="m{y}{m}" class="month">{MONTHS_LONG[lang][m - 1].capitalize()} {y}</h2><ol class="events">{"".join(event_row(lang, e) for e in evs)}</ol></section>'
    body = f"""
<section class="wrap page" aria-labelledby="h1">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{link(frm, (lang, ''))}">{t['home']}</a> <span aria-hidden="true">/</span> <span>{t['calendar']}</span></nav>
  <h1 id="h1">{t['cal_title']}</h1>
  <p class="lede">{t['cal_sub']}</p>
  {secs}
</section>"""
    return webpage(lang, "calendar", t["cal_title"] + " · WallBlock News", t["cal_sub"], body,
                   crumbs=[(t["home"], canon(lang, "")), (t["calendar"], canon(lang, "calendar"))])


def videos_page(lang):
    frm = (lang, "videos")
    t = UI[lang]
    vids = "".join(video_card(frm, lang, v) for v in D["videos"])
    body = f"""
<section class="wrap page" aria-labelledby="h1">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{link(frm, (lang, ''))}">{t['home']}</a> <span aria-hidden="true">/</span> <span>{t['videos']}</span></nav>
  <h1 id="h1">{t['videos_title']}</h1>
  <p class="lede">{t['videos_sub']}</p>
  <div class="videos">{vids}</div>
</section>"""
    return webpage(lang, "videos", t["videos_title"] + " · WallBlock News", t["videos_desc"], body,
                   crumbs=[(t["home"], canon(lang, "")), (t["videos"], canon(lang, "videos"))])


def text_page(lang, slug):
    frm = (lang, slug)
    t = UI[lang]
    title = t[slug]
    if slug == "contact":
        content = f"<p>{t['contact_body']}</p>" + (f'<p class="cta"><a class="btn" href="{E(TELEGRAM)}" rel="noopener noreferrer">{t["contact_cta"]}</a></p>' if TELEGRAM else "")
        desc = t["contact_body"]
    else:
        raw = tr(D["site"], slug, lang)
        content = paragraphs(raw)
        desc = trim(raw, 150)
    body = f"""
<section class="wrap page prose" aria-labelledby="h1">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{link(frm, (lang, ''))}">{t['home']}</a> <span aria-hidden="true">/</span> <span>{E(title)}</span></nav>
  <h1 id="h1">{E(title)}</h1>
  {content}
</section>"""
    return webpage(lang, slug, f"{title} · WallBlock News", desc, body,
                   crumbs=[(t["home"], canon(lang, "")), (title, canon(lang, slug))])



# --------------------------------------------------------------------------- live markets
import math

STABLE = {"USDT", "USDC", "DAI", "FDUSD", "USDE", "PYUSD", "TUSD", "USDS", "USDD", "USD1", "RLUSD", "GUSD", "USDP", "FRAX", "LUSD", "EURC", "BUIDL", "USDG"}
RGB = {"up": (127, 221, 163), "down": (255, 144, 136), "flat": (176, 195, 180)}
TV_SYMBOL = {"GOLD": "COMEX:GC1!", "SILVER": "COMEX:SI1!", "PLATINUM": "NYMEX:PL1!", "PALLADIUM": "NYMEX:PA1!",
             "S&P 500": "SP:SPX", "NASDAQ 100": "NASDAQ:NDX", "DOW": "DJ:DJI"}


def pack_bubbles(coins, W=1000, H=560, n=40):
    """Deterministic circle packing for the static preview (no JS needed)."""
    coins = [c for c in coins if c.get("s") not in STABLE][:n]
    ws = [(abs(c.get("d1") or 0) + .35) ** .85 for c in coins]
    tot = sum(ws) or 1
    area = W * H * .5
    items = sorted(({"c": c, "r": max(math.sqrt(area * w / tot / math.pi), 15)} for c, w in zip(coins, ws)), key=lambda i: -i["r"])
    placed = []
    for it in items:
        r = it["r"]
        while True:
            ang = rad = 0.0
            ok = False
            while rad < W:
                x = W / 2 + rad * math.cos(ang) * 1.7
                y = H / 2 + rad * math.sin(ang)
                if r <= x <= W - r and r <= y <= H - r and all((x - q["x"]) ** 2 + (y - q["y"]) ** 2 >= (r + q["r"] + 3) ** 2 for q in placed):
                    ok = True
                    break
                ang += .3
                rad += .55
            if ok:
                break
            r *= .92
        it.update(x=x, y=y, r=r)
        placed.append(it)
    return placed


def bubble_svg(lang, label):
    coins = D["bubbles"]["coins"]
    out = []
    for it in pack_bubbles(coins):
        c, d = it["c"], it["c"].get("d1") or 0
        kind = "up" if d > .05 else ("down" if d < -.05 else "flat")
        k = min(abs(d) / 8, 1)
        r, g, b = RGB[kind]
        fill = f"rgba({r},{g},{b},{.16 + .26 * k:.2f})"
        txt = ""
        if it["r"] > 20:
            fs = max(9, min(it["r"] * .42, 26))
            txt = (f'<text x="{it["x"]:.1f}" y="{it["y"] - fs * .25:.1f}" font-size="{fs:.1f}" font-weight="700">{E(c["s"][:6])}</text>'
                   f'<text x="{it["x"]:.1f}" y="{it["y"] + fs * .85:.1f}" font-size="{fs * .6:.1f}" font-weight="600">{E(fmt_pct(d, lang))}</text>')
        out.append(f'<g><circle cx="{it["x"]:.1f}" cy="{it["y"]:.1f}" r="{it["r"]:.1f}" fill="{fill}" stroke="rgb({r},{g},{b})" stroke-width="2"/>{txt}</g>')
    return (f'<svg class="bsvg" viewBox="0 0 1000 560" role="img" aria-label="{E(label)}" preserveAspectRatio="xMidYMid meet">'
            + "".join(out) + "</svg>")


def tv_cfg(lang, kind):
    loc = "es" if lang == "es" else "en"
    if kind == "advanced-chart":
        return {"autosize": True, "symbol": "BITSTAMP:BTCUSD", "interval": "D", "timezone": "Etc/UTC", "theme": "dark", "style": "1",
                "locale": loc, "backgroundColor": "#140813", "gridColor": "rgba(176,195,180,0.10)", "allow_symbol_change": True,
                "hide_side_toolbar": False, "calendar": False, "support_host": "https://www.tradingview.com"}
    if kind == "market-overview":
        def grp(title, syms):
            return {"title": title, "symbols": [{"s": a, "d": b} for a, b in syms], "originalTitle": title}
        L = {"en": ("Indices", "Futures", "Commodities", "Crypto", "Forex"), "es": ("Índices", "Futuros", "Materias primas", "Cripto", "Divisas")}[loc]
        return {"colorTheme": "dark", "dateRange": "1D", "showChart": True, "locale": loc, "isTransparent": True, "showSymbolLogo": True,
                "showFloatingTooltip": False, "width": "100%", "height": "100%", "plotLineColorGrowing": "rgba(127,221,163,1)",
                "plotLineColorFalling": "rgba(255,144,136,1)", "gridLineColor": "rgba(176,195,180,0.1)", "scaleFontColor": "rgba(224,228,205,1)",
                "belowLineFillColorGrowing": "rgba(127,221,163,0.12)", "belowLineFillColorFalling": "rgba(255,144,136,0.12)",
                "belowLineFillColorGrowingBottom": "rgba(127,221,163,0)", "belowLineFillColorFallingBottom": "rgba(255,144,136,0)",
                "symbolActiveColor": "rgba(224,228,205,0.12)", "tabs": [
                    grp(L[0], [("FOREXCOM:SPXUSD", "S&P 500"), ("FOREXCOM:NSXUSD", "Nasdaq 100"), ("FOREXCOM:DJI", "Dow 30"), ("INDEX:NKY", "Nikkei 225"), ("INDEX:DEU40", "DAX"), ("FOREXCOM:UKXGBP", "FTSE 100")]),
                    grp(L[1], [("CME_MINI:ES1!", "S&P 500"), ("CME:6E1!", "Euro"), ("COMEX:GC1!", "Gold"), ("NYMEX:CL1!", "WTI Crude"), ("NYMEX:NG1!", "Gas"), ("CBOT:ZC1!", "Corn")]),
                    grp(L[2], [("COMEX:GC1!", "Gold"), ("COMEX:SI1!", "Silver"), ("NYMEX:PL1!", "Platinum"), ("NYMEX:CL1!", "WTI"), ("NYMEX:NG1!", "Gas"), ("COMEX:HG1!", "Copper")]),
                    grp(L[3], [("BITSTAMP:BTCUSD", "Bitcoin"), ("BITSTAMP:ETHUSD", "Ethereum"), ("COINBASE:SOLUSD", "Solana"), ("BINANCE:XRPUSDT", "XRP"), ("BINANCE:BNBUSDT", "BNB")]),
                    grp(L[4], [("FX:EURUSD", "EUR/USD"), ("FX:GBPUSD", "GBP/USD"), ("FX:USDJPY", "USD/JPY"), ("FX:USDCNH", "USD/CNH"), ("CAPITALCOM:DXY", "DXY")])]}
    if kind == "stock-heatmap":
        return {"exchanges": [], "dataSource": "SPX500", "grouping": "sector", "blockSize": "market_cap_basic", "blockColor": "change", "locale": loc,
                "symbolUrl": "", "colorTheme": "dark", "hasTopBar": True, "isDataSetEnabled": True, "isZoomEnabled": True, "hasSymbolTooltip": True,
                "isMonoSize": False, "width": "100%", "height": "100%"}
    if kind == "crypto-coins-heatmap":
        return {"dataSource": "Crypto", "blockSize": "market_cap_calc", "blockColor": "change", "locale": loc, "symbolUrl": "", "colorTheme": "dark",
                "hasTopBar": True, "isDataSetEnabled": True, "isZoomEnabled": True, "hasSymbolTooltip": True, "isMonoSize": False, "width": "100%", "height": "100%"}
    if kind == "events":
        return {"colorTheme": "dark", "isTransparent": True, "locale": loc, "countryFilter": "us,eu,gb,jp,cn,es,de,fr", "importanceFilter": "0,1",
                "width": "100%", "height": "100%"}
    raise KeyError(kind)


def tv_block(lang, bid, title, kind, height, sub=""):
    t = UI[lang]
    cfg = json.dumps(tv_cfg(lang, kind), ensure_ascii=False, separators=(",", ":"))
    sub_html = f'<p class="tv-sub">{E(sub)}</p>' if sub else ""
    return f"""<section class="tv-card" id="{bid}" aria-labelledby="{bid}-h">
  <div class="tv-head"><h3 id="{bid}-h">{E(title)}</h3>{sub_html}</div>
  <div class="tv-box" data-tv="{kind}" data-cfg='{E(cfg)}' style="--h:{height}px">
    <div class="tv-gate"><p>{t['tv_consent']}</p><button type="button" class="btn ghost" data-tv-load>{t['tv_load']}</button></div>
  </div>
</section>"""


def bubble_payload(lang):
    t = UI[lang]
    def one(key, extra_note=False):
        b = D[key]
        coins = []
        for c in b["coins"]:
            row = {"s": tr(c, "s", lang), "n": tr(c, "n", lang)}
            for k in ("r", "p", "mc", "w", "h1", "d1", "w1"):
                if c.get(k) is not None:
                    row[k] = c[k]
            note = tr(c, "note", lang)
            if note:
                row["note"] = note
            raw = c["s"]
            row["tv"] = TV_SYMBOL.get(raw, "")
            coins.append(row)
        return {"asof": tr(b, "asof", lang), "source": b.get("source", ""), "period": tr(b, "period", lang), "coins": coins}
    keys = ("snapshot", "live_src", "price", "chg", "cap", "weight", "close", "tf_h1", "tf_d1", "tf_w1", "tv_chart", "no_data", "tv_consent", "tv_load")
    labels = {k: t.get(k, "") for k in ("snapshot", "live_src", "price", "chg", "cap", "weight", "close", "tv_chart", "no_data", "tv_consent", "tv_load", "ds_crypto", "ds_stocks", "ds_metals")}
    labels.update({"h1": t["tf1h"], "d1": t["tf24"], "w1": t["tf7d"]})
    return {"lang": lang, "locale": "es-ES" if lang == "es" else "en-US", "t": labels, "stable": sorted(STABLE),
            "ds": {"crypto": one("bubbles"), "stocks": one("stocks"), "metals": one("metals")}}


def data_tables(lang):
    t = UI[lang]
    out = []
    for key, label in (("bubbles", t["ds_crypto"]), ("stocks", t["ds_stocks"]), ("metals", t["ds_metals"])):
        b = D[key]
        rows = ""
        for c in b["coins"]:
            price = "–" if c.get("p") is None else (f"${c['p']:,.2f}" if c["p"] >= 1 else f"${c['p']:.4g}")
            if lang == "es":
                price = price.replace(",", "§").replace(".", ",").replace("§", ".")
            d = c.get("d1")
            rows += f'<tr><th scope="row">{E(tr(c, "n", lang))} <span>{E(tr(c, "s", lang))}</span></th><td>{price}</td><td>{pct_html(d, lang) if d is not None else "–"}</td></tr>'
        out.append(f'<details class="dt"><summary>{E(label)} · {t["data_table"]}</summary><p class="asof">{E(t["snapshot"])}: {E(tr(b, "asof", lang))} · {E(b.get("source", ""))}</p>'
                   f'<table class="mkt"><thead><tr><th scope="col">{E(label)}</th><th scope="col">{t["price"]}</th><th scope="col">{t["chg"]}</th></tr></thead><tbody>{rows}</tbody></table></details>')
    return "".join(out)


def markets_page(lang):
    frm = (lang, "markets")
    t = UI[lang]
    payload = json.dumps(bubble_payload(lang), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    jump = "".join(f'<li><a href="#{a}">{E(l)}</a></li>' for a, l in (("bubbles", t["bubble_h"]), ("chart", t["chart_h"]), ("overview", t["overview_h"]),
                                                                       ("heat-stocks", t["heat_stocks_h"]), ("heat-crypto", t["heat_crypto_h"]), ("calendar-live", t["calendar_h"])))
    body = f"""
<section class="wrap page" aria-labelledby="h1">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{link(frm, (lang, ''))}">{t['home']}</a> <span aria-hidden="true">/</span> <span>{t['live']}</span></nav>
  <h1 id="h1">{t['live']}</h1>
  <p class="lede">{t['live_sub']}</p>
  <nav class="jump" aria-label="{t['jump']}"><ul>{jump}</ul></nav>
</section>

<section class="wrap block" id="bubbles" aria-labelledby="bb-h" data-bubbles>
  <div class="block-h"><h2 id="bb-h">{t['bubble_h']}</h2><p>{t['bubble_sub']}</p></div>
  <div class="bctl">
    <div class="seg" role="group" aria-label="{t['bubble_h']}" data-seg="ds"><button type="button" data-v="crypto" aria-pressed="true">{t['ds_crypto']}</button><button type="button" data-v="stocks" aria-pressed="false">{t['ds_stocks']}</button><button type="button" data-v="metals" aria-pressed="false">{t['ds_metals']}</button></div>
    <div class="seg" role="group" aria-label="{t['tf']}" data-seg="tf"><button type="button" data-v="h1" aria-pressed="false">{t['tf1h']}</button><button type="button" data-v="d1" aria-pressed="true">{t['tf24']}</button><button type="button" data-v="w1" aria-pressed="false">{t['tf7d']}</button></div>
    <div class="seg" role="group" aria-label="{t['size']}" data-seg="sz"><button type="button" data-v="move" aria-pressed="true">{t['size_move']}</button><button type="button" data-v="cap" aria-pressed="false">{t['size_cap']}</button></div>
    <label class="chk"><input type="checkbox" data-hide-stable checked> {t['hide_stable']}</label>
  </div>
  <div class="bstage" data-stage>
    <canvas role="img" aria-label="{E(t['bubble_alt'])}"></canvas>
    <aside class="binfo" data-info hidden></aside>
    <noscript><div class="bsvg-wrap">{bubble_svg(lang, t['bubble_alt'])}</div></noscript>
  </div>
  <p class="bsrc"><span class="bdot" data-dot aria-hidden="true"></span><span data-src></span> <button type="button" class="btn ghost" data-live-btn aria-pressed="false" title="{E(t['live_note'])}">{t['live_btn']}</button></p>
  <p class="bnote">{t['live_note']}</p>
  <script type="application/json" id="bubble-data">{payload}</script>
  {data_tables(lang)}
</section>

<section class="wrap block" aria-labelledby="tv-h">
  <div class="block-h"><h2 id="tv-h">{t['tv_h']}</h2><p>{t['tv_sub']}</p>
    <p class="tv-actions"><button type="button" class="btn" data-tv-all>{t['tv_load_all']}</button> <button type="button" class="btn ghost" data-tv-forget hidden>{t['tv_forget']}</button></p></div>
  <div class="tv-grid">
    {tv_block(lang, 'chart', t['chart_h'], 'advanced-chart', 620)}
    {tv_block(lang, 'overview', t['overview_h'], 'market-overview', 560)}
    {tv_block(lang, 'heat-stocks', t['heat_stocks_h'], 'stock-heatmap', 600)}
    {tv_block(lang, 'heat-crypto', t['heat_crypto_h'], 'crypto-coins-heatmap', 600)}
    {tv_block(lang, 'calendar-live', t['calendar_h'], 'events', 640, t['calendar_sub'])}
  </div>
  <p class="attrib">{t['attrib']}</p>
</section>"""
    return webpage(lang, "markets", t["live_title"], t["live_desc"], body,
                   crumbs=[(t["home"], canon(lang, "")), (t["live"], canon(lang, "markets"))], extra_js=(MK_JS_NAME,))


def live_teaser(frm, lang):
    t = UI[lang]
    pts = "".join(f"<li>{E(x)}</li>" for x in t["live_points"])
    return f"""
<section class="wrap block" id="live" aria-labelledby="lv-h">
  <div class="live-card">
    <div class="live-copy"><h2 id="lv-h">{t['live']}</h2><p>{t['live_teaser']}</p><ul class="ticks">{pts}</ul>
      <p class="cta"><a class="btn" href="{link(frm, (lang, 'markets'))}">{t['live_open']}</a></p></div>
    <div class="live-art">{bubble_svg(lang, t['bubble_alt'])}</div>
  </div>
</section>
"""


# --------------------------------------------------------------------------- output
def write(rel, content):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


CSP = ("default-src 'self'; script-src 'self' https://s3.tradingview.com; style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data: https://*.tradingview.com; media-src 'self'; font-src 'self' data:; "
       "connect-src 'self' https://api.coingecko.com https://*.tradingview.com; "
       "frame-src https://*.tradingview-widget.com https://*.tradingview.com; object-src 'none'; base-uri 'self'; "
       "form-action 'self'; frame-ancestors 'self'")
SEC = {"X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin",
       "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()", "Content-Security-Policy": CSP}


def write_deploy_files():
    hdr = "/*\n" + "".join(f"  {k}: {v}\n" for k, v in SEC.items())
    hdr += "\n/css/*\n  Cache-Control: public, max-age=31536000, immutable\n/js/*\n  Cache-Control: public, max-age=31536000, immutable\n"
    hdr += "/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n/img/*\n  Cache-Control: public, max-age=604800\n/assets/*\n  Cache-Control: public, max-age=604800\n"
    write("_headers", hdr)
    htaccess = f"""# WallBlock News · Apache (Hostinger). Upload this file together with the site.
Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html

<IfModule mod_rewrite.c>
  RewriteEngine On
  # Force HTTPS (Hostinger also offers this switch in hPanel > Security > SSL)
  RewriteCond %{{HTTPS}} off
  RewriteRule ^ https://%{{HTTP_HOST}}%{{REQUEST_URI}} [L,R=301]
</IfModule>

<IfModule mod_headers.c>
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"
  Header always set Content-Security-Policy "{CSP}"
  <FilesMatch "\\.(css|js|woff2)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  <FilesMatch "\\.(png|jpe?g|webp|mp4|ico)$">
    Header set Cache-Control "public, max-age=604800"
  </FilesMatch>
  <FilesMatch "\\.(html|json|xml|txt|webmanifest)$">
    Header set Cache-Control "no-cache"
  </FilesMatch>
</IfModule>

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json application/xml image/svg+xml
</IfModule>

<IfModule mod_mime.c>
  AddType video/mp4 .mp4
  AddType application/manifest+json .webmanifest
  AddType font/woff2 .woff2
</IfModule>
"""
    write(".htaccess", htaccess)


def main():
    global CSS_NAME, JS_NAME, MK_JS_NAME
    if OUT != STATIC:
        if OUT.exists():
            shutil.rmtree(OUT)
        shutil.copytree(STATIC, OUT, ignore=shutil.ignore_patterns("*.html", "css", "js", "sitemap.xml", "robots.txt", "_headers", ".htaccess"))
    for old in list((OUT).glob("css/*")) + list(OUT.glob("js/*")):
        old.unlink()
    for kind, ext in (("site.css", "css"), ("site.js", "js"), ("markets.js", "js")):
        data = (SRC / kind).read_bytes()
        stem = kind.rsplit(".", 1)[0]
        name = f"{ext}/{stem}.{hashlib.md5(data).hexdigest()[:10]}.{ext}"
        (OUT / ext).mkdir(exist_ok=True)
        (OUT / name).write_bytes(data)
        if kind == "site.css":
            CSS_NAME = name
        elif kind == "site.js":
            JS_NAME = name
        else:
            MK_JS_NAME = name

    pages = []
    for lang in LANGS:
        write(out_rel(lang, ""), home(lang)); pages.append((lang, ""))
        for c in CATS:
            write(out_rel(lang, c[1]), category(lang, c)); pages.append((lang, c[1]))
        write(out_rel(lang, "calendar"), calendar_page(lang)); pages.append((lang, "calendar"))
        write(out_rel(lang, "videos"), videos_page(lang)); pages.append((lang, "videos"))
        write(out_rel(lang, "markets"), markets_page(lang)); pages.append((lang, "markets"))
        for s in STATIC_PAGES:
            write(out_rel(lang, s), text_page(lang, s)); pages.append((lang, s))

    # sitemap with hreflang alternates
    slugs = sorted({s for _, s in pages}, key=lambda s: (s != "", s))
    urls = []
    for s in slugs:
        for lang in LANGS:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{canon(l, s)}"/>' for l in LANGS)
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{canon("en", s)}"/>'
            urls.append(f"<url><loc>{canon(lang, s)}</loc><lastmod>{LAST_UPDATE.isoformat()}</lastmod>{alts}</url>")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")
    write_deploy_files()
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    write("manifest.webmanifest", json.dumps({
        "name": "WallBlock News", "short_name": "WallBlock", "description": "Wall Street, Asia & crypto market news",
        "start_url": "./", "scope": "./", "display": "standalone", "background_color": "#140813", "theme_color": "#140813",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
    }, indent=1))
    # 404 sits at the site root, so it can use root-relative links (it is served from any depth)
    h404 = head(("en", ""), "Page not found · WallBlock News", "Page not found", "en", "404")
    h404 = re.sub(r'<link rel="(canonical|alternate)"[^>]*>', "", h404)
    h404 = h404.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)
    h404 = re.sub(r'(href|src)="(css|js|fonts|img)/', r'\1="/\2/', h404)
    write("404.html", h404 + '<body><main id="main" class="wrap page"><h1>Page not found</h1><p class="lede">That page does not exist.</p><p class="cta"><a class="btn" href="/">Back to WallBlock News</a></p></main></body></html>')
    print(f"built {len(pages)} pages -> {OUT}  ({'preview' if PREVIEW else 'production'} links, {SITE_URL})")


if __name__ == "__main__":
    main()
