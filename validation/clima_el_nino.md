# Glaciar del Ruiz vs clima y El Niño — resultados exploratorios

Fecha: 2026-11-25 · Script: `python/analisis_clima_glaciar.py` · Datos: `gee/06_clima_mensual.js`, NOAA CPC ONI · Figura: `reports/figuras/glaciar_clima_el_nino.png` · Salida completa: `validation/resultados_clima.txt`

## Resultados

| Variable | Tendencia (Sen, por década) | IC95 % | Mann-Kendall p | Lectura |
|---|---|---|---|---|
| Temperatura 2 m (ERA5-Land, celda ~9 km, cota media 4283 m) | +0,10 °C | +0,04 a +0,18 | 0,005 | Calentamiento significativo |
| Isoterma 0 °C estimada (gradiente 6,5 °C/km) | +16 m | +6 a +28 | 0,005 | ~+70 m en 45 años (estimación) |
| Nevada ERA5-Land | −1,5 mm | −3,3 a −0,4 | 0,011 | Casi nula desde 2019 |
| Precipitación CHIRPS | +42 mm | −10 a +103 | 0,11 | Sin tendencia significativa |
| Área glaciar MapBiomas | −2,15 km² | −2,45 a −1,84 | < 0,001 | Pérdida monótona (−75 % 1985–2024) |

**El Niño y el clima local (Spearman, n = 45):** ONI vs temperatura ρ = +0,54 (p < 0,001); ONI vs precipitación CHIRPS ρ = −0,53 (p < 0,001); ONI vs nevada ρ = −0,33 (p = 0,03). → **En el Ruiz, El Niño = más cálido, más seco y con menos nieve.** Resultado robusto y coherente con la literatura sobre Colombia.

**El Niño y la pérdida de hielo (n = 39):** ΔA vs ONI ρ = −0,30 (p = 0,06); ΔA vs temperatura ρ = −0,28 (p = 0,08). Pérdida mediana en años El Niño −0,25 km²/año vs −0,12 km²/año en el resto (Mann-Whitney p = 0,10). → **Sugestivo, no significativo.** No se puede afirmar con estos datos que El Niño acelere la pérdida.

## Por qué la señal glaciar es débil (y no hay que forzarla)
1. MapBiomas aplica filtros temporales: el ΔA anual está suavizado y desplazado.
2. Las caídas grandes de MapBiomas (1990→91: −1,96 km²; 2013→14; 2021→23) coinciden con **actividad volcánica** (posterior a 1985; 2012; 2023), lo que mezcla pérdida real con ceniza (ver `auditoria_mapbiomas_v1.md`).
3. n ≈ 40 y autocorrelación → los p-valores son optimistas.
4. ERA5-Land a ~9 km no representa la cumbre; se usan anomalías.

## Afirmaciones publicables
- ✅ El Ruiz perdió ~75 % de su superficie glaciar entre 1985 y 2024 según MapBiomas; nuestras escenas limpias confirman la tendencia (10,7 km² en 2003 → ~4,4 km² en 2024–2026).
- ✅ La temperatura de la región subió ~0,1 °C por década y la nevada en el reanálisis casi desapareció.
- ✅ El Niño hace al Ruiz más cálido y seco.
- ⚠️ La relación directa El Niño → pérdida de hielo es sugestiva (p ≈ 0,06–0,10), no demostrada.
- ❌ No afirmar que la isoterma subió "X m medidos": es una estimación por gradiente.
