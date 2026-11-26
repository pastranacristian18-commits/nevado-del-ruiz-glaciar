"""
ANTARES Geospatial Lab · Project #1 Nevados
Builds reports/methodology_report_nevado_del_ruiz_en.pdf (English methodology report).
Run with QGIS's Python (includes reportlab):
  "C:\\Program Files\\QGIS 4.0.2\\bin\\python-qgis.bat" nevados\\python\\methodology_report_en.py
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
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

R = Path(__file__).resolve().parents[1]
FIG, P = R / "reports" / "figuras", R / "data" / "processed"
OUT = R / "reports" / "methodology_report_nevado_del_ruiz_en.pdf"

F = r"C:\Windows\Fonts"
for n, f in [("S", "segoeui"), ("S-B", "segoeuib"), ("S-I", "segoeuii"), ("S-BI", "segoeuiz")]:
    pdfmetrics.registerFont(TTFont(n, f"{F}\\{f}.ttf"))
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
    estilo = [("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#bbbbbb")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fb")])]
    if cab:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), AZ))
    t.setStyle(TableStyle(estilo))
    S.append(t); S.append(Spacer(1, 8))


def figura(ruta, ancho_cm, pie):
    w, h = PILImage.open(ruta).size
    S.append(KeepTogether([Image(str(ruta), width=ancho_cm * cm, height=ancho_cm * cm * h / w), Paragraph(pie, st["c"])]))


def pie_pagina(canv, doc):
    canv.saveState(); canv.setFont("S", 7.5); canv.setFillColor(colors.HexColor("#777"))
    canv.drawString(2 * cm, 1.2 * cm, "ANTARES Geospatial Lab · Nevado del Ruiz — Methodology report v1 (Nov 2026)")
    canv.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}"); canv.restoreState()


# =============================== COVER ===============================
S += [Spacer(1, 4 * cm), Paragraph("Nevado del Ruiz:<br/>40 Years of Glacier, Volcanic Ash and Climate", st["t"]), Spacer(1, 0.6 * cm),
      Paragraph("Detailed methodology report — what was done, how, what failed, and what can be claimed", st["st"]), Spacer(1, 1.2 * cm)]
figura(FIG / "before_after_2003_2024_en.png", 16, "Glacier outline in 2003 (white) and 2024 (red) over Landsat 7/8 false colour.")
S += [Spacer(1, 1 * cm), Paragraph("ANTARES Geospatial Lab · Project #1 Nevados<br/>Author: Cristian Pastrana<br/>"
                                    "Version 1 · November 2026 · Maturity level: N1 (100 % open data)", st["st"]), PageBreak()]

# =============================== 1. SUMMARY ===============================
h1("1. Summary")
p("This report documents, step by step, the first project of ANTARES Geospatial Lab: an analysis of glacier area on "
  "Nevado del Ruiz volcano (Colombia) from 1985 to 2026 using open satellite and climate data. The initial goal was to build an "
  "automatic annual glacier-area series from Landsat and relate it to El Niño. That goal, as framed, <b>failed</b>: three versions "
  "of an automatic algorithm produced physically impossible series. Diagnosing why led to the project's most interesting result: "
  "on Ruiz, <b>volcanic ash hides the glacier</b> in the dry season and <b>fresh snow inflates it</b> in the wet season, so "
  "automatic NDSI-based methods measure <i>visible ice</i>, not necessarily <i>glacier extent</i>.")
p("The final workflow combined: (1) the official MapBiomas Colombia Collection 3 series as a series to audit; (2) visual selection "
  "of clean Landsat scenes using a criterion independent of the cloud mask; (3) semi-automatic outlines with sensitivity analysis and "
  "visual review; (4) a dense Sentinel-2 series with Cloud Score+ and cross-sensor validation; (5) an exploratory analysis of "
  "climate (ERA5-Land, CHIRPS) and El Niño (NOAA ONI); and (6) a machine-learning experiment to map ice under ash.")
box("<b>Key results.</b> (a) MapBiomas records 14.73 km² of glacier in 1985 and 3.68 km² in 2024 (−75 %); the official IDEAM "
    "inventory records 18.7 km² in the 1980s and 7.17 ± 0.30 km² in 2024 (−62 %). "
    "(b) Our outlines on high-confidence scenes give 10.71 km² (2003), 6.36 km² (2017), 4.35 km² (2024) and 4.50 km² (2026); "
    "they differ from MapBiomas by −10 % to +18 %. (c) On the same day, Sentinel-2 and Landsat agree within 2–4 %. "
    "(d) In the dry season visible ice drops to ~0.5–1.5 km² and returns to ~3–4 km² months later: this is ash, not loss. "
    "(e) Temperature in the ERA5-Land cell rises +0.10 °C per decade (p = 0.005); El Niño makes Ruiz warmer (ρ = +0.54) "
    "and drier (ρ = −0.53). (f) A direct El Niño → ice-loss link is suggestive (ρ = −0.30; p = 0.06) but <b>not</b> conclusive. "
    "(g) A machine-learning model reached F1 = 0.88 with leave-one-scene-out validation but fell to ≈ 0.25 (same as NDSI) with "
    "leave-one-sector-out: the apparent skill was spatial leakage.")

# =============================== 2. QUESTION & AREA ===============================
h1("2. Research question and study area")
p("<b>Main question:</b> how much glacier area has Nevado del Ruiz lost since 1985, with what uncertainty, and how is that loss "
  "related to temperature, precipitation and El Niño?")
p("<b>Study area:</b> a 16 × 16 km window centred on the summit (4.895° N, 75.322° W; WGS84) inside Los Nevados National Natural Park. "
  "Area calculations used a 6 km radius around the summit and a minimum elevation of 4400 m (Copernicus DEM) to exclude occasional "
  "low-elevation snow. Ruiz is an active volcano, which conditions the whole optical analysis.")
p("<b>Working reference system:</b> UTM zone 18 North (EPSG:32618), 30 m pixels (Landsat, MapBiomas, DEM) and 10–20 m (Sentinel-2). "
  "Areas computed in the projection or with <i>ee.Image.pixelArea()</i> in Earth Engine.")

# =============================== 3. DATA ===============================
h1("3. Data")
p("Project rule: distinguish the processing already done by the provider from our own, and never re-apply corrections a product already includes.")
tabla([
    ["Source", "Resolution / period", "Provider processing", "What we did", "Licence / status"],
    ["Landsat 5, 7, 8, 9 Collection 2 Level 2 (USGS)", "30 m · 1985–2026", "Surface reflectance (atmospheric correction), QA_PIXEL band (Fmask)",
     "Scale factors (×0.0000275 − 0.2), NDSI, masks, scene selection, outlines", "USGS public domain (to verify)"],
    ["Landsat 8/9 Collection 2 TOA", "100 m (B10) · 2017–2026", "Top-of-atmosphere calibration", "Band 10 brightness temperature for ML", "USGS public domain (to verify)"],
    ["Sentinel-2 L2A Harmonized (ESA/Copernicus)", "10–20 m · 2017–2026", "Sen2Cor atmospheric correction; baseline 04.00 offset harmonised",
     "Daily mosaic, Cloud Score+ mask, NDSI, gallery", "Copernicus licence (free)"],
    ["Cloud Score+ S2 (Google)", "10 m", "Per-pixel quality score (trained model)", "Threshold cs_cdf ≥ 0.6 = clear", "Terms to verify"],
    ["MapBiomas Colombia Col. 3 — class 34 Glacier and snow", "30 m · 1985–2024", "Random Forest classification of Landsat mosaics, spatial and temporal filters",
     "Area series to audit; never used as truth", "Conflicting: CC-BY vs non-commercial (pending)"],
    ["Copernicus DEM GLO-30", "30 m", "Digital surface model", "Elevation thresholds (4400/4700 m), ring, ERA5 cell elevation, ML terrain features", "Copernicus DEM (attribution)"],
    ["ERA5-Land monthly (ECMWF)", "~9 km · 1981–2025", "Reanalysis", "2 m T, precipitation, snowfall; anomalies and trends", "Copernicus licence"],
    ["CHIRPS pentads (UCSB-CHC)", "~5 km · 1981–2025", "Satellite + stations", "Monthly and annual precipitation", "To verify"],
    ["ONI (NOAA CPC)", "Monthly · 1950–2026", "Official El Niño index", "Annual mean; El Niño year classification", "NOAA public domain"],
], [3.2, 2.3, 3.8, 4.0, 2.9])

# =============================== 4. WORKFLOW ===============================
h1("4. Overall workflow")
tabla([
    ["Step", "Tool", "Script / file", "Output"],
    ["1. Automatic Landsat series (v1, v2, v3)", "Earth Engine", "gee/01_*.js, gee/02_*.js", "Discarded series + diagnosis"],
    ["2. MapBiomas series + scene gallery", "Earth Engine", "gee/03_mapbiomas_y_galeria.js", "serie_mapbiomas_c3_ruiz.csv; 40 thumbnails"],
    ["3. Visual scene selection", "Visual review", "sampling/seleccion_escenas.md", "Categories A, A*, B, C"],
    ["4. GeoTIFF download", "Earth Engine + PowerShell", "gee/04_descargas_para_qgis.js", "11 scenes, MapBiomas 1985–2024, DEM"],
    ["5. QGIS project", "PyQGIS (QGIS 4.0.2)", "python/crear_proyecto_qgis.py", "qgis/nevados_ruiz.qgz"],
    ["6. Semi-automatic outlines", "GDAL/NumPy", "python/delinear_semiauto.py", "contornos_semiauto.gpkg; areas and ranges"],
    ["7. Sentinel-2 + Cloud Score+", "Earth Engine", "gee/05_sentinel2_serie_y_galeria.js", "serie_s2_hielo_limpio_ruiz.csv; gallery"],
    ["8. Climate and El Niño", "Earth Engine + SciPy", "gee/06_clima_mensual.js; python/analisis_clima_glaciar.py", "Annual table, figure, statistics"],
    ["9. Machine learning", "Earth Engine + scikit-learn/XGBoost", "gee/07_descargas_ml_termico.js; python/ml_hielo_bajo_ceniza.py", "Metrics, importance, ML figure"],
    ["10. Communication", "Matplotlib/PIL", "python/piezas_comunicacion.py", "Timelapse, before/after, carousel"],
], [4.6, 3.0, 5.0, 3.6])

# =============================== 5. PHASE 1 ===============================
h1("5. Phase 1 — Automatic Landsat series: three failed attempts")
p("The original plan was the classic baseline of glacier inventories: classify snow/ice with the <b>NDSI</b> (Normalized Difference "
  "Snow Index = (Green − SWIR1)/(Green + SWIR1)) at a 0.40 threshold, and compute area for each year.")
h2("5.1 Version 1 — annual 25th percentile of NDSI")
p("<b>Method.</b> Landsat 5, 7, 8 and 9 (C2 L2) were merged. Pixels flagged by Fmask as cloud, dilated cloud or shadow were masked. "
  "For each year the 25th percentile of NDSI was computed (to keep persistent ice rather than passing snowfalls), and ice was classified "
  "where NDSI > 0.40, green > 0.10, elevation > 4400 m and at least 3 valid observations. <i>Valid coverage</i> (fraction of the high "
  "zone with enough data) was also recorded.")
p("<b>Deliberate decision:</b> radiometric saturation was not masked, because Landsat 5/7 visible bands saturate over snow and masking "
  "them would have erased the glacier itself.")
p("<b>Result.</b> An impossible series: 4.24 km² in 2023 and 0.42 km² in 2024; almost every year in 1985–1994 at zero; valid coverage "
  "below 0.9 in 38 of 41 years.")
p("<b>Diagnosis.</b> (a) Fmask flags bright ice as cloud and dilates the mask, erasing the glacier; (b) the 25th percentile picks the "
  "dirtiest dates (shadows, ash, residual clouds); (c) coverage was measured over the whole > 4400 m zone rather than where glacier actually is.")
h2("5.2 Version 2 — annual snow frequency")
p("<b>Changes.</b> Only high-confidence clouds (QA_PIXEL bits 8–9) and shadows were masked, without dilation. A pixel was classified as "
  "glacier if it was snow/ice in ≥ 50 % of its valid observations in the year. Coverage was measured over the ≥ 4700 m zone, with a "
  "reliable-year flag (coverage ≥ 0.80).")
p("<b>Result.</b> Only 8 of 41 years were reliable, and still inconsistent: 14.55 km² in 2014, 7.59 km² in 2023, 1.53 km² in 2024. "
  "On the map, 2023 ice looked almost as large as 2001 ice.")
p("<b>Diagnosis.</b> With a looser mask, <b>ice clouds</b> (high NDSI, like snow) and <b>seasonal snowfall</b> were counted as glacier.")
h2("5.3 Version 3 — scene by scene (clear days only)")
p("<b>Changes.</b> Instead of annual composites, each scene was evaluated: clear fraction of the glacier zone (≥ 4700 m) according to "
  "Fmask (cloud, shadow, cirrus, fill). Only scenes ≥ 95 % clear were accepted; median, minimum and maximum were reported per year.")
p("<b>Result.</b> Of <b>2,102 Landsat scenes</b>, only <b>5</b> passed the filter, and two of them had zero area (scenes with missing "
  "reflectance not flagged by the QA band). The annual summary also failed with <i>User memory limit exceeded</i>.")
box("<b>Phase 1 conclusion.</b> Fmask is not usable over the Ruiz glacier: it confuses ice with cloud and cloud with ice, and cloud "
    "cover is almost permanent. Tuning thresholds does not fix it. A fully automatic Landsat pipeline does not work on this mountain. "
    "This negative result is kept on record (gee/01_serie_glaciar_landsat_v1_descartado.js, gee/01_serie_glaciar_landsat.js, "
    "gee/02_escenas_despejadas.js).", "warn")

# =============================== 6. MAPBIOMAS ===============================
h1("6. Phase 2 — MapBiomas Colombia series (Collection 3)")
p("<b>Why.</b> MapBiomas had already tackled much of the problem with minimum-NDSI mosaics, Random Forest classification, temporal "
  "filters and expert review (Collection 3 glacier methodology appendix). It was treated as <b>a series to audit, not as truth</b>.")
p("<b>Method.</b> Asset <i>projects/mapbiomas-colombia/assets/LULC/COLECCION3/INTEGRACION/COLOMBIA-1</i> (one band per year, 1985–2024). "
  "Class 34 area was computed for all bands with a single spatial reduction (avoiding the memory error). The 2024 value (3.679 km²) "
  "matches the 367.9 ha reported in MapBiomas' fact sheet for Ruiz, which confirms the study area is correctly delimited.")
mb = pd.read_csv(P / "serie_mapbiomas_c3_ruiz.csv")
sel = mb[mb["anio"].isin([1985, 1990, 1991, 1995, 2000, 2005, 2010, 2013, 2014, 2015, 2020, 2021, 2022, 2023, 2024])]
pares = [(str(a), f"{v:.2f}") for a, v in zip(sel["anio"], sel["area_km2_mapbiomas"])]
filas = [["Year", "km²", "Year", "km²", "Year", "km²"]]
for i in range(5):
    fila = []
    for k in range(3):
        fila += list(pares[i + 5 * k])
    filas.append(fila)
tabla(filas, [1.6, 1.6] * 3)
p("<b>Critical observations.</b> (a) The series is almost monotonic, indicating temporal filters (not an error, but it must be stated); "
  "(b) there are abrupt drops in 1990→1991 (−1.96 km²), 2013→2014 (−0.84 km²) and 2021→2023 (−2.47 km²) that coincide with periods of "
  "volcanic activity; (c) the comparison with the official IDEAM inventory is presented in Section 12.")

# =============================== 7. VISUAL SELECTION ===============================
h1("7. Phase 3 — Visual selection of Landsat scenes")
p("<b>A criterion independent of Fmask.</b> A <b>ring</b> of rock and páramo between 4200 and 4700 m around the glacier was defined. "
  "A scene is a candidate if at least 60 % of the ring is \"dark\" (blue < 0.15, i.e. cloud-free). Scenes were pre-filtered to "
  "CLOUD_COVER < 70 %, and Landsat 7 after May 2003 was excluded (scan-line corrector failure, SLC-off). The best 40 candidates were "
  "viewed in SWIR1-NIR-Green false colour (clean ice = cyan, cloud = white).")
figura(FIG / "hoja_contactos_candidatas.png", 16.5, "Figure 1. Gallery of 40 candidate scenes (Landsat 5, 7, 8 and 9). In almost every "
       "dry-season scene since 2014 the glacier appears covered by ash (dull blue-grey).")
tabla([
    ["Category", "Criterion", "Scenes", "Use"],
    ["A — clean ice", "No obvious fresh snow or ash", "2001-01-12, 2002-10-14, 2003-01-02, 2017-12-18, 2021-12-13, 2023-06-18, 2024-08-15, 2026-05-09", "Outlines (reference)"],
    ["A* — with caveats", "Partial ash, scene edge or nearby clouds", "1987-01-14, 1997-10-24, 2026-07-28", "Outlines with uncertainty"],
    ["B — fresh snow", "Inflated area", "2001-01-28, 2015-09-24, 2016-07-08, 2023-09-06", "Seasonal variability"],
    ["C — ash", "Darkened ice; NDSI underestimates it", "2014-12-26, 2020-01-09, 2022-01-30, 2023-01-25, 2023-12-03, 2024-01-04, 2025-01-14, 2025-01-22", "ML test cases"],
], [2.6, 3.6, 7.2, 2.8])
p("<b>Gaps:</b> no candidates in 1988–1996 or 2004–2013 (sparse Landsat 5 coverage over Colombia and exclusion of Landsat 7 SLC-off). "
  "<b>Later note:</b> when the outlines were reviewed, some category-A scenes turned out to contain fresh snow (2001, 2021, 2026-05); "
  "their confidence was downgraded (Section 8).")

# =============================== 8. OUTLINES ===============================
h1("8. Phase 4 — Semi-automatic outlines and MapBiomas audit")
p("<b>Download.</b> The 11 A/A* scenes, the MapBiomas 1985–2024 stack (40 bands) and the DEM were downloaded as GeoTIFF (UTM 18N, 30 m) "
  "through direct <i>getDownloadURL</i> links and checked with <i>gdalinfo</i> (bands, projection and value ranges).")
p("<b>Method (\"band ratio + correction\" type, as used in GLIMS/RGI inventories).</b> For each scene: NDSI > 0.40; green > 0.10; "
  "elevation > 4400 m; distance ≤ 6 km from the summit; removal of patches smaller than 5 pixels (0.45 ha) with <i>gdal.SieveFilter</i>; "
  "vectorisation with <i>gdal.Polygonize</i>; area in UTM. <b>Sensitivity:</b> repeated with thresholds 0.30 and 0.50 to obtain a range. "
  "<b>Visual review:</b> each outline was overlaid on the image and given a confidence level (high, medium, low, discard).")
figura(FIG / "control_contornos_hoja.png", 15.5, "Figure 2. Semi-automatic outlines (red) on each scene. 1987: ash to the west not detected. "
       "1997: cut-off scene. 2001 and 2021: fresh snow included.")
a = pd.read_csv(P / "areas_semiauto_vs_mapbiomas.csv")
conf = {"1987-01-14": "medium", "1997-10-24": "discard", "2001-01-12": "low", "2002-10-14": "medium", "2003-01-02": "high",
        "2017-12-18": "high", "2021-12-13": "low", "2023-06-18": "medium", "2024-08-15": "high", "2026-05-09": "low", "2026-07-28": "high"}
f = [["Date", "Cat.", "NDSI 0.40 area (km²)", "Range 0.50–0.30", "MapBiomas same year", "Diff.", "Confidence"]]
for _, r in a.iterrows():
    mbv = r["mapbiomas_km2_mismo_anio"]
    dif = "" if pd.isna(mbv) or conf[r["fecha"]] == "discard" else f"{100 * (r['area_km2_ndsi040'] / mbv - 1):+.0f} %"
    f.append([r["fecha"], r["categoria"], f"{r['area_km2_ndsi040']:.2f}", f"{r['area_km2_ndsi050']:.2f}–{r['area_km2_ndsi030']:.2f}",
              "" if pd.isna(mbv) else f"{mbv:.2f}", dif, conf[r["fecha"]]])
tabla(f, [2.2, 1.0, 2.6, 2.8, 2.8, 1.5, 2.2])
box("<b>Reading.</b> On high-confidence scenes the difference with MapBiomas ranges from −10 % to +18 %. The bias depends on the glacier "
    "surface, not on the method: ash causes underestimation (1987) and fresh snow overestimation (2001, 2021, 2026-05). Using only "
    "high-confidence scenes: 10.71 km² (2003) → 4.35 km² (2024), a loss of ~59 % in 21 years.")
p("<b>Important limitation:</b> the outlines are semi-automatic and the visual review was preliminary; the author must review and edit them "
  "in QGIS so that the interpreter's judgement is documented. There was no second independent interpreter.")

# =============================== 9. SENTINEL-2 ===============================
h1("9. Phase 5 — Sentinel-2 with Cloud Score+")
p("<b>Why.</b> Landsat did not have enough clean scenes to understand the MapBiomas drop in 2023. Sentinel-2 revisits every ~5 days at 10 m in the visible.")
p("<b>Method.</b> S2 L2A Harmonized collection 2017–2026 with CLOUDY_PIXEL_PERCENTAGE < 80; linked to Cloud Score+ (cs_cdf band); "
  "one mosaic per day (the volcano can fall on two tiles); a pixel is clear if cs_cdf ≥ 0.6 (no-data pixels count as not clear). Days with "
  "≥ 90 % of the glacier zone clear were accepted, and clean-ice area (NDSI > 0.40, green > 0.10, > 4400 m) was measured at 20 m. "
  "For June 2022 – June 2024 a true-colour and false-colour gallery was produced.")
p("<b>Result.</b> 359 days with imagery; 25 days accepted.")
tabla([
    ["Date", "Sentinel-2 (km²)", "Landsat same day (km²)", "Difference"],
    ["2024-08-15", "4.245", "4.350 (Landsat 8)", "−2.4 %"],
    ["2026-05-09", "5.628", "5.826 (Landsat 9)", "−3.4 %"],
    ["2026-07-28", "4.323", "4.501 (Landsat 9)", "−4.0 %"],
], [3, 3.5, 4.5, 3])
p("<b>Dry-season clean-ice series:</b> 3.1–3.7 km² (January 2020) → 1.5 km² (January 2023) → 0.9–1.1 km² (January 2024) → 0.5 km² "
  "(January 2025). Yet in August 2024 and July/August 2026 it returns to 3.0–4.3 km². In October 2022 a widespread snowfall gave "
  "41.8 km² (not glacier).")
figura(FIG / "s2_periodo_critico.png", 16.5, "Figure 3. Sentinel-2, critical period. Top: true colour (ash appears grey). Bottom: "
       "SWIR1-NIR-Green false colour (ice under ash appears dull blue-green with the glacier's shape). The red pixel in the crater is "
       "probably a thermal anomaly (not verified).")
box("<b>Interpretation.</b> A glacier does not lose 85 % of its area and regain it within six months. In the dry season the glacier is "
    "covered by ash: the ice is still there, but NDSI does not detect it. On Ruiz, NDSI-based methods therefore measure visible ice. "
    "<b>However</b>, MapBiomas' 2023 value (3.77 km²) is similar to ours for August 2024 (4.2–4.35 km²), so <b>we cannot claim MapBiomas "
    "is wrong</b>; much of the drop may be real.")

# =============================== 10. CLIMATE ===============================
h1("10. Phase 6 — Climate and El Niño")
p("<b>Data.</b> Monthly ERA5-Land (2 m temperature, precipitation, snowfall) in the ~9 km cell containing the summit; CHIRPS precipitation "
  "averaged over a 6 km radius; NOAA ONI (annual mean of the 12 overlapping seasons). <b>Estimated 0 °C isotherm</b> = mean cell elevation "
  "(4283 m, from the Copernicus DEM) + T / 0.0065 (fixed lapse rate of 6.5 °C/km): an approximation, not a measurement.")
p("<b>Statistical methods.</b> Trends with Mann-Kendall and Sen's slope (95 % CI); Spearman correlations; El Niño years (annual ONI ≥ 0.5) "
  "versus the rest with a one-sided Mann-Whitney test. Analysis in Python (SciPy).")
tabla([
    ["Variable", "Trend (Sen) per decade", "95 % CI", "p (MK)"],
    ["2 m temperature", "+0.10 °C", "+0.04 to +0.18", "0.005"],
    ["Estimated 0 °C isotherm", "+16 m", "+6 to +28", "0.005"],
    ["ERA5-Land snowfall", "−1.5 mm", "−3.3 to −0.4", "0.011"],
    ["CHIRPS precipitation", "+42 mm", "−10 to +103", "0.11"],
    ["MapBiomas glacier area", "−2.15 km²", "−2.45 to −1.84", "< 0.001"],
], [5, 4, 3.5, 2.5])
tabla([
    ["Relationship (Spearman)", "ρ", "p", "n", "Reading"],
    ["ONI vs temperature", "+0.54", "< 0.001", "45", "El Niño = warmer"],
    ["ONI vs CHIRPS precipitation", "−0.53", "< 0.001", "45", "El Niño = drier"],
    ["ONI vs snowfall", "−0.33", "0.027", "45", "El Niño = less snow"],
    ["ΔArea vs ONI", "−0.30", "0.062", "39", "Suggestive, not significant"],
    ["ΔArea vs temperature", "−0.28", "0.084", "39", "Suggestive, not significant"],
    ["ΔArea El Niño vs rest (Mann-Whitney)", "−0.25 vs −0.12 km²/yr", "0.096", "8 / 31", "Suggestive, not significant"],
], [5, 3.3, 1.8, 1.5, 4.4])
figura(FIG / "glacier_climate_el_nino_en.png", 13.5, "Figure 4. Glacier area (MapBiomas and this study's clean scenes), annual ONI, "
       "ERA5-Land temperature with estimated 0 °C isotherm, and CHIRPS precipitation anomaly, 1981–2026.")
p("<b>Why the glacier signal is weak:</b> (a) MapBiomas is temporally smoothed; (b) large drops coincide with volcanic activity, which mixes "
  "real loss with ash; (c) n ≈ 40 years and autocorrelated series (p-values are optimistic); (d) a 9 km cell does not represent the summit, "
  "hence the use of anomalies and trends.")
p("<b>Current context:</b> the August–October 2026 ONI is +2.46 (strong El Niño under way according to NOAA).")

# =============================== 11. ML ===============================
h1("11. Phase 7 — Machine learning: ice under ash?")
p("<b>Question.</b> Can machine-learning models with spectral, thermal and terrain features detect the glacier when it is covered by ash, where NDSI fails?")
p("<b>Data.</b> Nine Landsat 8/9 scenes downloaded with <i>gee/07_descargas_ml_termico.js</i>: six surface-reflectance bands and the band-10 "
  "brightness temperature (100 m native, delivered at 30 m). Five ash scenes (2020-01, 2023-12, 2024-01, 2025-01 ×2) and four clean scenes "
  "(2017-12, 2023-06, 2024-08, 2026-07). Physical hypothesis: ice under ash stays near 0 °C, while rock warms up.")
p("<b>Labels.</b> Semi-automatic outline from a clean scene: its own for clean scenes, and the 2024-08-15 outline for ash scenes (5–8 months apart). "
  "A 60 m band on each side of the boundary was excluded. The 2020 scene has no nearby outline and was only used to apply the model.")
p("<b>Features.</b> S = spectral (six bands, NDSI, NDWI, red/SWIR1 ratio, brightness, NIR texture); ST = S + thermal anomaly (B10 minus the "
  "scene median); STT = ST + elevation, slope and aspect. <b>Models:</b> NDSI > 0.40 (baseline), logistic regression, Random Forest (200 trees) "
  "and XGBoost (300 trees), with balanced sampling of 8000 pixels per scene and a fixed seed.")
p("<b>Validation.</b> (A) Leave one scene out. (B) Leave one sector out: the area was split into four quadrants around the summit (300 m margin); "
  "each quadrant was predicted by a model that never saw it in any scene, and the four predictions were merged into a full map for evaluation. "
  "A first version averaged F1 per sector and was biased because the north and west sectors hold almost no ice in 2024; this was corrected.")
tabla([
    ["Model", "Features", "F1 (A: scene out)", "F1 (B: sector out)", "Area error (B)"],
    ["NDSI > 0.40", "—", "0.28", "0.25", "−86 %"],
    ["XGBoost", "S", "0.60", "0.25", "−14 %"],
    ["XGBoost", "ST", "0.61", "0.21", "+3 %"],
    ["XGBoost", "STT", "0.88", "0.26", "−32 %"],
    ["Random Forest", "STT", "0.85", "0.27", "−28 %"],
    ["Logistic regression", "STT", "0.74", "0.34", "−17 %"],
], [3.4, 2.0, 3.6, 3.6, 3.4])
p("<b>Permutation importance</b> (Random Forest STT, tested on 2024-01-04, drop in F1): elevation 0.29; thermal anomaly 0.065; red/SWIR1 0.063; "
  "slope 0.04; the rest ≈ 0.")
figura(FIG / "ml_ice_under_ash_en.png", 16.5, "Figure 5. Ash scenes: image, NDSI baseline, XGBoost with thermal and terrain (leave-one-scene-out) "
       "and XGBoost with thermal (leave-one-sector-out). Red: reference outline; cyan: prediction.")
box("<b>Interpretation.</b> The F1 of 0.88 is largely <b>spatial information leakage</b>: all ash scenes share the same reference and the most "
    "important feature is elevation, so the model learns <i>where</i> the glacier is, not <i>what</i> ash-covered ice looks like. When the sector "
    "was not seen during training, every model drops to F1 ≈ 0.2–0.3, the baseline level: they estimate total area better but place the ice in "
    "the wrong locations. The thermal band adds little. <b>With these data, machine learning does not solve the problem in a generalisable way.</b> "
    "The application to 2020-01-09 (models 5.7–7.0 km² versus 2.79 km² for NDSI and 6.32 km² for MapBiomas) is not considered a reliable estimate.", "warn")
p("<b>Next iteration:</b> independent labels for covered ice (high-resolution imagery or field data), Sentinel-1 radar, multi-temporal features "
  "(change since the last clean scene) and a transfer test on another glacier (Santa Isabel, Tolima).")

# =============================== 12. IDEAM ===============================
h1("12. Phase 8 — Comparison with the official IDEAM glacier inventory")
p("<b>Sources read in the original PDFs.</b> IDEAM (Colombia's national hydro-meteorological institute), <i>State of Colombian Glaciers "
  "report 2023</i>, Table 17 (Ruiz series up to 2022), and <i>2024 report</i>, Table 1 and text: Ruiz glacier area on 20 February 2024 was "
  "<b>7.17 ± 0.30 km²</b> (PlanetScope imagery). The same report states that <b>about 88 % of the glacier surface was covered by volcanic "
  "ash in 2024</b>, that ash thicker than 5 cm acts as thermal insulation, and that the largest retreat occurred in the southern sector, "
  "where there was less ash.")
tabla([
    ["Year", "IDEAM (km²)", "MapBiomas (km²)", "IDEAM / MapBiomas", "This study, clean ice (km²)"],
    ["1980s", "18.7", "14.73 (1985)", "1.27", "—"],
    ["1990s", "14.1", "10.65 (1995)", "1.32", "—"],
    ["2010", "10.3", "9.36", "1.10", "—"],
    ["2017", "8.88", "7.12", "1.25", "6.36"],
    ["2020", "8.14", "6.32", "1.29", "—"],
    ["2022", "7.68", "5.19", "1.48", "—"],
    ["2024", "7.17 ± 0.30", "3.68", "1.95", "4.35 (August)"],
], [3.0, 2.6, 3.0, 3.2, 4.4])
figura(FIG / "ideam_comparison_en.png", 14.5, "Figure 6. Three ways to measure the same glacier: IDEAM (high resolution, includes ash-covered ice), "
       "MapBiomas (automatic Landsat classification) and this study (visible clean ice). Bottom: IDEAM/MapBiomas area ratio.")
box("<b>Reading.</b> All three sources agree on the trend but not on the magnitude. IDEAM always reports more area; the IDEAM/MapBiomas "
    "ratio stays at 1.1–1.3 until 2021, then rises to 1.48 in 2022 and <b>1.95 in 2024</b>, the year with ~88 % of the glacier under ash. "
    "This is an <b>official, independent confirmation</b> of the project's central finding: spectral methods measure visible ice, and ash "
    "widens the gap. In 2024 the difference from our clean-ice area (7.17 vs 4.35 km²) is ~2.8 km², consistent with the earlier estimate "
    "of ~3 km² hidden by ash. The 1.27–1.32 ratio in the 1980s and 1990s shows that resolution, glacier definition and image dates also "
    "matter, not only ash.")
p("<b>Adjusted claims.</b> Loss since the 1980s is <b>~62 % according to IDEAM</b> (18.7 → 7.17 km²) and ~75 % according to MapBiomas "
  "(1985–2024); the MapBiomas figure is inflated in recent years by ash. Given the official 2024 figure, it is reasonable to state that "
  "MapBiomas underestimates glacier extent in 2022–2024.")

# =============================== 12. FAILURES ===============================
h1("13. Complete log of what failed")
tabla([
    ["#", "What failed", "Cause", "How it was resolved / status"],
    ["1", "Impossible v1 series (25th percentile)", "Fmask erases ice; percentile picks dirty dates", "Discarded and documented"],
    ["2", "Inconsistent v2 series (frequency)", "Ice clouds and fresh snow with high NDSI", "Discarded and documented"],
    ["3", "v3 series: 5 of 2,102 scenes accepted", "Fmask unusable over the glacier; cloud cover", "Change of approach: visual selection"],
    ["4", "Zero areas in \"clear\" scenes", "QA band did not flag pixels without valid reflectance", "Identified; independent ring criterion"],
    ["5", "User memory limit exceeded", "Year-by-year reductions in the browser", "Single multi-band reduction; exports"],
    ["6", "MapBiomas asset: type 'Image' vs 'IMAGE'", "API format change", "Case-insensitive comparison"],
    ["7", "Cloud Score+ 'not found'", "Typo in the asset ID (underscore instead of slash)", "Fixed: GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED"],
    ["8", "ERA5 cell elevation: too many pixels", "reduceResolution exceeds 65,535 pixels", "Computed locally from the DEM"],
    ["9", "Unrealistic ERA5-Land precipitation (6000–9900 mm/yr)", "Known reanalysis bias in complex terrain", "CHIRPS used for rainfall"],
    ["10", "Automatic copy of scripts into the Code Editor", "The browser did not share the clipboard", "Manual paste (Ctrl+V)"],
    ["11", "Python error (GDAL object released)", "Temporary dataset collected by the garbage collector", "Explicit reference to the dataset"],
    ["12", "Direct CSV download from the browser", "Blocked by the environment", "Annual aggregation extracted as text"],
    ["13", "ML with F1 = 0.88 that does not generalise", "Spatial leakage: same reference and elevation as dominant feature", "Detected with sector validation; documented"],
    ["14", "Biased v1 sector validation", "Per-sector F1 average with nearly ice-free sectors", "Out-of-sector predictions merged and evaluated together"],
    ["15", "Feature importance: parallel worker crashed", "Child processes could not find the local libraries", "Computed in a single process"],
], [0.9, 4.2, 5.1, 5.6])

# =============================== 13. LIMITATIONS ===============================
h1("14. Limitations and uncertainty")
bullets([
    "The dominant uncertainty is the <b>glacier surface</b> (ash and fresh snow), not the sensor or the pixel.",
    "Semi-automatic outlines with a single preliminary visual review; a detailed review by the author and a second interpreter are missing.",
    "Temporal gaps in clean scenes: 1988–1996 and 2004–2013.",
    "30 m resolution is coarse for a ~4 km² glacier; edge error may be significant.",
    "MapBiomas: conflicting licence information and temporal filters not quantified by us.",
    "ERA5-Land at ~9 km; isotherm estimated with a fixed lapse rate; ERA5 precipitation not reliable here.",
    "Exploratory statistics: small n and autocorrelation; correlation does not imply causation.",
    "Machine-learning labels for ash scenes come from a different date (5–8 months); only one reference outline.",
    "No field data (Level 2): no figure is calibrated with in-situ measurements.",
    "The literature references in Section 18 are cited from memory and must be verified before formal publication.",
])

# =============================== 14. CLAIMS ===============================
h1("15. What can and cannot be claimed")
tabla([
    ["Claim", "Status"],
    ["Ruiz lost ~75 % of its glacier area between 1985 and 2024 according to MapBiomas Colombia", "Yes (citing the source)"],
    ["Independent clean scenes confirm the trend: 10.7 km² (2003) → ~4.4 km² (2024–2026)", "Yes"],
    ["Sentinel-2 and Landsat agree on the same day (2–4 %)", "Yes"],
    ["Ash hides the glacier in the dry season; NDSI measures visible ice", "Yes (visual and quantitative evidence)"],
    ["Regional temperature rises ~0.1 °C per decade", "Yes (ERA5-Land, 9 km cell)"],
    ["El Niño makes Ruiz warmer and drier", "Yes"],
    ["El Niño accelerates ice loss", "Not demonstrated (suggestive)"],
    ["MapBiomas underestimates glacier extent in 2022–2024 because of ash", "Yes, reasonable (IDEAM 2024: 7.17 km², 88 % under ash)"],
    ["Loss since the 1980s is ~62 % (IDEAM) / ~75 % (MapBiomas)", "Yes, citing each source"],
    ["The 0 °C isotherm rose X m (measured)", "No: it is an estimate"],
    ["Machine learning detects ice under ash", "No: it does not generalise beyond the known geometry"],
    ["Ash hides the glacier (confirmed by IDEAM)", "Yes"],
], [12, 4])

# =============================== 15. NEXT STEPS ===============================
h1("16. Next steps")
bullets([
    "<b>Author review</b> of the outlines in QGIS (edit 2021 and 2023; confirm confidence levels).",
    "<b>Machine learning v2 for ice under ash:</b> Sentinel-1 radar, multi-temporal features, independent labels for covered ice, and a transfer "
    "test on another glacier (Santa Isabel, Tolima).",
    "<b>Densify 2017–2026</b> with 10 m Sentinel-2 outlines on dates without ash or fresh snow.",
    "<b>Páramo:</b> NDVI by 100 m elevation bands.",
    "<b>Hydrology:</b> MapBiomas Water and IDEAM river discharge (DHIME).",
    "<b>Pending checks:</b> MapBiomas licence and literature references.",
])

# =============================== 16. REPRODUCIBILITY ===============================
h1("17. Reproducibility")
p("Environment: Google Earth Engine (Code Editor, JavaScript); QGIS 4.0.2 with Python 3.12 (GDAL, NumPy, pandas, SciPy, Matplotlib, Pillow, "
  "ReportLab) plus scikit-learn 1.9 and XGBoost 3.4 installed in <i>.pylibs/</i>; Windows 11. Python scripts run with:")
S.append(Paragraph('"C:\\Program Files\\QGIS 4.0.2\\bin\\python-qgis.bat" nevados\\python\\&lt;script&gt;.py', st["code"]))
p("Figures in English are produced by setting the environment variable ANTARES_LANG=en before running the figure scripts.")
tabla([
    ["Order", "Script", "Input", "Output"],
    ["1", "gee/03_mapbiomas_y_galeria.js", "Public GEE assets", "MapBiomas series; gallery"],
    ["2", "gee/04_descargas_para_qgis.js", "Selected scene IDs", "GeoTIFF links → data/raw/"],
    ["3", "python/crear_proyecto_qgis.py", "data/raw/", "qgis/nevados_ruiz.qgz"],
    ["4", "python/delinear_semiauto.py", "data/raw/", "contornos_semiauto.gpkg; area CSV"],
    ["5", "gee/05_sentinel2_serie_y_galeria.js", "Public GEE assets", "S2 series; gallery"],
    ["6", "gee/06_clima_mensual.js + data/raw/clima/oni_noaa_cpc.txt", "GEE assets; NOAA", "Annual climate"],
    ["7", "python/analisis_clima_glaciar.py", "Processed CSV", "Figure and statistics"],
    ["8", "gee/07_descargas_ml_termico.js", "Landsat 8/9 scene IDs", "GeoTIFF links with thermal → data/raw/ml/"],
    ["9", "python/ml_hielo_bajo_ceniza.py", "data/raw/ml/; outlines", "Metrics, importance, ML figure"],
    ["10", "python/piezas_comunicacion.py", "Outlines and figures", "Timelapse, carousel, before/after"],
    ["11", "python/comparacion_ideam.py", "IDEAM and MapBiomas series", "Comparison table and figure"],
    ["12", "python/informe_metodologia.py · python/methodology_report_en.py", "All of the above", "Spanish and English reports"],
], [1.3, 6.2, 4.2, 4.5])

# =============================== 17. REFERENCES ===============================
h1("18. Sources and references")
p("<b>Data sources and documentation consulted online during the project:</b>")
bullets([
    "MapBiomas Colombia — Legend codes, Collection 3: colombia.mapbiomas.org/wp-content/uploads/sites/3/2025/10/Codigo-de-la-Leyenda-coleccion-3.pdf",
    "MapBiomas Colombia — Glacier and snow appendix, Collection 3: colombia.mapbiomas.org/wp-content/uploads/sites/3/2025/10/Apendice_Glaciares_y_Nivales_Coleccion_3.pdf",
    "MapBiomas Colombia — Glacier and snow fact sheet C3: colombia.mapbiomas.org/wp-content/uploads/sites/3/2025/11/FactSheet-Glaciar-y-Nival-C3-Colombia.pdf",
    "MapBiomas Colombia — Tools (asset IDs): colombia.mapbiomas.org/en/herramientas/",
    "RGI 7.0 — User guide (CC BY 4.0 licence): glims.org/rgi_user_guide/welcome.html",
    "NOAA CPC — Oceanic Niño Index: cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
    "Colombian Ministry of Environment — \"Colombia is losing its glaciers: only 33 km² remain\" (national context).",
    "IDEAM (2023). Informe del estado de los glaciares colombianos 2023 (Table 17). ideam.gov.co",
    "IDEAM (2025). Informe del estado de los glaciares colombianos 2024 (Table 1). ideam.gov.co",
])
p("<b>Methodological literature (cited from memory; verify before formal publication):</b>")
bullets([
    "Dozier, J. (1989). Spectral signature of alpine snow cover from the Landsat Thematic Mapper. <i>Remote Sensing of Environment</i>, 28, 9–22.",
    "Paul, F. et al. (2013). On the accuracy of glacier outlines derived from remote-sensing data. <i>Annals of Glaciology</i>, 54(63).",
    "Olofsson, P. et al. (2014). Good practices for estimating area and assessing accuracy of land change. <i>Remote Sensing of Environment</i>, 148, 42–57.",
    "Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. <i>Journal of the American Statistical Association</i>, 63, 1379–1389.",
    "Pasquarella, V. J. et al. (2023). Comprehensive quality assessment of optical satellite imagery using weakly supervised video learning (Cloud Score+). CVPR Workshops.",
])

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
                        title="Nevado del Ruiz — Methodology report", author="Cristian Pastrana")
doc.build(S, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
print("PDF:", OUT)
