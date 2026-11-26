/**************************************************************************
 * ANTARES Geospatial Lab · Proyecto #1 Nevados
 * Script 07 — Escenas Landsat 8/9 para el experimento de Machine Learning
 *             "hielo bajo ceniza" (enlaces de descarga GeoTIFF)
 *
 * Por qué Landsat 8/9 y no Sentinel-2: tienen banda TÉRMICA (B10, 100 m,
 * entregada a 30 m). El hielo cubierto de ceniza se mantiene cerca de 0 °C,
 * mientras la roca y la ceniza sobre roca se calientan con el sol: la
 * temperatura es una pista física que el NDSI no tiene.
 *
 * Cada GeoTIFF trae 8 bandas en la misma grilla (UTM 18N, 30 m) que las
 * descargas del script 04:
 *   1-6  blue, green, red, nir, swir1, swir2  (reflectancia de superficie, C2 L2)
 *   7    bt10_k   temperatura de brillo TOA de la banda 10 (Kelvin, C2 TOA)
 *   8    qa_pixel (Fmask; solo como referencia, NO se usa para enmascarar)
 *
 * Escenas:
 *   ceniza (categoría C): 2023-12-03, 2024-01-04, 2025-01-14, 2025-01-22, 2020-01-09
 *   limpias (A): 2017-12-18, 2023-06-18, 2024-08-15, 2026-07-28
 **************************************************************************/

var aoi = ee.Geometry.Point([-75.322, 4.895]).buffer(8000).bounds();
var CRS = 'EPSG:32618';

var ESCENAS = [
  ['LC08', 'LC08_009056_20231203', 'ceniza'],
  ['LC08', 'LC08_009056_20240104', 'ceniza'],
  ['LC09', 'LC09_009056_20250114', 'ceniza'],
  ['LC08', 'LC08_009057_20250122', 'ceniza'],
  ['LC08', 'LC08_009057_20200109', 'ceniza'],
  ['LC08', 'LC08_009056_20171218', 'limpia'],
  ['LC09', 'LC09_009056_20230618', 'limpia'],
  ['LC08', 'LC08_009057_20240815', 'limpia'],
  ['LC09', 'LC09_009056_20260728', 'limpia']
];

ESCENAS.forEach(function (e) {
  var sr = ee.Image('LANDSAT/' + e[0] + '/C02/T1_L2/' + e[1]);
  var toa = ee.Image('LANDSAT/' + e[0] + '/C02/T1_TOA/' + e[1]);
  var img = sr.select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'],
                      ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'])
    .multiply(0.0000275).add(-0.2)
    .addBands(toa.select(['B10'], ['bt10_k']))
    .addBands(sr.select(['QA_PIXEL'], ['qa_pixel']))
    .toFloat();
  var url = img.getDownloadURL({name: e[1] + '_' + e[2], region: aoi, scale: 30,
                                crs: CRS, format: 'GEO_TIFF', filePerBand: false});
  print('DESCARGA|' + e[1] + '_' + e[2] + '|' + url);
});
print('Listo: ' + ESCENAS.length + ' enlaces de descarga generados.');
