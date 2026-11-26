"""
ANTARES Geospatial Lab · Proyecto #1 Nevados
Delineación SEMIAUTOMÁTICA de contornos glaciares en escenas seleccionadas.

Método (tipo "band ratio + corrección manual", estándar en inventarios
glaciares, p. ej. GLIMS/RGI):
  1. Solo escenas revisadas visualmente (categorías A / A*), no automáticas.
  2. Hielo/nieve: NDSI = (verde - SWIR1)/(verde + SWIR1) > umbral,
     verde > 0.10, cota > 4400 m (Copernicus DEM), radio ≤ 6 km de la cumbre.
  3. Limpieza: se eliminan parches < 5 píxeles (0,45 ha) con gdal.SieveFilter.
  4. Polígonos con gdal.Polygonize; área en UTM 18N.
  5. Sensibilidad: área con umbrales NDSI 0,30 / 0,40 / 0,50 → rango de
     incertidumbre del método.
  6. Revisión visual de cada contorno (figura de control) y edición manual
     en QGIS si hace falta. Esto NO reemplaza esa revisión.

Ejecutar con el Python de QGIS:
  "C:\\Program Files\\QGIS 4.0.2\\bin\\python-qgis.bat" nevados\\python\\delinear_semiauto.py
"""
import csv
from pathlib import Path

import numpy as np
from osgeo import gdal, ogr, osr

gdal.UseExceptions()
RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
OUT = RAIZ / "data" / "processed"
FIG = RAIZ / "reports" / "figuras" / "control_contornos"
FIG.mkdir(parents=True, exist_ok=True)

UMBRAL = 0.40
SENSIBILIDAD = [0.30, 0.40, 0.50]
COTA_MIN = 4400
RADIO_M = 6000
MIN_PIX = 5

dem_ds = gdal.Open(str(RAW / "dem" / "copernicus_dem_glo30.tif"))
mb_ds = gdal.Open(str(RAW / "referencias" / "mapbiomas_c3_glaciar_1985_2024.tif"))

# Cumbre del Ruiz en UTM 18N
src = osr.SpatialReference(); src.ImportFromEPSG(4326)
dst = osr.SpatialReference(); dst.ImportFromEPSG(32618)
src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
cx, cy, _ = osr.CoordinateTransformation(src, dst).TransformPoint(-75.322, 4.895)


def a_grilla(ds_fuente, ds_ref, banda=1):
    """Remuestrea una banda a la grilla de ds_ref (vecino más cercano)."""
    gt = ds_ref.GetGeoTransform()
    mem = gdal.GetDriverByName("MEM").Create("", ds_ref.RasterXSize, ds_ref.RasterYSize, 1, gdal.GDT_Float32)
    mem.SetGeoTransform(gt); mem.SetProjection(ds_ref.GetProjection())
    tmp = gdal.Translate("", ds_fuente, format="MEM", bandList=[banda])
    gdal.ReprojectImage(tmp, mem, None, None, gdal.GRA_NearestNeighbour)
    return mem.GetRasterBand(1).ReadAsArray()


def mascara_hielo(g, s, dem, dist, umbral):
    with np.errstate(divide="ignore", invalid="ignore"):
        ndsi = (g - s) / (g + s)
    m = (ndsi > umbral) & (g > 0.10) & (dem > COTA_MIN) & (dist <= RADIO_M)
    return np.nan_to_num(m).astype(np.uint8), ndsi


def tamizar(m, ds_ref):
    mem = gdal.GetDriverByName("MEM").Create("", m.shape[1], m.shape[0], 1, gdal.GDT_Byte)
    mem.SetGeoTransform(ds_ref.GetGeoTransform()); mem.SetProjection(ds_ref.GetProjection())
    b = mem.GetRasterBand(1); b.WriteArray(m)
    gdal.SieveFilter(b, None, b, MIN_PIX, 8)
    return mem


# GeoPackage de salida
gpkg = RAIZ / "qgis" / "contornos_semiauto.gpkg"
if gpkg.exists():
    gpkg.unlink()
drv = ogr.GetDriverByName("GPKG")
ds_out = drv.CreateDataSource(str(gpkg))
capa = ds_out.CreateLayer("contornos_semiauto", dst, ogr.wkbMultiPolygon)
for nombre, tipo in [("fecha", ogr.OFTString), ("escena", ogr.OFTString), ("categoria", ogr.OFTString),
                     ("metodo", ogr.OFTString), ("area_km2", ogr.OFTReal),
                     ("area_min_km2", ogr.OFTReal), ("area_max_km2", ogr.OFTReal),
                     ("mapbiomas_km2", ogr.OFTReal), ("revision", ogr.OFTString)]:
    capa.CreateField(ogr.FieldDefn(nombre, tipo))

filas = []
for tif in sorted((RAW / "landsat").glob("*.tif"), key=lambda p: p.stem.split("_")[2]):
    sensor, ruta, fch, cat = tif.stem.split("_")
    fecha = f"{fch[:4]}-{fch[4:6]}-{fch[6:]}"
    ds = gdal.Open(str(tif))
    g = ds.GetRasterBand(2).ReadAsArray().astype("float32")
    s = ds.GetRasterBand(5).ReadAsArray().astype("float32")
    n = ds.GetRasterBand(4).ReadAsArray().astype("float32")
    dem = a_grilla(dem_ds, ds)
    gt = ds.GetGeoTransform()
    xs = gt[0] + (np.arange(ds.RasterXSize) + 0.5) * gt[1]
    ys = gt[3] + (np.arange(ds.RasterYSize) + 0.5) * gt[5]
    X, Y = np.meshgrid(xs, ys)
    dist = np.hypot(X - cx, Y - cy)
    px_km2 = abs(gt[1] * gt[5]) / 1e6

    areas = {}
    for u in SENSIBILIDAD:
        m, _ = mascara_hielo(g, s, dem, dist, u)
        tz = tamizar(m, ds)
        areas[u] = float(tz.GetRasterBand(1).ReadAsArray().sum() * px_km2)
        tz = None

    m, ndsi = mascara_hielo(g, s, dem, dist, UMBRAL)
    mem = tamizar(m, ds)
    # Polígonos
    tmp_ds = ogr.GetDriverByName("Memory").CreateDataSource("t")
    tmp = tmp_ds.CreateLayer("p", dst, ogr.wkbPolygon)
    tmp.CreateField(ogr.FieldDefn("v", ogr.OFTInteger))
    b = mem.GetRasterBand(1)
    gdal.Polygonize(b, b, tmp, 0)
    multi = ogr.Geometry(ogr.wkbMultiPolygon)
    for f in tmp:
        if f.GetField("v") == 1:
            multi.AddGeometry(f.GetGeometryRef().Clone())

    anio = int(fch[:4])
    mb_km2 = None
    if 1985 <= anio <= 2024:
        mb = a_grilla(mb_ds, ds, banda=anio - 1984)
        mb_km2 = float(((mb == 1) & (dist <= RADIO_M)).sum() * px_km2)

    feat = ogr.Feature(capa.GetLayerDefn())
    feat.SetGeometry(multi)
    feat.SetField("fecha", fecha); feat.SetField("escena", f"{sensor}_{ruta}_{fch}")
    feat.SetField("categoria", cat.replace("Aestrella", "A*"))
    feat.SetField("metodo", f"NDSI>{UMBRAL}, verde>0.10, >{COTA_MIN} m, tamiz {MIN_PIX} px")
    feat.SetField("area_km2", round(multi.GetArea() / 1e6, 3))
    feat.SetField("area_min_km2", round(areas[0.50], 3))
    feat.SetField("area_max_km2", round(areas[0.30], 3))
    if mb_km2 is not None:
        feat.SetField("mapbiomas_km2", round(mb_km2, 3))
    feat.SetField("revision", "pendiente")
    capa.CreateFeature(feat)

    filas.append([fecha, f"{sensor}_{ruta}_{fch}", cat.replace("Aestrella", "A*"),
                  round(multi.GetArea() / 1e6, 3), round(areas[0.50], 3), round(areas[0.30], 3),
                  "" if mb_km2 is None else round(mb_km2, 3)])

    # Figura de control: falso color SWIR1-NIR-Verde + contorno en rojo
    rgb = np.stack([s, n, g], axis=-1)
    rgb = np.clip(rgb / 0.5, 0, 1)
    borde = (m == 1) & ~(
        np.roll(m, 1, 0).astype(bool) & np.roll(m, -1, 0).astype(bool) &
        np.roll(m, 1, 1).astype(bool) & np.roll(m, -1, 1).astype(bool))
    borde &= mem.GetRasterBand(1).ReadAsArray().astype(bool)
    rgb[borde] = [1, 0, 0]
    img8 = (rgb * 255).astype(np.uint8)
    r0, r1 = 120, 420   # recorte centrado en el glaciar
    img8 = img8[r0:r1, r0:r1]
    png = gdal.GetDriverByName("MEM").Create("", img8.shape[1], img8.shape[0], 3, gdal.GDT_Byte)
    for i in range(3):
        png.GetRasterBand(i + 1).WriteArray(img8[:, :, i])
    gdal.GetDriverByName("PNG").CreateCopy(str(FIG / f"{fecha}_{sensor}.png"), png)
    print(f"{fecha} {sensor:5s} [{cat:9s}] área={multi.GetArea()/1e6:6.3f} km² "
          f"(rango {areas[0.50]:.3f}–{areas[0.30]:.3f})  MapBiomas={mb_km2}")

ds_out = None
with open(OUT / "areas_semiauto_vs_mapbiomas.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["fecha", "escena", "categoria", "area_km2_ndsi040", "area_km2_ndsi050",
                "area_km2_ndsi030", "mapbiomas_km2_mismo_anio"])
    w.writerows(filas)
print("OK:", gpkg, "|", OUT / "areas_semiauto_vs_mapbiomas.csv")
