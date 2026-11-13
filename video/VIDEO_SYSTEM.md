# Sistema de vídeos de WallBlock News

Documento de referencia para no empezar de cero cada vez. Escrito el 13 nov 2026 después de rehacer el vídeo
de apertura tres veces por no tener esto guardado.

## 1. Reglas fijas (de la skill `wallblock-news` de Emilio)

- **Solo los avatares oficiales nuevos:** Wallie (robot blanco y dorado), Bullish (toro robot blindado verde) y
  Bearish (oso robot blindado rojo). Nunca el Wallie antiguo con el logo de la NYSE.
- **Nombres sin traducir** en todos los idiomas: Wallie, Bullish, Bearish, WallBlock News. En español **nunca**
  «toro» ni «oso»: siempre «Bullish» y «Bearish».
- **Siempre dos idiomas:** español **y** inglés (`_ES` / `_EN`), salvo que Emilio pida uno solo.
- Horas como «hora europea» / «European time» (y ET si ayuda).
- **Informar, nunca aconsejar.** Sin cifras inventadas: si no hay dato fiable, se deja fuera.
- Formato de números: español `7.405,2` y `−0,82 %`; inglés `7,405.2` y `−0.82%`.
- Sin calavera. Sin Nvidia mientras Emilio no diga lo contrario (petición del 13 nov).
- Menos de 1 minuto para redes sociales; vertical 1080×1920.

## 2. Formato diario (lo que Emilio ya tiene hecho)

Referencia: `assets/e9a146e0e7fb29d63192df5d1072e3c0.mp4` (apertura del mié 11 nov, 56 s, 1080×1920, en inglés).
Contactos en `video/ref/formato_diario_11nov_contactos.png`.

Es un **diálogo de los tres avatares en bocadillos**, no una voz en off:

| Elemento | Qué es |
|---|---|
| Etiqueta arriba a la derecha | quién habla: `NEUTRAL · WALLIE`, `BULLISH` (verde), `BEARISH` (rojo) |
| Wallie (abajo izq.) | guía neutral: abre («Hi! I'm Wallie. Today we learn to read 4 market charts») y cierra («Follow WallBlock News so you don't miss a thing!») |
| Bullish | la visión alcista de cada dato, bocadillo verde |
| Bearish | la visión bajista de cada dato, bocadillo rojo |
| Pantallas | «Wall Street Open» → «How the market opens» (S&P, Nasdaq, Dow) → 4 gráficos de TradingView con recuadro **LESSON** (CoreWeave, S&P 500, Brent, Bitcoin) → «This week» (calendario) |
| Pie | `WALLBLOCK NEWS` · «Not financial advice» |

**Esa pista de audio está vacía** (−91 dB): el vídeo del 11 nov y el de presentación del equipo
(`cb31f64a…mp4`) no llevan voz. Los diálogos son solo texto en bocadillos.

## 3. Voces: lo que se sabe y lo que NO

- La **única locución real de los avatares** está en `assets/wallblock-intro-es.mp4` (24,7 s, español, subtítulos).
  Contactos en `video/ref/intro_es_contactos.png`. Textos:
  - Wallie: «Hola, soy Wallie, tu guía en WallBlock News.»
  - Bullish: «Soy Bullish. Te enseño las oportunidades del mercado.»
  - Bearish: «Y yo soy Bearish. Te aviso de los riesgos.»
  - Los tres: «Breaking News, Wall Street, cripto, materias primas y vídeos. Cada día, claro y al momento.»
- Esa locución es de **banda ancha (≈16,6 kHz)**: voz de IA de un servicio externo. **No consta en ningún sitio con qué
  herramienta se hizo** (ni en la skill, ni en el repo, ni en las sesiones). Desde el contenedor no se puede
  reproducir: Hugging Face, Google y Bing están bloqueados por la red del entorno, y Emilio rechazó ampliar permisos.
- **PENDIENTE:** que Emilio diga con qué herramienta hizo las voces (o que suba los audios de cada avatar). Mientras
  tanto, el montaje del vídeo se puede hacer completo y la voz se mezcla después (ver §5).
- Motores que sí hay en el contenedor: `espeak-ng` + MBROLA (es1, us2…) y SVOX Pico (`libttspico-utils`, es-ES y
  en-US). Son voces básicas; **Emilio las rechazó** el 13 nov («entrecortada, no se entiende»). No usarlas como
  «la voz de los avatares».

## 4. Qué NO repetir (error del 13 nov)

Se hizo un vídeo con **una sola voz en off sintética y sin bocadillos**: no es el formato, ni son las voces.
Antes de producir un vídeo hay que partir de §2 y §3, y enseñar a Emilio el guion **por avatar** para que lo apruebe.

## 5. Guion por avatar (plantilla)

Cada línea lleva su avatar. Wallie abre y cierra; Bullish y Bearish dan su visión de cada dato (siempre como
información, sin recomendar comprar ni vender). Escenas del 13 nov, aprovechables como base:
hook cripto → Wall Street → Asia → petróleo → Fed 9 dic → cierre.

## 6. Herramientas (carpeta `video/tools/`)

Render de escenas HTML → vídeo (Playwright + ffmpeg), tiempos a partir de la duración de cada frase, subtítulos
palabra a palabra, mezcla de audio con ducking y loudnorm en dos pasadas.

```
python3 gen_voice.py            # voz (motor básico) por segmento; escribe durations.json y speech.json
python3 build_cfg.py            # calendario de escenas -> cfg_es.json / cfg_en.json
python3 mix2.py es|en           # mezcla de audio
NODE_PATH=$(npm root -g) node render.js cfg_es.json silent_es.mp4     # imagen
ffmpeg -i silent_es.mp4 -i audio_es.m4a -c copy -movflags +faststart salida_ES.mp4
```

Las escenas (`scene.html`) hoy son el vídeo de voz en off del 13 nov. Para el formato diario correcto hay que
rehacerlas con bocadillos por avatar (§2).
