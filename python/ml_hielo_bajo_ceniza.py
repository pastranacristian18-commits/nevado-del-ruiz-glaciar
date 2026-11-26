"""
ANTARES Geospatial Lab · Proyecto #1 Nevados
Experimento ML: ¿se puede mapear el hielo del Ruiz cuando está cubierto de ceniza?

Datos: 9 escenas Landsat 8/9 (gee/07): 6 bandas SR + temperatura de brillo B10.
Etiquetas: contornos semiautomáticos de escenas limpias (qgis/contornos_semiauto.gpkg).
  - Escena limpia → su propio contorno.
  - Escena con ceniza → contorno limpio más cercano (2024-08-15, a 5–8 meses).
  - Franja de 2 píxeles (60 m) a cada lado del borde se EXCLUYE (etiqueta incierta).
  - 2020-01-09 no tiene contorno cercano: solo se usa para aplicar el modelo.
Modelos: línea base NDSI > 0,40 (sin entrenamiento); regresión logística;
  Random Forest; XGBoost.
Conjuntos de variables (ablación):
  S   espectral (6 bandas, NDSI, NDWI, rojo/SWIR1, brillo, textura NIR)
  ST  S + anomalía térmica (B10 menos la mediana de la escena)
  STT ST + topografía (cota, pendiente, orientación)
Validación:
  A) dejar-una-escena-fuera (8 escenas etiquetadas).
  B) dejar-un-sector-fuera (4 cuadrantes alrededor de la cumbre, con margen
     de 300 m): prueba si el modelo aprende señal física y no "dónde está".
Ejecutar:
  "C:\\Program Files\\QGIS 4.0.2\\bin\\python-qgis.bat" python\\ml_hielo_bajo_ceniza.py
"""
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / ".pylibs"))

import numpy as np
import pandas as pd
from osgeo import gdal, ogr, osr
from scipy import ndimage
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from xgboost import XGBClassifier
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

gdal.UseExceptions(); ogr.UseExceptions()
RNG = np.random.default_rng(42)
ML = R / "data" / "raw" / "ml"
OUTP, FIG, VAL = R / "data" / "processed", R / "reports" / "figuras", R / "validation"
PX_KM2 = 0.0009

ESCENAS = {  # escena: (tipo, fecha del contorno de referencia o None)
    "LC08_009056_20231203_ceniza": ("ceniza", "2024-08-15"),
    "LC08_009056_20240104_ceniza": ("ceniza", "2024-08-15"),
    "LC09_009056_20250114_ceniza": ("ceniza", "2024-08-15"),
    "LC08_009057_20250122_ceniza": ("ceniza", "2024-08-15"),
    "LC08_009057_20200109_ceniza": ("ceniza", None),
    "LC08_009056_20171218_limpia": ("limpia", "2017-12-18"),
    "LC09_009056_20230618_limpia": ("limpia", "2023-06-18"),
    "LC08_009057_20240815_limpia": ("limpia", "2024-08-15"),
    "LC09_009056_20260728_limpia": ("limpia", "2026-07-28"),
}
VARS = {
    "S": ["blue", "green", "red", "nir", "swir1", "swir2", "ndsi", "ndwi", "red_swir1", "brillo", "tex_nir"],
}
VARS["ST"] = VARS["S"] + ["bt_anom"]
VARS["STT"] = VARS["ST"] + ["cota", "pendiente", "asp_cos", "asp_sin"]

# ------------------------------------------------------------------ grilla
ref_ds = gdal.Open(str(ML / f"{next(iter(ESCENAS))}.tif"))
GT, PROJ = ref_ds.GetGeoTransform(), ref_ds.GetProjection()
NY, NX = ref_ds.RasterYSize, ref_ds.RasterXSize


def a_grilla(path, banda=1):
    mem = gdal.GetDriverByName("MEM").Create("", NX, NY, 1, gdal.GDT_Float32)
    mem.SetGeoTransform(GT); mem.SetProjection(PROJ)
    src = gdal.Open(str(path))
    gdal.ReprojectImage(src, mem, None, None, gdal.GRA_Bilinear)
    return mem.GetRasterBand(1).ReadAsArray()


dem = a_grilla(R / "data" / "raw" / "dem" / "copernicus_dem_glo30.tif")
gy, gx = np.gradient(dem, 30.0)
pendiente = np.degrees(np.arctan(np.hypot(gx, gy)))
aspecto = np.arctan2(-gx, gy)
xs = GT[0] + (np.arange(NX) + 0.5) * GT[1]
ys = GT[3] + (np.arange(NY) + 0.5) * GT[5]
X, Y = np.meshgrid(xs, ys)
s_geo = osr.SpatialReference(); s_geo.ImportFromEPSG(4326); s_geo.SetAxisMappingStrategy(0)
s_utm = osr.SpatialReference(); s_utm.ImportFromEPSG(32618); s_utm.SetAxisMappingStrategy(0)
cx, cy, _ = osr.CoordinateTransformation(s_geo, s_utm).TransformPoint(-75.322, 4.895)
dist = np.hypot(X - cx, Y - cy)
sector = (((np.degrees(np.arctan2(X - cx, Y - cy)) + 360) % 360) // 90).astype(int)  # 0=N,1=E,2=S,3=O
ang = (np.degrees(np.arctan2(X - cx, Y - cy)) + 360) % 360
borde_sector = np.minimum.reduce([np.abs(((ang - a + 180) % 360) - 180) for a in (0, 90, 180, 270)])
lejos_borde_sector = (np.radians(borde_sector) * np.maximum(dist, 1)) > 300  # margen ~300 m
dominio_base = (dem > 4400) & (dist <= 6000)

gpkg = ogr.Open(str(R / "qgis" / "contornos_semiauto.gpkg"))
capa = gpkg.GetLayer(0)


def contorno(fecha):
    mem = gdal.GetDriverByName("MEM").Create("", NX, NY, 1, gdal.GDT_Byte)
    mem.SetGeoTransform(GT); mem.SetProjection(PROJ)
    capa.SetAttributeFilter(f"fecha = '{fecha}'")
    gdal.RasterizeLayer(mem, [1], capa, burn_values=[1])
    capa.SetAttributeFilter(None)
    return mem.GetRasterBand(1).ReadAsArray().astype(bool)


# ------------------------------------------------------------------ variables
datos = {}
for esc, (tipo, fref) in ESCENAS.items():
    ds = gdal.Open(str(ML / f"{esc}.tif"))
    assert (ds.RasterXSize, ds.RasterYSize) == (NX, NY), esc
    b = {n: ds.GetRasterBand(i + 1).ReadAsArray().astype("float32")
         for i, n in enumerate(["blue", "green", "red", "nir", "swir1", "swir2", "bt10", "qa"])}
    with np.errstate(divide="ignore", invalid="ignore"):
        f = {k: b[k] for k in ["blue", "green", "red", "nir", "swir1", "swir2"]}
        f["ndsi"] = (b["green"] - b["swir1"]) / (b["green"] + b["swir1"])
        f["ndwi"] = (b["green"] - b["nir"]) / (b["green"] + b["nir"])
        f["red_swir1"] = b["red"] / np.maximum(b["swir1"], 0.01)
        f["brillo"] = (b["blue"] + b["green"] + b["red"]) / 3
        m1 = ndimage.uniform_filter(b["nir"], 3); m2 = ndimage.uniform_filter(b["nir"] ** 2, 3)
        f["tex_nir"] = np.sqrt(np.maximum(m2 - m1 ** 2, 0))
    valido = dominio_base & np.isfinite(b["bt10"]) & (b["bt10"] > 150) & np.all(
        [np.isfinite(f[k]) for k in f], axis=0)
    f["bt_anom"] = b["bt10"] - np.nanmedian(b["bt10"][valido])
    f["cota"], f["pendiente"] = dem, pendiente
    f["asp_cos"], f["asp_sin"] = np.cos(aspecto), np.sin(aspecto)
    y = None; usable = valido.copy()
    if fref:
        y = contorno(fref)
        incierto = ndimage.binary_dilation(y, iterations=2) & ~ndimage.binary_erosion(y, iterations=2)
        usable &= ~incierto
    datos[esc] = dict(tipo=tipo, fref=fref, f=f, y=y, valido=valido, usable=usable,
                      rgb=np.clip(np.dstack([b["swir1"], b["nir"], b["green"]]) / 0.5, 0, 1))
    print(f"{esc}: válidos={valido.sum()}  usables={usable.sum()}  ref={fref}"
          + (f"  hielo_ref={y[valido].sum()*PX_KM2:.2f} km²" if fref else ""))

ETIQ = [e for e in ESCENAS if ESCENAS[e][1]]


def matriz(esc, vars_, mascara):
    f = datos[esc]["f"]
    return np.column_stack([f[v][mascara] for v in vars_])


def muestra(escs, vars_, extra=None, n=8000):
    Xs, ys = [], []
    for e in escs:
        m = datos[e]["usable"] if extra is None else datos[e]["usable"] & extra
        idx = np.flatnonzero(m)
        y = datos[e]["y"].ravel()[idx]
        sel = []
        for c in (0, 1):   # balance de clases por escena
            ic = idx[y == c]
            sel.append(RNG.choice(ic, size=min(n // 2, ic.size), replace=False))
        sel = np.concatenate(sel)
        mm = np.zeros(m.size, bool); mm[sel] = True; mm = mm.reshape(m.shape)
        Xs.append(matriz(e, vars_, mm)); ys.append(datos[e]["y"][mm])
    return np.vstack(Xs), np.concatenate(ys)


def modelos():
    return {
        "Logística": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced")),
        "RandomForest": RandomForestClassifier(n_estimators=200, min_samples_leaf=3, n_jobs=-1,
                                               class_weight="balanced", random_state=42),
        "XGBoost": XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.08, subsample=0.8,
                                 colsample_bytree=0.8, n_jobs=-1, random_state=42, eval_metric="logloss"),
    }


def metricas(pred, y, m):
    p, t = pred[m], y[m]
    tp = np.sum(p & t); fp = np.sum(p & ~t); fn = np.sum(~p & t)
    f1 = 2 * tp / max(2 * tp + fp + fn, 1); iou = tp / max(tp + fp + fn, 1)
    return f1, iou


def area(pred, esc):
    return pred[datos[esc]["valido"]].sum() * PX_KM2


filas, predicciones = [], {}
# ------------------------------------------------------------------ línea base
for e in ETIQ:
    d = datos[e]; pred = (d["f"]["ndsi"] > 0.40) & (d["f"]["green"] > 0.10) & d["valido"]
    f1, iou = metricas(pred, d["y"], d["usable"])
    filas.append(dict(validacion="A_escena", modelo="NDSI_0.40", vars="-", escena=e, tipo=d["tipo"], f1=f1, iou=iou,
                      area_pred=area(pred, e), area_ref=area(d["y"], e)))
    predicciones[("NDSI_0.40", e)] = pred

# ------------------------------------------------------------------ A) dejar una escena fuera
for vs, vars_ in VARS.items():
    for e in ETIQ:
        Xtr, ytr = muestra([x for x in ETIQ if x != e], vars_)
        for nombre, mod in modelos().items():
            mod.fit(Xtr, ytr.astype(int))
            d = datos[e]
            pred = np.zeros((NY, NX), bool)
            pred[d["valido"]] = mod.predict(matriz(e, vars_, d["valido"])) == 1
            f1, iou = metricas(pred, d["y"], d["usable"])
            filas.append(dict(validacion="A_escena", modelo=nombre, vars=vs, escena=e, tipo=d["tipo"], f1=f1, iou=iou,
                              area_pred=area(pred, e), area_ref=area(d["y"], e)))
            predicciones[(f"{nombre}|{vs}", e)] = pred
    print("A listo:", vs)

# ------------------------------------------------------------------ B) dejar un sector fuera
# Cada sector se predice con un modelo que NUNCA vio ese sector (en ninguna escena).
# Las 4 predicciones fuera-de-sector se unen en un mapa completo y se evalúa el mapa entero
# (agregación por píxeles; promediar por sector distorsiona porque N y O casi no tienen hielo en 2024).
CENIZA = [x for x in ETIQ if datos[x]["tipo"] == "ceniza"]
for vs, vars_ in VARS.items():
    mapas = {(n, e): np.zeros((NY, NX), bool) for n in modelos() for e in CENIZA}
    for s in range(4):
        fuera = (sector != s) & lejos_borde_sector
        dentro = (sector == s) & lejos_borde_sector
        Xtr, ytr = muestra(ETIQ, vars_, extra=fuera)
        for nombre, mod in modelos().items():
            mod.fit(Xtr, ytr.astype(int))
            for e in CENIZA:
                m = datos[e]["valido"] & dentro
                mapas[(nombre, e)][m] = mod.predict(matriz(e, vars_, m)) == 1
    for (nombre, e), pred in mapas.items():
        d = datos[e]; ev = d["usable"] & lejos_borde_sector
        f1, iou = metricas(pred, d["y"], ev)
        filas.append(dict(validacion="B_sector", modelo=nombre, vars=vs, escena=e, tipo="ceniza", f1=f1, iou=iou,
                          area_pred=pred[d["valido"] & lejos_borde_sector].sum() * PX_KM2,
                          area_ref=d["y"][d["valido"] & lejos_borde_sector].sum() * PX_KM2))
        predicciones[(f"B|{nombre}|{vs}", e)] = pred
    print("B listo:", vs)
for e in CENIZA:
    d = datos[e]; ev = d["usable"] & lejos_borde_sector
    pred = (d["f"]["ndsi"] > 0.40) & (d["f"]["green"] > 0.10) & d["valido"]
    f1, iou = metricas(pred, d["y"], ev)
    filas.append(dict(validacion="B_sector", modelo="NDSI_0.40", vars="-", escena=e, tipo="ceniza", f1=f1, iou=iou,
                      area_pred=pred[d["valido"] & lejos_borde_sector].sum() * PX_KM2,
                      area_ref=d["y"][d["valido"] & lejos_borde_sector].sum() * PX_KM2))

res = pd.DataFrame(filas)
res.to_csv(OUTP / "ml_metricas_detalle.csv", index=False, float_format="%.4f")

# ------------------------------------------------------------------ resumen
A = res[res.validacion == "A_escena"].copy()
A["err_area_pct"] = 100 * (A.area_pred / A.area_ref - 1)
resA = A.groupby(["tipo", "modelo", "vars"]).agg(F1=("f1", "mean"), IoU=("iou", "mean"),
                                                   err_area_pct=("err_area_pct", "mean")).reset_index()
B = res[res.validacion == "B_sector"].copy(); B["err_area_pct"] = 100 * (B.area_pred / B.area_ref - 1)
resB = B.groupby(["modelo", "vars"]).agg(F1=("f1", "mean"), IoU=("iou", "mean"), err_area_pct=("err_area_pct", "mean")).reset_index()
resA.to_csv(OUTP / "ml_resumen_A.csv", index=False, float_format="%.3f")
resB.to_csv(OUTP / "ml_resumen_B.csv", index=False, float_format="%.3f")

# Importancia por permutación: RF|ST entrenado sin 2024-01-04, evaluado en esa escena
e_test = "LC08_009056_20240104_ceniza"
Xtr, ytr = muestra([x for x in ETIQ if x != e_test], VARS["STT"])
rf = modelos()["RandomForest"].fit(Xtr, ytr.astype(int))
Xte, yte = muestra([e_test], VARS["STT"], n=6000)
pi = permutation_importance(rf, Xte, yte.astype(int), n_repeats=5, random_state=42, scoring="f1", n_jobs=1)
imp = pd.Series(pi.importances_mean, index=VARS["STT"]).sort_values(ascending=False)

# Aplicación a 2020-01-09 (sin etiqueta): modelo entrenado con todo
e20 = "LC08_009057_20200109_ceniza"
apl = {}
for vs in ("ST", "STT"):
    Xtr, ytr = muestra(ETIQ, VARS[vs])
    for nombre in ("RandomForest", "XGBoost"):
        mod = modelos()[nombre].fit(Xtr, ytr.astype(int))
        d = datos[e20]; pred = np.zeros((NY, NX), bool)
        pred[d["valido"]] = mod.predict(matriz(e20, VARS[vs], d["valido"])) == 1
        apl[f"{nombre}|{vs}"] = pred
pred20_ndsi = (datos[e20]["f"]["ndsi"] > 0.40) & (datos[e20]["f"]["green"] > 0.10) & datos[e20]["valido"]

with open(VAL / "ml_resultados.txt", "w", encoding="utf-8") as fh:
    fh.write("A) DEJAR UNA ESCENA FUERA — promedio por tipo de escena\n")
    fh.write(resA.sort_values(["tipo", "F1"], ascending=[True, False]).to_string(index=False, float_format="%.3f"))
    fh.write("\n\nB) DEJAR UN SECTOR FUERA — escenas con ceniza\n")
    fh.write(resB.sort_values("F1", ascending=False).to_string(index=False, float_format="%.3f"))
    fh.write("\n\nImportancia por permutación (RF, variables STT, prueba en 2024-01-04, caída de F1)\n")
    fh.write(imp.to_string(float_format="%.3f"))
    fh.write(f"\n\nAplicación a 2020-01-09 (sin etiqueta): NDSI {area(pred20_ndsi, e20):.2f} km²; "
             + "; ".join(f"{k} {area(v, e20):.2f} km²" for k, v in apl.items()) + " (MapBiomas 2020: 6,32 km²)\n")
print(open(VAL / "ml_resultados.txt", encoding="utf-8").read())

# ------------------------------------------------------------------ figura
VENT = 3300
filas_fig = ["LC08_009056_20231203_ceniza", "LC08_009056_20240104_ceniza", "LC09_009056_20250114_ceniza"]
cols = [("Imagen (SWIR1-NIR-Verde)", None, None),
        ("Línea base NDSI > 0,40", "NDSI_0.40", ("A_escena", "NDSI_0.40", "-")),
        ("XGBoost + térmico + topografía\n(dejando la escena fuera)", "XGBoost|STT", ("A_escena", "XGBoost", "STT")),
        ("XGBoost + térmico\n(dejando el sector fuera)", "B|XGBoost|ST", ("B_sector", "XGBoost", "ST"))]
fig, axs = plt.subplots(len(filas_fig), len(cols), figsize=(13, 3.4 * len(filas_fig)), dpi=130)
ext = [GT[0], GT[0] + GT[1] * NX, GT[3] + GT[5] * NY, GT[3]]
for i, e in enumerate(filas_fig):
    d = datos[e]
    for j, (titulo, clave, met) in enumerate(cols):
        ax = axs[i, j]; ax.imshow(d["rgb"], extent=ext)
        if clave:
            pred = predicciones[(clave, e)]
            ov = np.zeros((NY, NX, 4)); ov[pred] = [0.0, 0.9, 1.0, 0.55]
            ax.imshow(ov, extent=ext)
            r = res[(res.validacion == met[0]) & (res.escena == e) & (res.modelo == met[1]) & (res.vars == met[2])].iloc[0]
            ax.text(0.03, 0.04, f"F1={r.f1:.2f}  área={r.area_pred:.2f} km²", transform=ax.transAxes,
                    color="white", fontsize=8, bbox=dict(facecolor="black", alpha=0.55, lw=0))
        ax.contour(X, Y, d["y"].astype(float), levels=[0.5], colors="#ff2b2b", linewidths=0.9)
        ax.set_xlim(cx - VENT, cx + VENT); ax.set_ylim(cy - VENT, cy + VENT); ax.set_xticks([]); ax.set_yticks([])
        if i == 0: ax.set_title(titulo, fontsize=9.5)
    fe = e.split("_")[2]
    axs[i, 0].set_ylabel(f"{fe[:4]}-{fe[4:6]}-{fe[6:]}\n(ceniza)", fontsize=9)
fig.suptitle("¿Hielo bajo ceniza? Rojo: contorno de referencia (escena limpia de ago-2024) · cian: predicción", fontsize=10.5)
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig(FIG / "ml_hielo_bajo_ceniza.png"); plt.close(fig)
print("Figura:", FIG / "ml_hielo_bajo_ceniza.png")
