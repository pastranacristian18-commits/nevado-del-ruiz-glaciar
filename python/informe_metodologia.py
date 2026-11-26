"""
ANTARES Geospatial Lab · Proyecto #1 Nevados
Genera reports/informe_metodologia_nevado_del_ruiz.pdf (informe técnico detallado).
Ejecutar con el Python de QGIS (incluye reportlab):
  "C:\\Program Files\\QGIS 4.0.2\\bin\\python-qgis.bat" nevados\\python\\informe_metodologia.py
"""
from pathlib import Path

import pandas as pd
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle, ListFlowable, ListItem)

R = Path(__file__).resolve().parents[1]
FIG, LI, P, V = R / "reports" / "figuras", R / "reports" / "linkedin", R / "data" / "processed", R / "validation"
OUT = R / "reports" / "informe_metodologia_nevado_del_ruiz.pdf"

F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("S", f"{F}\\segoeui.ttf"))
pdfmetrics.registerFont(TTFont("S-B", f"{F}\\segoeuib.ttf"))
pdfmetrics.registerFont(TTFont("S-I", f"{F}\\segoeuii.ttf"))
pdfmetrics.registerFont(TTFont("S-BI", f"{F}\\segoeuiz.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("S", normal="S", bold="S-B", italic="S-I", boldItalic="S-BI")

AZ = colors.HexColor("#1f4e79")
st = {
    "t": ParagraphStyle("t", fontName="S-B", fontSize=24, leading=30, textColor=AZ, alignment=TA_CENTER),
    "st": ParagraphStyle("st", fontName="S", fontSize=13, leading=18, textColor=colors.HexColor("#444"), alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName="S-B", fontSize=15, leading=20, textColor=AZ, spaceBefore=14, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="S-B", fontSize=11.5, leading=15, textColor=colors.HexColor("#2e2e2e"), spaceBefore=10, spaceAfter=4),
    "p": ParagraphStyle("p", fontName="S", fontSize=9.6, leading=13.6, alignment=TA_JUSTIFY, spaceAfter=5),
    "c": ParagraphStyle("c", fontName="S-I", fontSize=8.2, leading=11, textColor=colors.HexColor("#555"), spaceAfter=8),
    "tb": ParagraphStyle("tb", fontName="S", fontSize=8, leading=10.2),
    "th": ParagraphStyle("th", fontName="S-B", fontSize=8, leading=10.2, textColor=colors.white),
    "box": ParagraphStyle("box", fontName="S", fontSize=9.3, leading=13, backColor=colors.HexColor("#eef4fa"),
                          borderColor=AZ, borderWidth=0.6, borderPadding=7, spaceBefore=6, spaceAfter=10),
    "warn": ParagraphStyle("warn", fontName="S", fontSize=9.3, leading=13, backColor=colors.HexColor("#fff4e5"),
                           borderColor=colors.HexColor("#d95f0e"), borderWidth=0.6, borderPadding=7, spaceBefore=6, spaceAfter=10),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=7.8, leading=10, backColor=colors.HexColor("#f4f4f4"),
                           borderPadding=5, spaceAfter=8),
}
S = []


def h1(t): S.append(Paragraph(t, st["h1"]))
def h2(t): S.append(Paragraph(t, st["h2"]))
def p(t): S.append(Paragraph(t, st["p"]))
def box(t, k="box"): S.append(Paragraph(t, st[k]))


def bullets(items):
    S.append(ListFlowable([ListItem(Paragraph(i, st["p"]), leftIndent=12) for i in items],
                          bulletType="bullet", start="•", leftIndent=12, bulletFontName="S"))


def tabla(filas, anchos, cab=True):
    data = [[Paragraph(str(c), st["th"] if (cab and i == 0) else st["tb"]) for c in f] for i, f in enumerate(filas)]
    t = Table(data, colWidths=[a * cm for a in anchos], repeatRows=1 if cab else 0)
    estilo = [("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#bbbbbb")),
              ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fb")])]
    if cab:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), AZ))
    t.setStyle(TableStyle(estilo))
    S.append(t); S.append(Spacer(1, 8))


def figura(ruta, ancho_cm, pie):
    w, h = PILImage.open(ruta).size
    img = Image(str(ruta), width=ancho_cm * cm, height=ancho_cm * cm * h / w)
    S.append(KeepTogether([img, Paragraph(pie, st["c"])]))


def pie_pagina(canv, doc):
    canv.saveState()
    canv.setFont("S", 7.5); canv.setFillColor(colors.HexColor("#777"))
    canv.drawString(2 * cm, 1.2 * cm, "ANTARES Geospatial Lab · Nevado del Ruiz — Informe metodológico v1 (25-nov-2026)")
    canv.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canv.restoreState()


# =============================== PORTADA ===============================
S += [Spacer(1, 4 * cm), Paragraph("Nevado del Ruiz:<br/>40 años de glaciar, ceniza y clima", st["t"]), Spacer(1, 0.6 * cm),
      Paragraph("Informe metodológico detallado — qué se hizo, cómo, qué falló y qué se puede afirmar", st["st"]),
      Spacer(1, 1.2 * cm)]
figura(LI / "antes_despues_2003_2024.png", 16, "Borde del glaciar en 2003 (blanco) y 2024 (rojo) sobre Landsat 7/8 en falso color.")
S += [Spacer(1, 1 * cm), Paragraph("ANTARES Geospatial Lab · Proyecto #1 Nevados<br/>Autor: Cristhian Pastrana<br/>"
                                    "Versión 1 · 25 de noviembre de 2026 · Nivel de madurez: N1 (100 % datos abiertos)", st["st"]),
      PageBreak()]

# =============================== 1. RESUMEN ===============================
h1("1. Resumen")
p("Este informe documenta, paso a paso, el primer proyecto de ANTARES Geospatial Lab: el análisis de la superficie glaciar del "
  "Volcán Nevado del Ruiz (Colombia) entre 1985 y 2026 con datos satelitales y climáticos abiertos. El objetivo inicial era "
  "construir una serie anual automática de área glaciar con Landsat y relacionarla con El Niño. Ese objetivo, tal como estaba "
  "planteado, <b>falló</b>: tres versiones de un algoritmo automático produjeron series físicamente imposibles. Diagnosticar "
  "por qué falló condujo al resultado más interesante del proyecto: en el Ruiz, la <b>ceniza volcánica oculta el glaciar</b> "
  "en temporada seca y la <b>nieve fresca lo infla</b> en temporada húmeda, de modo que los métodos automáticos basados en el "
  "índice NDSI miden <i>hielo visible</i> y no necesariamente <i>extensión glaciar</i>.")
p("El flujo final combinó: (1) la serie oficial de MapBiomas Colombia Colección 3 como serie a auditar; (2) selección visual "
  "de escenas Landsat limpias con un criterio independiente de la máscara de nubes; (3) contornos semiautomáticos con "
  "análisis de sensibilidad y revisión visual; (4) una serie densa de Sentinel-2 con Cloud Score+ y validación cruzada entre "
  "sensores; y (5) un análisis exploratorio de clima (ERA5-Land, CHIRPS) y El Niño (ONI de NOAA).")
box("<b>Resultados principales.</b> (a) MapBiomas registra 14,73 km² de glaciar en 1985 y 3,68 km² en 2024 (−75 %). "
    "(b) Nuestros contornos en escenas de confianza alta dan 10,71 km² (2003), 6,36 km² (2017), 4,35 km² (2024) y 4,50 km² (2026); "
    "con MapBiomas difieren entre −10 % y +18 %. (c) El mismo día, Sentinel-2 y Landsat coinciden con diferencias de 2–4 %. "
    "(d) En temporada seca el hielo visible cae a ~0,5–1,5 km² y meses después vuelve a ~3–4 km²: es ceniza, no pérdida. "
    "(e) La temperatura de la celda ERA5-Land sube +0,10 °C por década (p = 0,005); El Niño hace al Ruiz más cálido "
    "(ρ = +0,54) y más seco (ρ = −0,53). (f) La relación directa El Niño → pérdida de hielo es sugestiva (ρ = −0,30; p = 0,06) "
    "pero <b>no</b> concluyente. (g) Un modelo de Machine Learning para detectar hielo bajo ceniza alcanzó F1 = 0,88 "
    "dejando una escena fuera, pero cayó a ≈ 0,25 (igual que el NDSI) dejando un sector fuera: el acierto aparente era fuga de información espacial.")

# =============================== 2. PREGUNTA Y ÁREA ===============================
h1("2. Pregunta de investigación y área de estudio")
p("<b>Pregunta general:</b> ¿cuánta superficie glaciar ha perdido el Nevado del Ruiz desde 1985, con qué incertidumbre, y qué "
  "relación tiene esa pérdida con la temperatura, la precipitación y El Niño?")
p("<b>Área de estudio:</b> ventana cuadrada de 16 × 16 km centrada en la cumbre (4,895° N, 75,322° O; WGS84) dentro del "
  "Parque Nacional Natural Los Nevados. Para los cálculos de área se usó un radio de 6 km alrededor de la cumbre y una cota "
  "mínima de 4400 m (Copernicus DEM) para excluir nieve ocasional en zonas bajas. El Ruiz es un volcán activo, lo que "
  "condiciona todo el análisis óptico.")
p("<b>Sistema de referencia de trabajo:</b> UTM zona 18 Norte (EPSG:32618), píxel de 30 m (Landsat, MapBiomas, DEM) y "
  "10–20 m (Sentinel-2). Áreas calculadas sobre la proyección o con <i>ee.Image.pixelArea()</i> en Earth Engine.")

# =============================== 3. DATOS ===============================
h1("3. Datos utilizados")
p("Regla del proyecto: distinguir el procesamiento que ya hace el proveedor del que hacemos nosotros, y no aplicar "
  "correcciones que el producto ya trae.")
tabla([
    ["Fuente", "Resolución / periodo", "Procesamiento del proveedor", "Lo que hicimos nosotros", "Licencia / estado"],
    ["Landsat 5, 7, 8, 9 Collection 2 Level 2 (USGS)", "30 m · 1985–2026", "Reflectancia de superficie (corrección atmosférica), banda QA_PIXEL (Fmask)",
     "Factores de escala (×0,0000275 − 0,2), NDSI, máscaras, selección de escenas, contornos", "Dominio público USGS (verificar)"],
    ["Sentinel-2 L2A Harmonized (ESA/Copernicus)", "10–20 m · 2017–2026", "Corrección atmosférica Sen2Cor; corrección de offset de la línea base 04.00",
     "Mosaico diario, máscara Cloud Score+, NDSI, galería", "Licencia Copernicus (libre)"],
    ["Cloud Score+ S2 (Google)", "10 m", "Puntaje de calidad por píxel (modelo entrenado)", "Umbral cs_cdf ≥ 0,6 = despejado", "Verificar términos"],
    ["MapBiomas Colombia Col. 3 — clase 34 Glaciar y nival", "30 m · 1985–2024", "Clasificación Random Forest sobre mosaicos Landsat, filtros espaciales y temporales",
     "Serie de área a auditar; nunca usada como verdad", "Contradictoria: CC-BY vs uso no comercial (pendiente)"],
    ["Copernicus DEM GLO-30", "30 m", "Modelo digital de superficie", "Cotas (4400/4700 m), anillo, cota de celda ERA5", "Copernicus DEM (atribución)"],
    ["ERA5-Land mensual (ECMWF)", "~9 km · 1981–2025", "Reanálisis", "T 2 m, precipitación, nevada; anomalías y tendencias", "Licencia Copernicus"],
    ["CHIRPS péntadas (UCSB-CHC)", "~5 km · 1981–2025", "Satélite + estaciones", "Precipitación mensual y anual", "Verificar"],
    ["ONI (NOAA CPC)", "Mensual · 1950–2026", "Índice oficial de El Niño", "Promedio anual; clasificación de años El Niño", "Dominio público NOAA"],
], [3.2, 2.3, 3.8, 4.0, 2.9])

# =============================== 4. FLUJO ===============================
h1("4. Flujo de trabajo general")
tabla([
    ["Paso", "Herramienta", "Script / archivo", "Producto"],
    ["1. Serie automática Landsat (v1, v2, v3)", "Earth Engine", "gee/01_*.js, gee/02_*.js", "Series descartadas + diagnóstico"],
    ["2. Serie MapBiomas + galería de escenas", "Earth Engine", "gee/03_mapbiomas_y_galeria.js", "serie_mapbiomas_c3_ruiz.csv; 40 miniaturas"],
    ["3. Selección visual de escenas", "Revisión visual", "sampling/seleccion_escenas.md", "Categorías A, A*, B, C"],
    ["4. Descarga GeoTIFF", "Earth Engine + PowerShell", "gee/04_descargas_para_qgis.js", "11 escenas, MapBiomas 1985–2024, DEM"],
    ["5. Proyecto QGIS", "PyQGIS (QGIS 4.0.2)", "python/crear_proyecto_qgis.py", "qgis/nevados_ruiz.qgz"],
    ["6. Contornos semiautomáticos", "GDAL/NumPy", "python/delinear_semiauto.py", "contornos_semiauto.gpkg; áreas y rangos"],
    ["7. Sentinel-2 + Cloud Score+", "Earth Engine", "gee/05_sentinel2_serie_y_galeria.js", "serie_s2_hielo_limpio_ruiz.csv; galería"],
    ["8. Clima y El Niño", "Earth Engine + SciPy", "gee/06_clima_mensual.js; python/analisis_clima_glaciar.py", "Tabla anual, figura, estadísticas"],
    ["9. Comunicación", "Matplotlib/PIL", "python/piezas_comunicacion.py", "Timelapse, antes/después, carrusel"],
], [4.6, 3.0, 5.0, 3.6])

# =============================== 5. FASE 1 ===============================
h1("5. Fase 1 — Serie automática con Landsat: tres intentos fallidos")
p("El plan original era la línea base clásica de inventarios glaciares: clasificar nieve/hielo con el <b>NDSI</b> "
  "(Normalized Difference Snow Index = (Verde − SWIR1)/(Verde + SWIR1)) con umbral 0,40, y calcular el área de cada año.")
h2("5.1 Versión 1 — percentil 25 anual del NDSI")
p("<b>Método.</b> Se unieron Landsat 5, 7, 8 y 9 (C2 L2). Se enmascararon los píxeles marcados por Fmask como nube, nube "
  "dilatada o sombra. Para cada año se calculó el percentil 25 del NDSI (para quedarse con el hielo persistente y no con nevadas "
  "pasajeras) y se clasificó hielo donde NDSI > 0,40, verde > 0,10, cota > 4400 m y al menos 3 observaciones válidas. "
  "Se midió además la <i>cobertura válida</i> (fracción de la zona alta con datos suficientes).")
p("<b>Decisión deliberada:</b> no se enmascaró la saturación radiométrica, porque las bandas visibles de Landsat 5/7 se "
  "saturan sobre nieve y enmascararlas habría borrado el propio glaciar.")
p("<b>Resultado.</b> Serie imposible: 4,24 km² en 2023 y 0,42 km² en 2024; casi todos los años de 1985–1994 en cero; cobertura "
  "válida menor a 0,9 en 38 de 41 años.")
p("<b>Diagnóstico.</b> (a) Fmask marca el hielo brillante como nube y además dilata la máscara, borrando el glaciar; (b) el "
  "percentil 25 selecciona las fechas más sucias (sombras, ceniza, nubes residuales); (c) la cobertura se medía sobre toda la "
  "zona > 4400 m y no donde realmente hay glaciar.")
h2("5.2 Versión 2 — frecuencia anual de nieve")
p("<b>Cambios.</b> Solo se enmascararon nubes de confianza alta (bits 8–9 del QA_PIXEL) y sombras, sin dilatación. Cada píxel se "
  "clasificó como glaciar si era nieve/hielo en ≥ 50 % de sus observaciones válidas del año. Cobertura medida sobre la zona ≥ 4700 m, "
  "con una bandera de año confiable (cobertura ≥ 0,80).")
p("<b>Resultado.</b> Solo 8 de 41 años confiables, y aun así incoherentes: 14,55 km² en 2014, 7,59 km² en 2023, 1,53 km² en 2024. "
  "En el mapa, el hielo de 2023 aparecía casi tan grande como el de 2001.")
p("<b>Diagnóstico.</b> Al relajar la máscara, las <b>nubes de hielo</b> (que tienen NDSI alto, igual que la nieve) y las "
  "<b>nevadas estacionales</b> pasaron a contarse como glaciar.")
h2("5.3 Versión 3 — escena por escena (solo días despejados)")
p("<b>Cambios.</b> En lugar de compuestos anuales, se evaluó cada escena: fracción despejada de la zona glaciar (≥ 4700 m) según "
  "Fmask (nube, sombra, cirro, relleno). Solo se aceptaban escenas con ≥ 95 % despejado; por año se reportaban mediana, mínimo y máximo.")
p("<b>Resultado.</b> De <b>2102 escenas</b> Landsat, solo <b>5</b> superaron el filtro, y en dos de ellas el área era cero "
  "(escenas con reflectancia sin datos que el QA no marcaba). El resumen anual además falló con <i>User memory limit exceeded</i>.")
box("<b>Conclusión de la Fase 1.</b> Fmask no es utilizable sobre el glaciar del Ruiz: confunde hielo con nube y nube con hielo, "
    "y la nubosidad es casi permanente. El problema no se resuelve ajustando umbrales. Un pipeline 100 % automático con Landsat "
    "no sirve en esta montaña. Este resultado negativo se conserva documentado (gee/01_serie_glaciar_landsat_v1_descartado.js, "
    "gee/01_serie_glaciar_landsat.js, gee/02_escenas_despejadas.js).", "warn")

# =============================== 6. FASE 2 MAPBIOMAS ===============================
h1("6. Fase 2 — Serie de MapBiomas Colombia (Colección 3)")
p("<b>Por qué.</b> MapBiomas ya resolvió buena parte del problema con mosaicos de NDSI mínimo, clasificación Random Forest, "
  "filtros temporales y revisión experta (apéndice metodológico de glaciares de la Colección 3). Se tomó como <b>serie a auditar, "
  "no como verdad</b>.")
p("<b>Método.</b> Asset <i>projects/mapbiomas-colombia/assets/LULC/COLECCION3/INTEGRACION/COLOMBIA-1</i> (imagen con una banda por "
  "año, 1985–2024). Se calculó el área de la clase 34 en todas las bandas con una sola reducción espacial (evita el error de memoria). "
  "El valor de 2024 (3,679 km²) coincide con las 367,9 ha que reporta la ficha técnica de MapBiomas para el Ruiz, lo que valida "
  "que el área de estudio está bien delimitada.")
mb = pd.read_csv(P / "serie_mapbiomas_c3_ruiz.csv")
sel = mb[mb["anio"].isin([1985, 1990, 1991, 1995, 2000, 2005, 2010, 2013, 2014, 2015, 2020, 2021, 2022, 2023, 2024])]
pares = [(str(a), f"{v:.2f}".replace(".", ",")) for a, v in zip(sel["anio"], sel["area_km2_mapbiomas"])]
filas = [["Año", "km²", "Año", "km²", "Año", "km²"]]
for i in range(5):
    fila = []
    for k in range(3):
        fila += list(pares[i + 5 * k])
    filas.append(fila)
tabla(filas, [1.6, 1.6] * 3, cab=True)
p("<b>Observaciones críticas.</b> (a) La serie es casi monótona: indica filtros temporales (no es un error, pero hay que declararlo); "
  "(b) hay caídas abruptas en 1990→1991 (−1,96 km²), 2013→2014 (−0,84 km²) y 2021→2023 (−2,47 km²), que coinciden con periodos de "
  "actividad volcánica; (c) la cifra del IDEAM (~7,7 km² en un año no confirmado) no se usó porque no se pudo leer en el documento original.")

# =============================== 7. SELECCIÓN VISUAL ===============================
h1("7. Fase 3 — Selección visual de escenas Landsat")
p("<b>Criterio independiente de Fmask.</b> Se definió un <b>anillo</b> de roca y páramo entre 4200 y 4700 m alrededor del glaciar. "
  "Una escena es candidata si al menos 60 % del anillo es \"oscuro\" (azul < 0,15, es decir, sin nube). Se pre-filtraron escenas con "
  "CLOUD_COVER < 70 % y se excluyó Landsat 7 después de mayo de 2003 (falla del corrector de líneas, SLC-off). Las 40 mejores "
  "candidatas se visualizaron en falso color SWIR1-NIR-Verde (hielo limpio = cian, nube = blanco).")
figura(FIG / "hoja_contactos_candidatas.png", 16.5, "Figura 1. Galería de 40 escenas candidatas (Landsat 5, 7, 8 y 9). "
       "Se observa el glaciar cubierto de ceniza (gris-azulado opaco) en casi todas las escenas de temporada seca desde 2014.")
tabla([
    ["Categoría", "Criterio", "Escenas", "Uso"],
    ["A — hielo limpio", "Sin nieve fresca ni ceniza evidente", "2001-01-12, 2002-10-14, 2003-01-02, 2017-12-18, 2021-12-13, 2023-06-18, 2024-08-15, 2026-05-09", "Contornos (referencia)"],
    ["A* — con salvedad", "Ceniza parcial, borde de escena o nubes cercanas", "1987-01-14, 1997-10-24, 2026-07-28", "Contornos con incertidumbre"],
    ["B — nieve fresca", "Área inflada", "2001-01-28, 2015-09-24, 2016-07-08, 2023-09-06", "Variabilidad estacional"],
    ["C — ceniza", "Hielo oscurecido; NDSI lo subestima", "2014-12-26, 2020-01-09, 2022-01-30, 2023-01-25, 2023-12-03, 2024-01-04, 2025-01-14, 2025-01-22", "Casos de prueba para ML"],
], [2.6, 3.6, 7.2, 2.8])
p("<b>Vacíos:</b> no hubo candidatas en 1988–1996 ni en 2004–2013 (poca cobertura de Landsat 5 sobre Colombia y exclusión de Landsat 7 SLC-off). "
  "<b>Nota posterior:</b> en la revisión de los contornos, algunas escenas de la categoría A resultaron tener nieve fresca (2001, 2021, 2026-05); "
  "su confianza se rebajó (Sección 8).")

# =============================== 8. CONTORNOS ===============================
h1("8. Fase 4 — Contornos semiautomáticos y auditoría de MapBiomas")
p("<b>Descarga.</b> Las 11 escenas A/A*, la pila MapBiomas 1985–2024 (40 bandas) y el DEM se descargaron como GeoTIFF (UTM 18N, 30 m) "
  "mediante enlaces directos <i>getDownloadURL</i>, verificados con <i>gdalinfo</i> (bandas, proyección y rangos).")
p("<b>Método (tipo \"band ratio + corrección\", usado en inventarios GLIMS/RGI).</b> Para cada escena: NDSI > 0,40; verde > 0,10; "
  "cota > 4400 m; distancia ≤ 6 km a la cumbre; eliminación de parches menores a 5 píxeles (0,45 ha) con <i>gdal.SieveFilter</i>; "
  "vectorización con <i>gdal.Polygonize</i>; área en UTM. <b>Sensibilidad:</b> se repitió con umbrales 0,30 y 0,50 para obtener un "
  "rango. <b>Revisión visual:</b> cada contorno se superpuso a la imagen y se le asignó una confianza (alta, media, baja, descartar).")
figura(FIG / "control_contornos_hoja.png", 15.5, "Figura 2. Contornos semiautomáticos (rojo) sobre cada escena. 1987: ceniza al oeste no detectada. "
       "1997: escena cortada. 2001 y 2021: nieve fresca incluida.")
a = pd.read_csv(P / "areas_semiauto_vs_mapbiomas.csv")
conf = {"1987-01-14": "media", "1997-10-24": "descartar", "2001-01-12": "baja", "2002-10-14": "media", "2003-01-02": "alta",
        "2017-12-18": "alta", "2021-12-13": "baja", "2023-06-18": "media", "2024-08-15": "alta", "2026-05-09": "baja", "2026-07-28": "alta"}
f = [["Fecha", "Cat.", "Área NDSI 0,40 (km²)", "Rango 0,50–0,30", "MapBiomas mismo año", "Dif.", "Confianza"]]
for _, r in a.iterrows():
    mbv = r["mapbiomas_km2_mismo_anio"]
    dif = "" if pd.isna(mbv) or conf[r["fecha"]] == "descartar" else f"{100 * (r['area_km2_ndsi040'] / mbv - 1):+.0f} %"
    f.append([r["fecha"], r["categoria"], f"{r['area_km2_ndsi040']:.2f}".replace(".", ","),
              f"{r['area_km2_ndsi050']:.2f}–{r['area_km2_ndsi030']:.2f}".replace(".", ","),
              "" if pd.isna(mbv) else f"{mbv:.2f}".replace(".", ","), dif, conf[r["fecha"]]])
tabla(f, [2.2, 1.0, 2.6, 2.8, 2.8, 1.5, 2.2])
box("<b>Lectura.</b> En las escenas de confianza alta la diferencia con MapBiomas va de −10 % a +18 %. El sesgo depende de la "
    "superficie del glaciar y no del método: la ceniza produce subestimación (1987) y la nieve fresca sobreestimación (2001, 2021, 2026-05). "
    "Con solo escenas de confianza alta: 10,71 km² (2003) → 4,35 km² (2024), una pérdida de ~59 % en 21 años.")
p("<b>Limitación importante:</b> los contornos son semiautomáticos y la revisión visual fue preliminar; el autor debe revisarlos "
  "y editarlos en QGIS para que el criterio del intérprete quede documentado. No hubo un segundo intérprete independiente.")

# =============================== 9. SENTINEL-2 ===============================
h1("9. Fase 5 — Sentinel-2 con Cloud Score+")
p("<b>Por qué.</b> Landsat no tenía escenas limpias suficientes para entender la caída de MapBiomas en 2023. Sentinel-2 tiene revisita de "
  "~5 días y 10 m en el visible.")
p("<b>Método.</b> Colección S2 L2A Harmonized 2017–2026 con CLOUDY_PIXEL_PERCENTAGE < 80; enlace con Cloud Score+ (banda cs_cdf); "
  "un mosaico por día (el volcán puede caer en dos teselas); píxel despejado si cs_cdf ≥ 0,6 (los píxeles sin datos cuentan como "
  "no despejados). Se aceptaron los días con ≥ 90 % de la zona glaciar despejada y se midió el área de hielo limpio (NDSI > 0,40, "
  "verde > 0,10, > 4400 m) a 20 m. Para junio 2022 – junio 2024 se generó una galería en color verdadero y en falso color.")
p("<b>Resultado.</b> 359 días con imagen; 25 días aceptados.")
tabla([
    ["Fecha", "Sentinel-2 (km²)", "Landsat mismo día (km²)", "Diferencia"],
    ["2024-08-15", "4,245", "4,350 (Landsat 8)", "−2,4 %"],
    ["2026-05-09", "5,628", "5,826 (Landsat 9)", "−3,4 %"],
    ["2026-07-28", "4,323", "4,501 (Landsat 9)", "−4,0 %"],
], [3, 3.5, 4.5, 3])
p("<b>Serie de hielo limpio en temporada seca:</b> 3,1–3,7 km² (enero 2020) → 1,5 km² (enero 2023) → 0,9–1,1 km² (enero 2024) → "
  "0,5 km² (enero 2025). Pero en agosto 2024 y julio/agosto 2026 vuelve a 3,0–4,3 km². En octubre 2022 una nevada generalizada dio "
  "41,8 km² (no es glaciar).")
figura(FIG / "s2_periodo_critico.png", 16.5, "Figura 3. Sentinel-2, periodo crítico. Arriba: color verdadero (la ceniza se ve gris). "
       "Abajo: falso color SWIR1-NIR-Verde (el hielo bajo ceniza aparece azul-verdoso opaco con la forma del glaciar). "
       "El píxel rojo en el cráter es probablemente una anomalía térmica (no verificado).")
box("<b>Interpretación.</b> Un glaciar no pierde 85 % de su área y la recupera en seis meses. En temporada seca el glaciar está "
    "cubierto de ceniza: el hielo sigue ahí, pero el NDSI no lo detecta. Por tanto, en el Ruiz los métodos basados en NDSI miden "
    "hielo visible. <b>Sin embargo</b>, el valor de MapBiomas para 2023 (3,77 km²) se parece al nuestro de agosto 2024 (4,2–4,35 km²), "
    "así que <b>no se puede afirmar que MapBiomas esté equivocado</b>; la caída puede ser real en buena parte.")

# =============================== 10. CLIMA ===============================
h1("10. Fase 6 — Clima y El Niño")
p("<b>Datos.</b> ERA5-Land mensual (temperatura a 2 m, precipitación, nevada) en la celda de ~9 km que contiene la cumbre; CHIRPS "
  "(precipitación) promediado en un radio de 6 km; ONI de NOAA (promedio anual de las 12 temporadas trimestrales). "
  "<b>Isoterma de 0 °C estimada</b> = cota media de la celda (4283 m, calculada con Copernicus DEM) + T / 0,0065 (gradiente fijo de "
  "6,5 °C/km): es una aproximación, no una medición.")
p("<b>Métodos estadísticos.</b> Tendencias con Mann-Kendall y pendiente de Sen (con IC95 %); correlaciones de Spearman; comparación "
  "de años El Niño (ONI anual ≥ 0,5) contra el resto con Mann-Whitney (unilateral). Análisis en Python (SciPy).")
tabla([
    ["Variable", "Tendencia (Sen) por década", "IC95 %", "p (MK)"],
    ["Temperatura 2 m", "+0,10 °C", "+0,04 a +0,18", "0,005"],
    ["Isoterma 0 °C estimada", "+16 m", "+6 a +28", "0,005"],
    ["Nevada ERA5-Land", "−1,5 mm", "−3,3 a −0,4", "0,011"],
    ["Precipitación CHIRPS", "+42 mm", "−10 a +103", "0,11"],
    ["Área glaciar MapBiomas", "−2,15 km²", "−2,45 a −1,84", "< 0,001"],
], [5, 4, 3.5, 2.5])
tabla([
    ["Relación (Spearman)", "ρ", "p", "n", "Lectura"],
    ["ONI vs temperatura", "+0,54", "< 0,001", "45", "El Niño = más cálido"],
    ["ONI vs precipitación CHIRPS", "−0,53", "< 0,001", "45", "El Niño = más seco"],
    ["ONI vs nevada", "−0,33", "0,027", "45", "El Niño = menos nieve"],
    ["ΔÁrea vs ONI", "−0,30", "0,062", "39", "Sugestivo, no significativo"],
    ["ΔÁrea vs temperatura", "−0,28", "0,084", "39", "Sugestivo, no significativo"],
    ["ΔÁrea El Niño vs resto (Mann-Whitney)", "−0,25 vs −0,12 km²/año", "0,096", "8 / 31", "Sugestivo, no significativo"],
], [5, 3.3, 1.8, 1.5, 4.4])
figura(FIG / "glaciar_clima_el_nino.png", 13.5, "Figura 4. Área glaciar (MapBiomas y escenas limpias de este estudio), ONI anual, "
       "temperatura ERA5-Land con isoterma de 0 °C estimada y anomalía de precipitación CHIRPS, 1981–2026.")
p("<b>Por qué la señal glaciar es débil:</b> (a) MapBiomas está suavizado temporalmente; (b) las caídas grandes coinciden con actividad "
  "volcánica, que mezcla pérdida real con ceniza; (c) n ≈ 40 años y series autocorrelacionadas (los p-valores son optimistas); "
  "(d) una celda de 9 km no representa la cumbre, por eso se usan anomalías y tendencias.")
p("<b>Contexto actual:</b> el ONI de agosto–octubre de 2026 es +2,46 (El Niño fuerte en curso según NOAA).")

# =============================== 11. ML ===============================
h1("11. Fase 7 — Machine Learning: ¿hielo bajo ceniza?")
p("<b>Pregunta.</b> ¿Pueden modelos de Machine Learning con variables espectrales, térmicas y topográficas detectar el glaciar "
  "cuando está cubierto de ceniza, donde el NDSI falla?")
p("<b>Datos.</b> Nueve escenas Landsat 8/9 descargadas con <i>gee/07_descargas_ml_termico.js</i>: seis bandas de reflectancia de "
  "superficie y la temperatura de brillo de la banda térmica B10 (100 m nativos, entregada a 30 m). Cinco escenas con ceniza "
  "(2020-01, 2023-12, 2024-01, 2025-01 ×2) y cuatro limpias (2017-12, 2023-06, 2024-08, 2026-07). La hipótesis física: el hielo bajo "
  "ceniza se mantiene cerca de 0 °C, mientras la roca se calienta.")
p("<b>Etiquetas.</b> Contorno semiautomático de la escena limpia: el propio para escenas limpias y el de 2024-08-15 para las escenas "
  "con ceniza (5–8 meses de diferencia). Se excluyó una franja de 60 m a cada lado del borde. La escena de 2020 no tiene contorno "
  "cercano y solo se usó para aplicar el modelo.")
p("<b>Variables.</b> S = espectral (seis bandas, NDSI, NDWI, cociente rojo/SWIR1, brillo, textura NIR); ST = S + anomalía térmica "
  "(B10 menos la mediana de la escena); STT = ST + cota, pendiente y orientación. <b>Modelos:</b> NDSI > 0,40 (línea base), "
  "regresión logística, Random Forest (200 árboles) y XGBoost (300 árboles), con muestreo balanceado de 8000 píxeles por escena y semilla fija.")
p("<b>Validación.</b> (A) Dejar una escena fuera. (B) Dejar un sector fuera: el área se dividió en cuatro cuadrantes alrededor de la "
  "cumbre (con 300 m de margen); cada cuadrante se predijo con un modelo que nunca lo vio en ninguna escena, y las cuatro predicciones "
  "se unieron en un mapa completo para evaluarlo. Una primera versión promediaba el F1 por sector y quedaba sesgada porque los sectores "
  "norte y oeste casi no tienen hielo en 2024; se corrigió.")
tabla([
    ["Modelo", "Variables", "F1 (A: escena fuera)", "F1 (B: sector fuera)", "Error de área (B)"],
    ["NDSI > 0,40", "—", "0,28", "0,25", "−86 %"],
    ["XGBoost", "S", "0,60", "0,25", "−14 %"],
    ["XGBoost", "ST", "0,61", "0,21", "+3 %"],
    ["XGBoost", "STT", "0,88", "0,26", "−32 %"],
    ["Random Forest", "STT", "0,85", "0,27", "−28 %"],
    ["Regresión logística", "STT", "0,74", "0,34", "−17 %"],
], [3.4, 2.0, 3.6, 3.6, 3.4])
p("<b>Importancia por permutación</b> (Random Forest STT, prueba en 2024-01-04, caída del F1): cota 0,29; anomalía térmica 0,065; "
  "rojo/SWIR1 0,063; pendiente 0,04; el resto ≈ 0.")
figura(FIG / "ml_hielo_bajo_ceniza.png", 16.5, "Figura 5. Escenas con ceniza: imagen, línea base NDSI, XGBoost con térmico y topografía "
       "(validación dejando la escena fuera) y XGBoost con térmico (validación dejando el sector fuera). Rojo: contorno de referencia; cian: predicción.")
box("<b>Interpretación.</b> El F1 de 0,88 es en gran parte <b>fuga de información espacial</b>: todas las escenas con ceniza comparten "
    "la misma referencia y la variable más importante es la cota, así que el modelo aprende <i>dónde</i> está el glaciar y no <i>cómo</i> "
    "se ve el hielo bajo ceniza. Cuando el sector no se vio en el entrenamiento, todos los modelos caen a F1 ≈ 0,2–0,3, al nivel de la línea "
    "base: aciertan mejor el área total, pero ubican el hielo en sitios equivocados. El térmico aporta poco. <b>Con estos datos, el ML no "
    "resuelve el problema de forma generalizable.</b> La aplicación a 2020-01-09 (modelos 5,7–7,0 km² frente a 2,79 km² del NDSI y 6,32 km² "
    "de MapBiomas) no se considera una estimación confiable.", "warn")
p("<b>Siguiente iteración:</b> etiquetas independientes del hielo cubierto (alta resolución o campo), radar Sentinel-1, variables "
  "multitemporales (cambio respecto a la última escena limpia) y prueba de transferencia a otro glaciar (Santa Isabel, Tolima).")

# =============================== 11. FALLOS ===============================
h1("12. Registro completo de lo que falló")
tabla([
    ["#", "Qué falló", "Causa", "Cómo se resolvió / estado"],
    ["1", "Serie v1 imposible (percentil 25)", "Fmask borra el hielo; percentil escoge fechas sucias", "Descartada y documentada"],
    ["2", "Serie v2 incoherente (frecuencia)", "Nubes de hielo y nieve fresca con NDSI alto", "Descartada y documentada"],
    ["3", "Serie v3: 5 de 2102 escenas aceptadas", "Fmask inservible sobre el glaciar; nubosidad", "Cambio de enfoque: selección visual"],
    ["4", "Áreas cero en escenas \"despejadas\"", "QA sin marcar píxeles sin reflectancia válida", "Identificado; criterio de anillo independiente"],
    ["5", "User memory limit exceeded", "Reducciones año por año en el navegador", "Una sola reducción multibanda; exportaciones"],
    ["6", "Asset MapBiomas: tipo 'Image' vs 'IMAGE'", "Cambio de formato en la API", "Comparación sin distinguir mayúsculas"],
    ["7", "Cloud Score+ 'not found'", "Error de escritura del ID (guion bajo en lugar de barra)", "Corregido: GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED"],
    ["8", "Cota de celda ERA5: demasiados píxeles", "reduceResolution supera 65 535 píxeles", "Calculada localmente con el DEM"],
    ["9", "Precipitación ERA5-Land irreal (6000–9900 mm/año)", "Sesgo conocido del reanálisis en terreno complejo", "Se usa CHIRPS para lluvia"],
    ["10", "Copiado automático de scripts al Code Editor", "El navegador no compartía el portapapeles", "Pegado manual (Ctrl+V)"],
    ["11", "Error en Python (objeto GDAL liberado)", "Dataset temporal recolectado por el recolector de basura", "Referencia explícita al dataset"],
    ["12", "Descarga directa de CSV desde el navegador", "Bloqueada por el entorno", "Agregación anual extraída como texto"],
    ["13", "ML con F1 = 0,88 que no generaliza", "Fuga espacial: misma referencia y la cota como variable dominante", "Detectado con validación por sectores; documentado"],
    ["14", "Validación por sectores v1 sesgada", "Promedio de F1 por sector con sectores casi sin hielo", "Predicciones fuera-de-sector unidas y evaluadas juntas"],
    ["15", "Importancia de variables: proceso paralelo caído", "Los procesos hijos no encontraban las librerías locales", "Cálculo en un solo proceso"],
], [0.9, 4.2, 5.1, 5.6])

# =============================== 12. LIMITACIONES ===============================
h1("13. Limitaciones e incertidumbre")
bullets([
    "La incertidumbre dominante es la <b>superficie del glaciar</b> (ceniza y nieve fresca), no el sensor ni el píxel.",
    "Contornos semiautomáticos con una sola revisión visual preliminar; falta revisión detallada del autor y un segundo intérprete.",
    "Vacíos temporales de escenas limpias: 1988–1996 y 2004–2013.",
    "La resolución de 30 m es gruesa para un glaciar de ~4 km²; el error de borde puede ser relevante.",
    "MapBiomas: licencia contradictoria y filtros temporales no cuantificados por nosotros.",
    "ERA5-Land a ~9 km; isoterma estimada con gradiente fijo; precipitación de ERA5 no confiable aquí.",
    "Estadística exploratoria: n pequeño y autocorrelación; correlación no implica causalidad.",
    "No hay datos de campo (Nivel 2): ninguna cifra está calibrada con mediciones in situ.",
    "Las referencias bibliográficas de la Sección 17 se citan de memoria y deben verificarse antes de publicar formalmente.",
])

# =============================== 13. AFIRMACIONES ===============================
h1("14. Qué se puede afirmar y qué no")
tabla([
    ["Afirmación", "Estado"],
    ["El Ruiz perdió ~75 % de su superficie glaciar entre 1985 y 2024 según MapBiomas Colombia", "Sí (citando la fuente)"],
    ["Escenas limpias independientes confirman la tendencia: 10,7 km² (2003) → ~4,4 km² (2024–2026)", "Sí"],
    ["Sentinel-2 y Landsat coinciden el mismo día (2–4 %)", "Sí"],
    ["La ceniza oculta el glaciar en temporada seca; el NDSI mide hielo visible", "Sí (evidencia visual y cuantitativa)"],
    ["La temperatura de la región sube ~0,1 °C por década", "Sí (ERA5-Land, celda de 9 km)"],
    ["El Niño hace al Ruiz más cálido y más seco", "Sí"],
    ["El Niño acelera la pérdida de hielo", "No demostrado (sugestivo)"],
    ["MapBiomas se equivoca en 2023", "No"],
    ["La isoterma de 0 °C subió X m (medido)", "No: es una estimación"],
    ["El ML detecta hielo bajo ceniza", "No: no generaliza fuera de la geometría conocida"],
    ["Cifra del IDEAM", "No citar hasta leer el documento original"],
], [12, 4])

# =============================== 14. PRÓXIMOS ===============================
h1("15. Próximos pasos")
bullets([
    "<b>Revisión del autor</b> de los contornos en QGIS (editar 2021 y 2023; confirmar confianza).",
    "<b>Machine Learning v2 para hielo bajo ceniza:</b> radar Sentinel-1, variables multitemporales, etiquetas independientes "
    "del hielo cubierto y prueba de transferencia a otro glaciar (Santa Isabel, Tolima).",
    "<b>Densificar 2017–2026</b> con Sentinel-2 a 10 m y contornos en fechas sin ceniza ni nieve fresca.",
    "<b>Páramo:</b> NDVI por franjas de altitud de 100 m.",
    "<b>Hidrología:</b> MapBiomas Agua y caudales del IDEAM (DHIME).",
    "<b>Verificaciones pendientes:</b> licencia de MapBiomas, cifras del IDEAM en el PDF original, referencias bibliográficas.",
    "<b>Repositorio GitHub</b> con este informe, scripts y datos procesados.",
])

# =============================== 15. REPRODUCIBILIDAD ===============================
h1("16. Reproducibilidad")
p("Entorno: Google Earth Engine (Code Editor, JavaScript); QGIS 4.0.2 con Python 3.12 (GDAL, NumPy, pandas, SciPy, Matplotlib, "
  "Pillow, ReportLab); Windows 11. Todos los scripts están en la carpeta del proyecto; los scripts de Python se ejecutan con:")
S.append(Paragraph('"C:\\Program Files\\QGIS 4.0.2\\bin\\python-qgis.bat" nevados\\python\\&lt;script&gt;.py', st["code"]))
tabla([
    ["Orden", "Script", "Entrada", "Salida"],
    ["1", "gee/03_mapbiomas_y_galeria.js", "Assets públicos GEE", "Serie MapBiomas; galería"],
    ["2", "gee/04_descargas_para_qgis.js", "IDs de escenas seleccionadas", "Enlaces GeoTIFF → data/raw/"],
    ["3", "python/crear_proyecto_qgis.py", "data/raw/", "qgis/nevados_ruiz.qgz"],
    ["4", "python/delinear_semiauto.py", "data/raw/", "contornos_semiauto.gpkg; CSV de áreas"],
    ["5", "gee/05_sentinel2_serie_y_galeria.js", "Assets públicos GEE", "Serie S2; galería"],
    ["6", "gee/06_clima_mensual.js + data/raw/clima/oni_noaa_cpc.txt", "Assets GEE; NOAA", "Clima anual"],
    ["7", "python/analisis_clima_glaciar.py", "CSV procesados", "Figura y estadísticas"],
    ["8", "python/piezas_comunicacion.py", "Contornos y figuras", "Timelapse, carrusel"],
    ["9", "gee/07_descargas_ml_termico.js", "IDs de escenas Landsat 8/9", "Enlaces GeoTIFF con térmico → data/raw/ml/"],
    ["10", "python/ml_hielo_bajo_ceniza.py", "data/raw/ml/; contornos", "Métricas, importancia, figura ML"],
    ["11", "python/informe_metodologia.py", "Todo lo anterior", "Este informe"],
], [1.3, 6.2, 4.2, 4.5])

# =============================== 16. REFERENCIAS ===============================
h1("17. Fuentes y referencias")
p("<b>Fuentes de datos y documentación consultadas en línea durante el proyecto:</b>")
bullets([
    "MapBiomas Colombia — Código de la leyenda, Colección 3: colombia.mapbiomas.org/wp-content/uploads/sites/3/2025/10/Codigo-de-la-Leyenda-coleccion-3.pdf",
    "MapBiomas Colombia — Apéndice Glaciares y Nivales, Colección 3: colombia.mapbiomas.org/wp-content/uploads/sites/3/2025/10/Apendice_Glaciares_y_Nivales_Coleccion_3.pdf",
    "MapBiomas Colombia — Ficha técnica Glaciar y Nival C3: colombia.mapbiomas.org/wp-content/uploads/sites/3/2025/11/FactSheet-Glaciar-y-Nival-C3-Colombia.pdf",
    "MapBiomas Colombia — Herramientas (IDs de assets): colombia.mapbiomas.org/en/herramientas/",
    "RGI 7.0 — Guía de usuario (licencia CC BY 4.0): glims.org/rgi_user_guide/welcome.html",
    "NOAA CPC — Oceanic Niño Index: cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
    "Minambiente — \"Colombia está perdiendo sus glaciares: solo quedan 33 km²\" (referencia contextual nacional).",
])
p("<b>Literatura metodológica (citada de memoria; verificar antes de una publicación formal):</b>")
bullets([
    "Dozier, J. (1989). Spectral signature of alpine snow cover from the Landsat Thematic Mapper. <i>Remote Sensing of Environment</i>, 28, 9–22.",
    "Paul, F. et al. (2013). On the accuracy of glacier outlines derived from remote-sensing data. <i>Annals of Glaciology</i>, 54(63).",
    "Olofsson, P. et al. (2014). Good practices for estimating area and assessing accuracy of land change. <i>Remote Sensing of Environment</i>, 148, 42–57.",
    "Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. <i>Journal of the American Statistical Association</i>, 63, 1379–1389.",
    "Pasquarella, V. J. et al. (2023). Comprehensive quality assessment of optical satellite imagery using weakly supervised video learning (Cloud Score+). CVPR Workshops.",
])

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
                        title="Nevado del Ruiz — Informe metodológico", author="ANTARES Geospatial Lab")
doc.build(S, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
print("PDF:", OUT)
