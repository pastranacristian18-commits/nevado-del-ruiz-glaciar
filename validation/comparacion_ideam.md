# Comparación con el IDEAM — área glaciar del Nevado del Ruiz

Fecha: 2026-11-26 · Script: `python/comparacion_ideam.py` · Datos: `data/processed/serie_ideam_ruiz.csv`, `data/processed/comparacion_ideam_mapbiomas.csv` · Figuras: `reports/figuras/comparacion_ideam.png` (ES), `reports/figuras/ideam_comparison_en.png` (EN)

## Fuentes oficiales leídas (PDF originales)
- **IDEAM — Informe del estado de los glaciares colombianos 2023**, Tabla 17 ("Evolución del área de los seis actuales glaciares colombianos en los últimos 170 años"): serie del Ruiz desde mediados del siglo XIX hasta 2022.
- **IDEAM — Informe del estado de los glaciares colombianos 2024**, Tabla 1 y texto: "El área glaciar del Nevado del Ruiz, estimada para el 20 de febrero de 2024, fue de 7,17 ± 0,30 km²". Imagen base: PlanetScope (20-feb-2024); DEM SRTM 30.
- En el mismo informe 2024, el IDEAM reporta que **"aproximadamente el 88 % de la superficie glaciar del Nevado del Ruiz estuvo cubierta por ceniza volcánica"**, que una capa de más de 5 cm actúa como aislante térmico, y que los mayores retrocesos ocurrieron en el sector sur (menos ceniza).
- Informes anteriores del IDEAM describen el mismo fenómeno: el glaciar del Ruiz cubierto por ceniza (imagen PlanetScope de noviembre de 2021) y nieve estacional que excede al glaciar durante La Niña.

Los PDF se guardaron en `data/raw/referencias/ideam/` (no versionados en GitHub por su tamaño).

## Resultados

| Año | IDEAM (km²) | MapBiomas (km²) | IDEAM / MapBiomas | Este estudio, hielo limpio (km²) |
|---|---:|---:|---:|---:|
| década 1980 | 18,7 | 14,73 (1985) | 1,27 | — |
| década 1990 | 14,1 | 10,65 (1995) | 1,32 | — |
| 2003 | — | 9,61 | — | 10,71 |
| 2010 | 10,3 | 9,36 | 1,10 | — |
| 2017 | 8,88 | 7,12 | 1,25 | 6,36 |
| 2020 | 8,14 | 6,32 | 1,29 | — |
| 2022 | 7,68 | 5,19 | 1,48 | — |
| 2024 | 7,17 ± 0,30 | 3,68 | **1,95** | 4,35 (ago) |

## Lectura
1. **Las tres fuentes coinciden en la tendencia:** el Ruiz pierde glaciar de forma sostenida.
2. **La magnitud depende de cómo se mide.** El IDEAM (fotointerpretación en alta resolución, que incluye hielo cubierto de ceniza) siempre da más área que MapBiomas y que nuestros contornos (clasificación espectral del hielo visible).
3. **La diferencia crece justo cuando aumenta la ceniza.** Hasta 2021 el IDEAM reporta 1,1–1,3 veces el área de MapBiomas; en 2022 sube a 1,48 y en 2024 a 1,95, el año en que el IDEAM estima ~88 % del glaciar cubierto de ceniza. Es la confirmación independiente y oficial del hallazgo central de este proyecto: **los métodos espectrales miden hielo visible, no la extensión del glaciar, y la ceniza amplía esa brecha.**
4. **Hielo oculto en 2024:** IDEAM 7,17 km² frente a 4,35 km² de hielo limpio visible en nuestra escena de agosto de 2024 → ~2,8 km² de glaciar no visible espectralmente (~39 %). Es coherente con la estimación previa de este proyecto (~3 km² ocultos por ceniza en una fecha dada), aunque las fechas y métodos no son idénticos.
5. **No todo es ceniza.** En las décadas de 1980 y 1990 (antes de la cubierta de ceniza actual) la relación ya era 1,27–1,32: también influyen la resolución (3 m frente a 30 m), la definición de glaciar, las fechas de las imágenes y la nieve.

## Implicaciones para las afirmaciones del proyecto

| Afirmación anterior | Ajuste tras la comparación |
|---|---|
| "El Ruiz perdió ~75 % de su glaciar en 40 años" | Cierto **según MapBiomas** (1985–2024). Según el **IDEAM** la pérdida es de **~62 %** (18,7 km² en la década de 1980 → 7,17 km² en 2024). El valor de MapBiomas está inflado en los últimos años por la ceniza. |
| "No se puede afirmar que MapBiomas esté equivocado en 2023" | Con la cifra oficial de 2024 (7,17 km²) y el 88 % de cobertura de ceniza reportado por el IDEAM, **es razonable afirmar que MapBiomas subestima la extensión glaciar en 2022–2024** porque no detecta el hielo cubierto. |
| "La ceniza oculta el glaciar" | **Confirmado por el IDEAM** (fuente oficial independiente). |

## Limitaciones
- Las cifras de las décadas de 1980 y 1990 del IDEAM son valores por década (se grafican en 1985 y 1995).
- El IDEAM no publica en estos informes sus contornos digitales, así que la comparación es de áreas, no de polígonos.
- Nuestra escena de agosto de 2024 está en temporada húmeda; parte del "hielo limpio" puede ser nieve fresca sobre ceniza.
