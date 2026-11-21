# Datos en vivo sin salir de tu web

| Qué | Cómo está hecho | Estado |
|---|---|---|
| Mapa de burbujas (cripto, S&P 500, metales e índices) | Propio, en canvas (`src/markets.js`). Usa la instantánea de `content.json`; con un clic se actualizan los precios cripto desde la API pública de CoinGecko. Al tocar una burbuja se ve el detalle **dentro** de la página, con gráfico de TradingView opcional. Tabla de datos accesible debajo. | Probado con datos simulados |
| Gráfico interactivo, resumen de mercados, mapas de calor de acciones (S&P 500) y de cripto, calendario económico | Widgets gratuitos de TradingView, incrustados con consentimiento (nada se carga hasta que el visitante pulsa). Configuración en `tv_cfg()` de `src/build.py`. | **Falta probar en un despliegue real**: el entorno de desarrollo no puede llegar a `tradingview.com` |
| Noticias, índices, calendario curado, vídeos | `src/content.json` (ronda de noticias) | Actualizado con el cierre del viernes 20 nov |

## Por qué se pide un clic

Los widgets de TradingView y la API de CoinGecko cargan recursos de terceros, que reciben la IP del visitante y pueden instalar cookies. En la UE eso exige consentimiento previo. Además, así la portada pesa menos y pasa mejor Lighthouse.

## Finviz

Finviz no ofrece un widget gratuito incrustable: su mapa (`finviz.com/map.ashx`) está pensado para verse en su web, y copiar sus datos incumple sus condiciones. Alternativas que sí se pueden hacer:
- **Mapa de calor del S&P 500 de TradingView** (ya incluido): mismo concepto, incrustable.
- **Mapa de burbujas propio** con nuestros datos (ya incluido).
- Finviz Elite tiene exportación de datos para uso personal; revisa sus condiciones antes de mostrarlos públicamente.

## CoinGlass (liquidaciones)

CoinGlass no ofrece widget gratuito; sus gráficos de liquidaciones no se pueden incrustar y su API es de pago. Opciones:
1. **API de pago de CoinGlass** + gráfico propio (coste mensual; la clave debe ir en un servidor o función, nunca en el navegador).
2. **Flujo público de liquidaciones de Binance Futures** (`!forceOrder@arr` por WebSocket): gratis, en tiempo real, pero solo de Binance, sin histórico y no accesible desde algunas regiones. Se podría hacer un contador "liquidaciones en vivo".
3. Mientras tanto, las cifras de liquidaciones salen en las noticias con su fuente.

## Actualizar a mano cada día

1. Ronda de noticias → `src/content.json` (ver `docs/PROMPT-PERFECCIONAR.md`).
2. `python3 src/build.py`
3. Subir `public/` (ver `docs/DEPLOY.md`).
