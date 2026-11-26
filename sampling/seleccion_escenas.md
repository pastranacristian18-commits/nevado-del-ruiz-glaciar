# Selección visual de escenas Landsat — Nevado del Ruiz

Fuente: galería del script `gee/03_mapbiomas_y_galeria.js` (40 candidatas con anillo 4200–4700 m ≥ 60 % despejado, criterio independiente de Fmask).
Hoja de contactos: `reports/figuras/hoja_contactos_candidatas.png` · miniaturas: `data/raw/referencias/miniaturas/`.
Composición SWIR1-NIR-Verde: hielo/nieve limpia = cian brillante; hielo con ceniza = gris-azulado opaco; nube = blanco.
Revisión: 2026-11-25 (primera pasada; pendiente confirmación del autor).

## Hallazgo principal
En casi todas las escenas de **temporada seca (dic–ene) desde 2014** el glaciar aparece **cubierto de ceniza** (gris-azulado opaco), y el NDSI lo subestima o no lo detecta: 2014-12-26, 2020-01-09, 2023-12-03, 2024-01-04, 2025-01-14, 2025-01-22. En temporada húmeda, la **nieve fresca** tapa la ceniza y el área se infla: 2015-09-24, 2016-07-08, 2023-09-06.
→ Explica en buena parte las series imposibles de los scripts 01–02. Ninguna serie automática con NDSI es confiable en el Ruiz sin tratar ceniza y nieve fresca.

## Clasificación de escenas

| Categoría | Escenas (fecha · path/row) | Uso |
|---|---|---|
| **A — Hielo limpio, sin nieve fresca evidente** | 2001-01-12 (009057), 2002-10-14 (009057), 2003-01-02 (009057), 2017-12-18 (009056/057), 2021-12-13 (009056/057), 2023-06-18 (009056/057), 2024-08-15 (009056/057), 2026-05-09 (009056/057) | Digitalización manual del contorno (referencia independiente) |
| **A* — Útil con salvedad** | 1987-01-14 (009057, parte del glaciar con ceniza post-erupción 1985), 1997-10-24 (009056, recorte por borde de escena), 2026-07-28 (nubes al oeste) | Digitalizar marcando la incertidumbre |
| **B — Nieve fresca (sobreestima)** | 2001-01-28 (nube sobre el glaciar), 2015-09-24, 2016-07-08, 2023-09-06 | Solo para análisis de variabilidad estacional |
| **C — Ceniza (subestima con NDSI)** | 2014-12-26, 2020-01-09, 2022-01-30 (bruma), 2023-01-25, 2023-12-03, 2024-01-04, 2025-01-14, 2025-01-22 | Caso de prueba para el modelo ML (¿detecta hielo bajo ceniza?) |
| Descartadas | 1987-01-14 (009056) y 2003-01-02 (009056): borde de escena | — |

## Vacíos temporales
Sin candidatas: 1988–1996 y 2004–2013 (escasez de Landsat 5 sobre Colombia y falla SLC de Landsat 7 desde 2003, excluida a propósito). Opciones: incluir Landsat 7 SLC-off con relleno, ASTER, o Sentinel-2 (2017+) para densificar.
