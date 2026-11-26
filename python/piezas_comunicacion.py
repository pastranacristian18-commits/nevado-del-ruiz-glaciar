"""
ANTARES Geospatial Lab · Proyecto #1 Nevados
Piezas de comunicación a partir de resultados YA calculados (no genera datos nuevos):
  reports/linkedin/timelapse_ruiz.gif        escenas limpias con contorno y área
  reports/linkedin/antes_despues_2003_2024.png
  reports/linkedin/carrusel_ruiz.pdf         carrusel LinkedIn (6 diapositivas 4:5)
Regla: solo escenas de confianza alta (+1987 marcada como subestimada) para no
mostrar nieve fresca como si fuera glaciar.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from osgeo import gdal, ogr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

R = Path(__file__).resolve().parents[1]
RAW, P = R / "data" / "raw", R / "data" / "processed"
OUT = R / "reports" / "linkedin"; OUT.mkdir(parents=True, exist_ok=True)
CX, CY = None, None
AZUL, NAR, GRIS = "#2c7fb8", "#d95f0e", "#444444"

# ---------- contornos ----------
ds = ogr.Open(str(R / "qgis" / "contornos_semiauto.gpkg"))
lyr = ds.GetLayer(0)
cont = {}
for f in lyr:
    g = f.GetGeometryRef()
    polys = []
    for i in range(g.GetGeometryCount()):
        ring = g.GetGeometryRef(i).GetGeometryRef(0)
        polys.append(np.array(ring.GetPoints())[:, :2])
    cont[f.GetField("fecha")] = dict(polys=polys, area=f.GetField("area_km2"),
                                     lo=f.GetField("area_min_km2"), hi=f.GetField("area_max_km2"),
                                     conf=f.GetField("confianza"), escena=f.GetField("escena"))

FRAMES = [("1987-01-14", "Ceniza de la erupción de 1985: el área está subestimada"),
          ("2003-01-02", ""), ("2017-12-18", ""), ("2024-08-15", ""), ("2026-07-28", "")]


def cargar(fecha):
    tif = next((RAW / "landsat").glob(f"*_{fecha.replace('-', '')}_*.tif"))
    d = gdal.Open(str(tif))
    g, n, s = (d.GetRasterBand(b).ReadAsArray().astype(float) for b in (2, 4, 5))
    gt = d.GetGeoTransform()
    ext = [gt[0], gt[0] + gt[1] * d.RasterXSize, gt[3] + gt[5] * d.RasterYSize, gt[3]]
    rgb = np.clip(np.dstack([s, n, g]) / 0.5, 0, 1)
    return rgb, ext, tif.stem.split("_")[0]


ref = cont["2003-01-02"]["polys"]
allx = np.concatenate([p[:, 0] for p in ref]); ally = np.concatenate([p[:, 1] for p in ref])
CX, CY = allx.mean(), ally.mean()
VENT = 3300


def panel(ax, fecha, nota="", ref_dash=True, titulo=True, fs=11):
    rgb, ext, sensor = cargar(fecha)
    ax.imshow(rgb, extent=ext)
    if ref_dash and fecha != "2003-01-02" and fecha > "2003":
        for p in ref:
            ax.plot(p[:, 0], p[:, 1], "--", color="white", lw=1.0, alpha=0.9)
    c = cont[fecha]
    for p in c["polys"]:
        ax.plot(p[:, 0], p[:, 1], "-", color="#ff2b2b", lw=1.4)
    ax.set_xlim(CX - VENT, CX + VENT); ax.set_ylim(CY - VENT, CY + VENT)
    ax.set_xticks([]); ax.set_yticks([])
    if titulo:
        ax.text(0.03, 0.97, fecha[:4], transform=ax.transAxes, va="top", color="white",
                fontsize=fs + 10, fontweight="bold")
        coma = lambda v: f"{v:.2f}".replace(".", ",")
        ax.text(0.03, 0.85, f"{coma(c['area'])} km²  ({coma(c['lo'])}–{coma(c['hi'])})", transform=ax.transAxes,
                va="top", color="white", fontsize=fs + 1)
        ax.text(0.03, 0.03, f"{sensor.replace('LT05','Landsat 5').replace('LE07','Landsat 7').replace('LC08','Landsat 8').replace('LC09','Landsat 9')} · {fecha}",
                transform=ax.transAxes, color="white", fontsize=fs - 3)
        if nota:
            ax.text(0.03, 0.10, nota, transform=ax.transAxes, color="#ffd166", fontsize=fs - 3)
    # barra de escala 1 km
    x0, y0 = CX + VENT - 1400, CY - VENT + 300
    ax.plot([x0, x0 + 1000], [y0, y0], color="white", lw=3)
    ax.text(x0 + 500, y0 + 120, "1 km", color="white", ha="center", fontsize=fs - 3)


# ---------- GIF ----------
imgs = []
for fecha, nota in FRAMES:
    fig, ax = plt.subplots(figsize=(5.4, 5.4), dpi=120)
    panel(ax, fecha, nota)
    ax.text(0.97, 0.97, "rojo: borde del hielo\nblanco: borde 2003", transform=ax.transAxes,
            ha="right", va="top", color="white", fontsize=8)
    fig.subplots_adjust(0, 0, 1, 1)
    fig.canvas.draw()
    imgs.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3]))
    plt.close(fig)
dur = [1400] * (len(imgs) - 1) + [3000]
imgs[0].save(OUT / "timelapse_ruiz.gif", save_all=True, append_images=imgs[1:], duration=dur, loop=0)

# ---------- Antes / después ----------
fig, axs = plt.subplots(1, 2, figsize=(10, 5.4), dpi=160)
panel(axs[0], "2003-01-02", fs=12); panel(axs[1], "2024-08-15", fs=12)
fig.suptitle("Nevado del Ruiz: borde del glaciar en 2003 (blanco) y 2024 (rojo)", fontsize=13, fontweight="bold", y=0.99)
fig.text(0.5, 0.01, "Landsat 7/8, falso color SWIR1-NIR-Verde (hielo = cian). Contornos semiautomáticos NDSI > 0,40 revisados visualmente; "
         "rango = umbrales 0,3–0,5. ANTARES Geospatial Lab", ha="center", fontsize=7, color=GRIS)
fig.subplots_adjust(0.01, 0.05, 0.99, 0.93, wspace=0.02)
fig.savefig(OUT / "antes_despues_2003_2024.png"); plt.close(fig)

# ---------- Carrusel (PDF 4:5) ----------
mb = pd.read_csv(P / "serie_mapbiomas_c3_ruiz.csv")
s2 = R / "data" / "raw" / "referencias" / "miniaturas_s2"
W, H = 7.2, 9.0


def diapo(pdf, titulo, cuerpo=None, n=None):
    fig = plt.figure(figsize=(W, H), dpi=150)
    fig.patch.set_facecolor("white")
    fig.text(0.07, 0.94, titulo, fontsize=19, fontweight="bold", va="top", wrap=True, color="#111")
    if cuerpo:
        fig.text(0.07, 0.20, cuerpo, fontsize=11.5, va="top", color="#333", linespacing=1.45, wrap=True)
    if n:
        fig.text(0.93, 0.025, f"{n}/6", fontsize=9, ha="right", color=GRIS)
    fig.text(0.07, 0.025, "ANTARES Geospatial Lab · Nevados de Colombia", fontsize=8.5, color=GRIS)
    return fig


_n = [0]


def guardar(pdf, fig):
    _n[0] += 1
    pdf.savefig(fig)
    fig.savefig(OUT / f"carrusel_{_n[0]}.png", dpi=150)
    plt.close(fig)


with PdfPages(OUT / "carrusel_ruiz.pdf") as pdf:
    # 1 — gancho
    fig = diapo(pdf, "El Nevado del Ruiz perdió\n~3/4 de su glaciar en 40 años", n=1)
    a1 = fig.add_axes([0.07, 0.30, 0.42, 0.42]); a2 = fig.add_axes([0.51, 0.30, 0.42, 0.42])
    panel(a1, "2003-01-02", fs=9); panel(a2, "2024-08-15", fs=9)
    fig.text(0.07, 0.24, "14,7 km² en 1985 → 3,7 km² en 2024 (MapBiomas Colombia).\n"
             "Mis contornos en escenas limpias: 10,7 km² (2003) → 4,4 km² (2024).", fontsize=11.5, va="top", color="#333")
    guardar(pdf, fig)

    # 2 — serie
    fig = diapo(pdf, "40 años de datos satelitales", n=2)
    ax = fig.add_axes([0.12, 0.30, 0.82, 0.52])
    ax.plot(mb["anio"], mb["area_km2_mapbiomas"], "-o", ms=3, color=AZUL, label="MapBiomas Col. 3")
    pts = [(2003.0, "2003-01-02"), (2017.96, "2017-12-18"), (2024.62, "2024-08-15"), (2026.57, "2026-07-28")]
    for t, f in pts:
        c = cont[f]
        ax.errorbar(t, c["area"], yerr=[[c["area"] - c["lo"]], [c["hi"] - c["area"]]], fmt="s", color=NAR, capsize=3)
    ax.plot([], [], "s", color=NAR, label="Este análisis (escenas limpias)")
    ax.set_ylabel("Área glaciar (km²)"); ax.legend(frameon=False)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.text(0.07, 0.22, "Validación cruzada: el mismo día, Sentinel-2 y Landsat\ncoinciden con diferencias de 2–4 %.",
             fontsize=11.5, va="top", color="#333")
    guardar(pdf, fig)

    # 3 — ceniza
    fig = diapo(pdf, "Lo que no esperaba:\nla ceniza esconde el glaciar", n=3)
    for k, (f, t) in enumerate([("2024-01-08_TC", "Color verdadero: todo gris"),
                                 ("2024-01-08_FC", "Falso color: el hielo sigue ahí")]):
        a = fig.add_axes([0.07 + 0.44 * k, 0.36, 0.42, 0.42])
        a.imshow(Image.open(s2 / f"{f}.png")); a.set_xticks([]); a.set_yticks([])
        a.set_title(t, fontsize=10)
    fig.text(0.07, 0.30, "Sentinel-2, 8 de enero de 2024.\n"
             "En temporada seca el hielo \"visible\" cae a ~1 km², pero meses después\n"
             "vuelve a ~4 km². No se derrite y reaparece: lo tapa la ceniza del volcán.\n"
             "Los mapas automáticos miden hielo visible, no glaciar.", fontsize=11, va="top", color="#333")
    guardar(pdf, fig)

    # 4 — clima
    fig = diapo(pdf, "El Niño calienta y seca el Ruiz", n=4)
    a = fig.add_axes([0.05, 0.28, 0.90, 0.56])
    im = Image.open(R / "reports" / "figuras" / "glaciar_clima_el_nino.png")
    w, h = im.size
    a.imshow(im.crop((0, int(h * 0.36), w, int(h * 0.74)))); a.axis("off")
    fig.text(0.07, 0.25, "1981–2025: +0,10 °C por década (p = 0,005); la nevada del\nreanálisis casi desaparece.\n"
             "El Niño ↔ más temperatura (ρ = +0,54) y menos lluvia (ρ = −0,53).\n"
             "El Niño ↔ más pérdida de hielo: sugestivo (p ≈ 0,06), NO demostrado.", fontsize=11, va="top", color="#333")
    guardar(pdf, fig)

    # 5 — método y honestidad
    fig = diapo(pdf, "Lo que falló (y por qué importa)", n=5, cuerpo=None)
    fig.text(0.07, 0.80,
             "• Un método automático estándar (Fmask + NDSI) aceptó\n   5 de 2.102 escenas Landsat. Inservible en el Ruiz.\n\n"
             "• Tres versiones del algoritmo dieron series imposibles\n   antes de entender la causa: nubes, nieve fresca y ceniza.\n\n"
             "• Solución: selección visual de escenas, contornos\n   semiautomáticos, rango de sensibilidad y\n   validación entre sensores.\n\n"
             "• Todo el código, los datos y los intentos fallidos están\n   documentados para que cualquiera los reproduzca.",
             fontsize=12, va="top", color="#333", linespacing=1.4)
    guardar(pdf, fig)

    # 6 — siguiente
    fig = diapo(pdf, "Qué sigue", n=6)
    fig.text(0.07, 0.80,
             "1. Machine Learning para mapear hielo bajo ceniza\n    (comparado contra el método NDSI como línea base).\n\n"
             "2. El páramo que sube: vegetación por franjas de altura.\n\n"
             "3. Transferir el método a Santa Isabel, Tolima y El Cocuy.\n\n"
             "4. Contraste con datos de campo e IDEAM.\n\n"
             "Datos abiertos: MapBiomas Colombia, USGS Landsat,\nCopernicus Sentinel-2 y ERA5-Land, CHIRPS, NOAA.",
             fontsize=12, va="top", color="#333", linespacing=1.4)
    guardar(pdf, fig)

print("OK", [p.name for p in OUT.iterdir()])
