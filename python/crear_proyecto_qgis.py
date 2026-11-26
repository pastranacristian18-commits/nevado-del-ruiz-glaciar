"""
ANTARES Geospatial Lab · Proyecto #1 Nevados
Crea el proyecto QGIS nevados/qgis/nevados_ruiz.qgz con:
  - Copernicus DEM (sombreado)
  - MapBiomas Col. 3 glaciar 1985 y 2024
  - 11 escenas Landsat seleccionadas en falso color SWIR1-NIR-Verde
  - Capa vacía para digitalizar contornos: qgis/contornos_glaciar.gpkg

Ejecutar con el Python de QGIS:
  "C:\\Program Files\\QGIS 4.0.2\\bin\\python-qgis.bat" nevados\\python\\crear_proyecto_qgis.py
"""
import os
import sys
from pathlib import Path

from qgis.core import (
    QgsApplication, QgsProject, QgsRasterLayer, QgsVectorLayer,
    QgsCoordinateReferenceSystem, QgsVectorFileWriter, QgsField, QgsFields,
    QgsWkbTypes, QgsHillshadeRenderer, QgsPalettedRasterRenderer,
    QgsMultiBandColorRenderer, QgsContrastEnhancement, QgsCoordinateTransformContext,
    QgsFillSymbol,
)
from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QColor

RAIZ = Path(__file__).resolve().parents[1]          # .../nevados
RAW = RAIZ / "data" / "raw"
QGIS_DIR = RAIZ / "qgis"
CRS = QgsCoordinateReferenceSystem("EPSG:32618")

qgs = QgsApplication([], False)
qgs.initQgis()
proj = QgsProject.instance()
proj.setCrs(CRS)
proj.setTitle("ANTARES · Nevado del Ruiz — glaciar, páramo y agua")
raiz = proj.layerTreeRoot()


def agregar(capa, grupo=None, visible=True):
    if not capa.isValid():
        print("NO VÁLIDA:", capa.name())
        return None
    proj.addMapLayer(capa, False)
    nodo = (grupo or raiz).addLayer(capa)
    nodo.setItemVisibilityChecked(visible)
    return capa


# ---------------- Capa de digitalización (GeoPackage) ----------------
gpkg = QGIS_DIR / "contornos_glaciar.gpkg"
if not gpkg.exists():
    campos = QgsFields()
    for nombre, tipo in [("fecha", QMetaType.Type.QString), ("escena", QMetaType.Type.QString),
                         ("categoria", QMetaType.Type.QString), ("interprete", QMetaType.Type.QString),
                         ("confianza", QMetaType.Type.QString), ("notas", QMetaType.Type.QString)]:
        campos.append(QgsField(nombre, tipo))
    opts = QgsVectorFileWriter.SaveVectorOptions()
    opts.driverName = "GPKG"
    opts.layerName = "contornos_glaciar"
    w = QgsVectorFileWriter.create(str(gpkg), campos, QgsWkbTypes.Type.MultiPolygon, CRS,
                                   QgsCoordinateTransformContext(), opts)
    del w
contornos = QgsVectorLayer(f"{gpkg}|layername=contornos_glaciar", "Contornos glaciar (digitalizar)", "ogr")
contornos.setRenderer(contornos.renderer().clone())
contornos.renderer().setSymbol(QgsFillSymbol.createSimple(
    {"color": "0,0,0,0", "outline_color": "255,0,0", "outline_width": "0.6"}))
agregar(contornos)

# ---------------- MapBiomas ----------------
g_ref = raiz.addGroup("Referencias")
mb_path = str(RAW / "referencias" / "mapbiomas_c3_glaciar_1985_2024.tif")
for banda, anio, color in [(40, 2024, "#d7191c"), (1, 1985, "#2166ac")]:
    capa = QgsRasterLayer(mb_path, f"MapBiomas glaciar {anio}")
    if capa.isValid():
        r = QgsPalettedRasterRenderer(capa.dataProvider(), banda,
                                      [QgsPalettedRasterRenderer.Class(1, QColor(color), str(anio))])
        capa.setRenderer(r)
        capa.renderer().setOpacity(0.6)
    agregar(capa, g_ref, visible=(anio == 1985))

# ---------------- Landsat ----------------
g_ls = raiz.addGroup("Landsat seleccionadas (SWIR1-NIR-Verde)")
escenas = sorted((RAW / "landsat").glob("*.tif"), key=lambda p: p.stem.split("_")[2], reverse=True)
for i, tif in enumerate(escenas):
    p = tif.stem.split("_")             # LC09_009056_20230618_A
    fecha = f"{p[2][:4]}-{p[2][4:6]}-{p[2][6:]}"
    capa = QgsRasterLayer(str(tif), f"{fecha} {p[0]} [{p[3]}]")
    if capa.isValid():
        r = QgsMultiBandColorRenderer(capa.dataProvider(), 5, 4, 2)   # swir1, nir, green
        for setter, banda in [(r.setRedContrastEnhancement, 5), (r.setGreenContrastEnhancement, 4),
                              (r.setBlueContrastEnhancement, 2)]:
            ce = QgsContrastEnhancement(capa.dataProvider().dataType(banda))
            ce.setMinimumValue(0.0)
            ce.setMaximumValue(0.5)
            ce.setContrastEnhancementAlgorithm(
                QgsContrastEnhancement.ContrastEnhancementAlgorithm.StretchToMinimumMaximum)
            setter(ce)
        capa.setRenderer(r)
    agregar(capa, g_ls, visible=(i == 0))
g_ls.setExpanded(True)

# ---------------- DEM ----------------
dem = QgsRasterLayer(str(RAW / "dem" / "copernicus_dem_glo30.tif"), "Copernicus DEM (sombreado)")
if dem.isValid():
    dem.setRenderer(QgsHillshadeRenderer(dem.dataProvider(), 1, 315, 45))
agregar(dem)

salida = QGIS_DIR / "nevados_ruiz.qgz"
ok = proj.write(str(salida))
print("Proyecto guardado:" if ok else "ERROR guardando:", salida)
print("Capas:", len(proj.mapLayers()))
qgs.exitQgis()
