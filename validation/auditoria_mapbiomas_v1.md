# Auditoría v1 — Contornos semiautomáticos vs MapBiomas Col. 3 (Nevado del Ruiz)

Fecha: 2026-11-25 · Método: `python/delinear_semiauto.py` (NDSI > 0,40, verde > 0,10, > 4400 m, radio 6 km, tamiz 5 px) sobre escenas seleccionadas visualmente. Rango = umbrales NDSI 0,50–0,30. Revisión visual preliminar (pendiente revisión del autor). Figura: `reports/figuras/control_contornos_hoja.png`.

| Fecha | Sensor | Área NDSI (km²) | Rango (km²) | MapBiomas mismo año (km²) | Diferencia | Confianza | Observación |
|---|---|---:|---|---:|---:|---|---|
| 1987-01-14 | L5 | 10,75 | 10,23–11,18 | 14,49 | −26 % | media | Ceniza post-1985 no detectada: subestima |
| 1997-10-24 | L5 | 7,27 | 6,72–7,77 | 10,54 | — | descartar | Escena cortada |
| 2001-01-12 | L7 | 14,53 | 14,11–14,92 | 10,01 | +45 % | baja | Nieve fresca |
| 2002-10-14 | L7 | 12,40 | 12,08–12,77 | 9,76 | +27 % | media | Posible nieve fresca |
| 2003-01-02 | L7 | 10,71 | 10,43–11,01 | 9,59 | +12 % | **alta** | — |
| 2017-12-18 | L8 | 6,36 | 6,19–6,53 | 7,10 | −10 % | **alta** | Referencia |
| 2021-12-13 | L8 | 7,75 | 6,93–8,45 | 6,22 | +25 % | baja | Nieve fresca al norte |
| 2023-06-18 | L9 | 7,81 | 7,49–8,03 | 3,76 | +108 % | media | Temporada húmeda |
| 2024-08-15 | L8 | 4,35 | 4,15–4,58 | 3,67 | +18 % | **alta** | — |
| 2026-05-09 | L9 | 5,83 | 5,44–6,08 | — | — | baja | Nieve fresca |
| 2026-07-28 | L9 | 4,50 | 4,28–4,80 | — | — | **alta** | — |

(MapBiomas recalculado dentro del mismo radio de 6 km; difiere levemente de la serie del área completa.)

## Lectura preliminar (no concluyente)
1. **Escenas de confianza alta** (2003, 2017, 2024, 2026-07): diferencias con MapBiomas entre −10 % y +18 %. Acuerdo razonable para un glaciar pequeño a 30 m.
2. **El sesgo depende de la superficie**, no del método: ceniza → subestima (1987); nieve fresca → sobreestima (2001, 2021, 2026-05). La incertidumbre real del área del Ruiz en una fecha dada es mucho mayor que el error de píxel.
3. **2023 es el caso clave:** MapBiomas cae a 3,76 km² (−27 % vs 2022); nuestra escena de junio de 2023 da 7,81 km², pero en temporada húmeda (posible nieve fresca). Hipótesis a probar: la caída de MapBiomas en 2023 refleja en parte **hielo cubierto de ceniza** (período de actividad volcánica) y no solo pérdida de hielo. Requiere: escena limpia de temporada seca 2023 sin ceniza (no existe en la galería), Sentinel-2 (10 m, más fechas) o datos IDEAM de campo.
4. Tendencia robusta pese a todo: con solo escenas de confianza alta, 10,7 km² (2003) → 6,4 (2017) → 4,4 (2024) → 4,5 (2026). Pérdida ≈ 59 % en 21 años.

## Actualización — Sentinel-2 + Cloud Score+ (script 05)
359 días con imagen 2017–2026; 25 con ≥ 90 % de la zona glaciar despejada (`data/processed/serie_s2_hielo_limpio_ruiz.csv`). Figura: `reports/figuras/s2_periodo_critico.png`.

1. **Validación cruzada entre sensores (mismo día):** 2024-08-15 S2 4,245 vs Landsat 8 4,350 km² (−2,4 %); 2026-07-28 S2 4,323 vs L9 4,501 (−4,0 %); 2026-05-09 S2 5,628 vs L9 5,826 (−3,4 %). El método es consistente entre sensores; la incertidumbre dominante no es el sensor sino la superficie.
2. **El "hielo limpio" no es el glaciar.** Temporada seca: 3,1–3,7 km² (2020) → 1,5 (ene-2023) → 0,9–1,1 (ene-2024) → 0,5 (ene-2025). Pero en ago-2024 y jul/ago-2026 vuelve a 3,0–4,3 km². Un glaciar no pierde 85 % y lo recupera en 6 meses.
3. **Evidencia visual (color verdadero + falso color):** en ene-2023 y ene-2024 el glaciar está casi totalmente **cubierto de ceniza** (gris en color verdadero; azul-verdoso opaco en falso color, forma del glaciar intacta). En oct-2022 se ve una nevada generalizada (41,8 km², no es glaciar) y nieve fresca con depósito de ceniza. En el cráter aparece un píxel rojo en SWIR (probable anomalía térmica del volcán; no verificado).
4. **Implicación para MapBiomas 2023 (3,77 km²):** su valor es cercano al nuestro en ago-2024 (4,2–4,35 km²), así que **no podemos afirmar que MapBiomas esté equivocado**. Sí podemos afirmar que cualquier método basado en NDSI de temporada seca en el Ruiz mide **hielo visible**, no **extensión glaciar**, y que la ceniza puede ocultar hasta ~3 km² de hielo en una fecha.

## Pregunta científica resultante (para la fase ML)
¿Se puede estimar la extensión glaciar **incluyendo hielo bajo ceniza** con variables espectrales (NDSI débil, NIR, SWIR), textura y topografía? Baseline: NDSI > 0,40. Referencia: contornos de escenas sin ceniza ni nieve fresca cercanas en el tiempo. Validación: dejar-una-fecha-fuera y dejar-un-glaciar-fuera.

## Próximos pasos
- Revisión del autor en QGIS (editar 2021 y 2023, confirmar confianza).
- Densificar 2017–2026 con Sentinel-2 (10 m) para resolver 2023.
- Contrastar con cifras IDEAM leídas en el PDF original.
