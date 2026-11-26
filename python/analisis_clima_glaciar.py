"""
ANTARES Geospatial Lab · Proyecto #1 Nevados
Glaciar del Ruiz vs clima y El Niño (1981–2025) — análisis EXPLORATORIO.

Entradas (data/processed y data/raw):
  serie_mapbiomas_c3_ruiz.csv        área glaciar anual MapBiomas Col. 3
  clima_anual_ruiz_1981_2025.csv     ERA5-Land (T2m, precip, nevada) + CHIRPS (script gee/06)
  raw/clima/oni_noaa_cpc.txt         Oceanic Niño Index (NOAA CPC)
  raw/dem/copernicus_dem_glo30.tif   para la cota media de la celda ERA5-Land
Salidas:
  reports/figuras/glaciar_clima_el_nino.png
  data/processed/tabla_glaciar_clima_anual.csv
  validation/resultados_clima.txt

Cautelas (se reportan junto a los resultados):
  - n ≈ 40 años; series autocorrelacionadas → p-valores optimistas.
  - MapBiomas aplica filtros temporales: ΔA anual está suavizado.
  - ERA5-Land a ~9 km: se usan anomalías y tendencias, no valores de cumbre.
  - La precipitación de ERA5-Land en esta celda (~6000–9900 mm/año) es
    poco realista frente a CHIRPS (~1300–2500); se usa CHIRPS para lluvia.
  - Correlación ≠ causalidad.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from osgeo import gdal, osr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[1]
P, RAW = R / "data" / "processed", R / "data" / "raw"
FIG = R / "reports" / "figuras"
GRAD = 0.0065  # °C/m

# ---------------- Datos ----------------
mb = pd.read_csv(P / "serie_mapbiomas_c3_ruiz.csv")
cl = pd.read_csv(P / "clima_anual_ruiz_1981_2025.csv")
oni = pd.read_csv(RAW / "clima" / "oni_noaa_cpc.txt", sep=r"\s+")
oni_a = oni.groupby("YR")["ANOM"].agg(["mean", "max", "count"]).reset_index()
oni_a = oni_a[oni_a["count"] == 12].rename(columns={"YR": "anio", "mean": "oni", "max": "oni_max"})

# Cota media de la celda ERA5-Land (0,1°) que contiene la cumbre: lon -75.35..-75.25, lat 4.85..4.95
ds = gdal.Open(str(RAW / "dem" / "copernicus_dem_glo30.tif"))
z = ds.GetRasterBand(1).ReadAsArray().astype(float)
gt = ds.GetGeoTransform()
xs = gt[0] + (np.arange(ds.RasterXSize) + 0.5) * gt[1]
ys = gt[3] + (np.arange(ds.RasterYSize) + 0.5) * gt[5]
X, Y = np.meshgrid(xs, ys)
s_utm = osr.SpatialReference(); s_utm.ImportFromEPSG(32618)
s_geo = osr.SpatialReference(); s_geo.ImportFromEPSG(4326)
for s in (s_utm, s_geo):
    s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
ct = osr.CoordinateTransformation(s_utm, s_geo)
ll = np.array(ct.TransformPoints(np.c_[X.ravel(), Y.ravel()]))
lon, lat = ll[:, 0].reshape(X.shape), ll[:, 1].reshape(X.shape)
celda = (lon >= -75.35) & (lon < -75.25) & (lat >= 4.85) & (lat < 4.95)
z_celda = float(z[celda].mean())

df = cl.merge(oni_a[["anio", "oni", "oni_max"]], on="anio", how="left").merge(mb, on="anio", how="left")
df["isoterma0_m"] = z_celda + df["t2m_c"] / GRAD
df["dA_km2"] = df["area_km2_mapbiomas"].diff()
df["oni_prev"] = df["oni"].shift(1)
df["t2m_anom"] = df["t2m_c"] - df["t2m_c"].mean()
df["chirps_anom_pct"] = 100 * (df["precip_chirps_mm"] / df["precip_chirps_mm"].mean() - 1)
df.to_csv(P / "tabla_glaciar_clima_anual.csv", index=False, float_format="%.4f")

# ---------------- Estadística ----------------
lineas = [f"Cota media celda ERA5-Land (Copernicus DEM): {z_celda:.0f} m  (píxeles: {celda.sum()})", ""]


def tendencia(col, d=df):
    s = d[["anio", col]].dropna()
    tau, p = stats.kendalltau(s["anio"], s[col])
    sen = stats.theilslopes(s[col], s["anio"])
    return f"{col:22s} Sen = {sen.slope*10:+.3f} /década  (IC95 {sen.low_slope*10:+.3f} a {sen.high_slope*10:+.3f})  MK tau={tau:+.2f} p={p:.3f}  n={len(s)}"


lineas.append("TENDENCIAS (Mann-Kendall + pendiente de Sen)")
for c in ["t2m_c", "isoterma0_m", "precip_chirps_mm", "nevada_era5_mm", "area_km2_mapbiomas"]:
    lineas.append("  " + tendencia(c))

lineas += ["", "CORRELACIONES con ΔA (cambio anual de área MapBiomas, km²) — Spearman"]
for c in ["oni", "oni_prev", "t2m_c", "precip_chirps_mm", "nevada_era5_mm"]:
    s = df[["dA_km2", c]].dropna()
    rho, p = stats.spearmanr(s["dA_km2"], s[c])
    lineas.append(f"  ΔA vs {c:18s} rho={rho:+.2f}  p={p:.3f}  n={len(s)}")

lineas += ["", "CORRELACIONES clima local vs ONI — Spearman"]
for c in ["t2m_c", "precip_chirps_mm", "nevada_era5_mm"]:
    s = df[["oni", c]].dropna()
    rho, p = stats.spearmanr(s["oni"], s[c])
    lineas.append(f"  ONI vs {c:18s} rho={rho:+.2f}  p={p:.3f}  n={len(s)}")

nino = df["oni"] >= 0.5
nina = df["oni"] <= -0.5
s = df.dropna(subset=["dA_km2"])
a, b = s.loc[nino, "dA_km2"], s.loc[~nino, "dA_km2"]
u, pu = stats.mannwhitneyu(a, b, alternative="less")
lineas += ["", "AÑOS EL NIÑO (ONI anual ≥ 0,5) vs resto",
           f"  ΔA mediana El Niño = {a.median():+.3f} km² (n={len(a)}) | resto = {b.median():+.3f} km² (n={len(b)})  Mann-Whitney (El Niño < resto) p={pu:.3f}",
           f"  T2m media El Niño = {df.loc[nino,'t2m_c'].mean():.2f} °C | La Niña = {df.loc[nina,'t2m_c'].mean():.2f} °C | neutro = {df.loc[~nino & ~nina,'t2m_c'].mean():.2f} °C"]

lineas += ["", "CAUTELAS: n≈40 y autocorrelación → p-valores optimistas; MapBiomas filtrado temporalmente;",
           "ERA5-Land ~9 km (usar anomalías); isoterma 0 °C estimada por gradiente fijo 6,5 °C/km; exploratorio."]
txt = "\n".join(lineas)
print(txt)
(R / "validation" / "resultados_clima.txt").write_text(txt, encoding="utf-8")

# ---------------- Figura ----------------
propios = pd.DataFrame({  # contornos de confianza alta (validation/auditoria_mapbiomas_v1.md)
    "t": [2003.0, 2017.96, 2024.62, 2026.57],
    "a": [10.71, 6.36, 4.35, 4.50], "lo": [10.43, 6.19, 4.15, 4.28], "hi": [11.01, 6.53, 4.58, 4.80]})

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(4, 1, figsize=(8, 9.5), sharex=True,
                       gridspec_kw={"height_ratios": [2.2, 1, 1.2, 1]})
x = df["anio"]

ax[0].plot(mb["anio"], mb["area_km2_mapbiomas"], "-o", ms=3, color="#2c7fb8", label="MapBiomas Col. 3 (anual)")
ax[0].errorbar(propios["t"], propios["a"], yerr=[propios["a"] - propios["lo"], propios["hi"] - propios["a"]],
               fmt="s", color="#d95f0e", ms=5, capsize=3, label="Este estudio: escenas limpias (rango NDSI 0,3–0,5)")
for yr in x[nino]:
    ax[0].axvspan(yr - 0.5, yr + 0.5, color="#de2d26", alpha=0.08, lw=0)
ax[0].set_ylabel("Área glaciar (km²)")
ax[0].set_title("Nevado del Ruiz: glaciar, temperatura y El Niño (1981–2026)", loc="left", fontweight="bold")
ax[0].legend(frameon=False, loc="upper right")
ax[0].text(0.01, 0.04, "Franjas rojas: años El Niño (ONI anual ≥ 0,5)", transform=ax[0].transAxes, fontsize=7.5, color="#a50f15")

col = np.where(df["oni"] >= 0, "#de2d26", "#3182bd")
ax[1].bar(x, df["oni"], color=col, width=0.8)
ax[1].axhline(0, color="k", lw=0.5)
ax[1].set_ylabel("ONI anual (°C)")

ax[2].plot(x, df["t2m_c"], color="#e6550d", lw=1.2)
sen = stats.theilslopes(df["t2m_c"], x)
ax[2].plot(x, sen.intercept + sen.slope * x, "--", color="#e6550d", lw=1)
ax[2].set_ylabel("T 2 m ERA5-Land (°C)\n(celda ~9 km)")
a2 = ax[2].twinx(); a2.spines["right"].set_visible(True)
lo, hi = ax[2].get_ylim()   # misma curva: la isoterma es una transformación lineal de T
a2.set_ylim(z_celda + lo / GRAD, z_celda + hi / GRAD)
a2.set_ylabel("Isoterma 0 °C estimada (m)", color="#636363")
ax[2].text(0.01, 0.06, f"Tendencia {sen.slope*10:+.2f} °C/década ≈ {sen.slope*10/GRAD:+.0f} m/década de la isoterma 0 °C",
           transform=ax[2].transAxes, fontsize=7.5, color="#a63603")

ax[3].bar(x, df["chirps_anom_pct"], color=np.where(df["chirps_anom_pct"] >= 0, "#41ab5d", "#a6611a"), width=0.8)
ax[3].axhline(0, color="k", lw=0.5)
ax[3].set_ylabel("Precip. CHIRPS\n(anomalía %)")
ax[3].set_xlabel("Año")

fig.text(0.01, 0.012, "Fuentes: MapBiomas Colombia Col. 3; Landsat 5–9 (USGS); ERA5-Land (Copernicus/ECMWF); CHIRPS (UCSB-CHC); ONI (NOAA CPC).\n"
         "ANTARES Geospatial Lab · análisis exploratorio.", fontsize=6.5, color="#555")
fig.tight_layout(rect=(0, 0.035, 1, 1))
out = FIG / "glaciar_clima_el_nino.png"
fig.savefig(out, dpi=200)
print("Figura:", out)
