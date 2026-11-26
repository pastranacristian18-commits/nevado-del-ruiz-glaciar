"""
ANTARES Geospatial Lab · Proyecto #1 Nevados
Comparación del área glaciar del Ruiz: IDEAM (oficial) vs MapBiomas Col. 3 vs este estudio.

Fuentes IDEAM (leídas en los PDF originales, ver data/processed/serie_ideam_ruiz.csv):
  - Informe del estado de los glaciares colombianos 2023, Tabla 17 (serie 1980s–2022).
  - Informe del estado de los glaciares colombianos 2024, Tabla 1 y texto (2024: 7,17 ± 0,30 km²,
    PlanetScope 20-feb-2024; ~88 % del glaciar cubierto por ceniza).
Ejecutar (ANTARES_LANG=en para la versión en inglés):
  "C:\\Program Files\\QGIS 4.0.2\\bin\\python-qgis.bat" python\\comparacion_ideam.py
"""
import os
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[1]
P, FIG = R / "data" / "processed", R / "reports" / "figuras"
EN = os.environ.get("ANTARES_LANG") == "en"
T = lambda es, en: en if EN else es

ideam = pd.read_csv(P / "serie_ideam_ruiz.csv")
mb = pd.read_csv(P / "serie_mapbiomas_c3_ruiz.csv")
propios = pd.DataFrame({"t": [2003.0, 2017.96, 2024.62, 2026.57], "a": [10.71, 6.36, 4.35, 4.50],
                        "lo": [10.43, 6.19, 4.15, 4.28], "hi": [11.01, 6.53, 4.58, 4.80]})

# Tabla comparativa en años comunes
comp = ideam.merge(mb, on="anio", how="left")
comp["dif_mapbiomas_km2"] = comp["area_km2_ideam"] - comp["area_km2_mapbiomas"]
comp["ratio_ideam_mapbiomas"] = comp["area_km2_ideam"] / comp["area_km2_mapbiomas"]
comp.to_csv(P / "comparacion_ideam_mapbiomas.csv", index=False, float_format="%.3f")
print(comp[["anio", "area_km2_ideam", "area_km2_mapbiomas", "dif_mapbiomas_km2", "ratio_ideam_mapbiomas"]].to_string(index=False))

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, (a0, a1) = plt.subplots(2, 1, figsize=(8, 7.5), dpi=180, sharex=True, gridspec_kw={"height_ratios": [2.2, 1]})
a0.plot(ideam["anio"], ideam["area_km2_ideam"], "-o", color="#1b7837", ms=4,
        label=T("IDEAM (oficial; PlanetScope/alta resolución, incluye hielo con ceniza)",
                "IDEAM (official; PlanetScope/high resolution, includes ash-covered ice)"))
a0.errorbar([2024], [7.17], yerr=[[0.30], [0.30]], fmt="none", ecolor="#1b7837", capsize=3)
a0.plot(mb["anio"], mb["area_km2_mapbiomas"], "-", color="#2c7fb8", lw=1.6,
        label=T("MapBiomas Col. 3 (Landsat, clasificación automática)", "MapBiomas Col. 3 (Landsat, automatic classification)"))
a0.errorbar(propios["t"], propios["a"], yerr=[propios["a"] - propios["lo"], propios["hi"] - propios["a"]],
            fmt="s", color="#d95f0e", ms=5, capsize=3,
            label=T("Este estudio: hielo limpio visible (NDSI, escenas limpias)", "This study: visible clean ice (NDSI, clean scenes)"))
a0.annotate(T("~88 % del glaciar\ncubierto de ceniza\n(IDEAM, 2024)", "~88 % of the glacier\ncovered by ash\n(IDEAM, 2024)"),
            xy=(2024, 5.7), xytext=(2008.5, 4.2), fontsize=8, color="#7f2704",
            arrowprops=dict(arrowstyle="->", color="#7f2704", lw=0.8))
a0.annotate("", xy=(2024.3, 4.4), xytext=(2024.3, 7.0), arrowprops=dict(arrowstyle="<->", color="#7f2704", lw=1))
a0.set_ylabel(T("Área glaciar (km²)", "Glacier area (km²)"))
a0.set_title(T("Nevado del Ruiz: tres formas de medir el mismo glaciar", "Nevado del Ruiz: three ways to measure the same glacier"),
             loc="left", fontweight="bold")
a0.legend(frameon=False, fontsize=7.5, loc="upper right")
a0.set_ylim(0, 20)

c = comp.dropna(subset=["area_km2_mapbiomas"])
a1.bar(c["anio"], c["ratio_ideam_mapbiomas"], color="#7f2704", width=0.8)
a1.axhline(1, color="k", lw=0.6)
for x, y in [(x, y) for x, y in zip(c["anio"], c["ratio_ideam_mapbiomas"]) if x in (1985, 1995, 2010, 2017, 2020, 2022, 2024)]:
    a1.text(x, y + 0.03, f"{y:.2f}", ha="center", fontsize=7)
a1.set_ylabel(T("IDEAM / MapBiomas", "IDEAM / MapBiomas"))
a1.set_xlabel(T("Año", "Year"))
a1.set_ylim(0, 2.3)
fig.text(0.01, 0.01, T("Fuentes: IDEAM, Informes del estado de los glaciares colombianos 2023 (Tabla 17) y 2024 (Tabla 1);\n"
                       "MapBiomas Colombia Col. 3; Landsat/Sentinel-2. Décadas de 1980 y 1990 graficadas en 1985 y 1995.",
                       "Sources: IDEAM, State of Colombian Glaciers reports 2023 (Table 17) and 2024 (Table 1);\n"
                       "MapBiomas Colombia Col. 3; Landsat/Sentinel-2. 1980s and 1990s values plotted at 1985 and 1995."),
         fontsize=6.3, color="#555")
fig.tight_layout(rect=(0, 0.05, 1, 1))
out = FIG / ("ideam_comparison_en.png" if EN else "comparacion_ideam.png")
fig.savefig(out); plt.close(fig)
print("Figura:", out)
