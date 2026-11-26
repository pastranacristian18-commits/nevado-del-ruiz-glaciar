/**************************************************************************
 * ANTARES Geospatial Lab · Proyecto #1 Nevados
 * Script 04 — Enlaces de descarga directa (GeoTIFF) para trabajar en QGIS
 *
 *   1. Escenas Landsat seleccionadas (categorías A y A* de
 *      sampling/seleccion_escenas.md): reflectancia de superficie,
 *      6 bandas (blue, green, red, nir, swir1, swir2), UTM 18N, 30 m.
 *   2. MapBiomas Col. 3 clase Glaciar y nival (34), 1985–2024, una banda
 *      por año (1 = glaciar).
 *   3. Copernicus DEM GLO-30.
 *
 * Los enlaces aparecen en la consola. La descarga la hace un script local
 * hacia nevados/data/raw/ (no pasa por Google Drive).
 **************************************************************************/

var aoi = ee.Geometry.Point([-75.322, 4.895]).buffer(8000).bounds();
var CRS = 'EPSG:32618';

var ESCENAS = [
  // [id de la colección, categoría]
  ['LANDSAT/LT05/C02/T1_L2/LT05_009057_19870114', 'Aestrella'],
  ['LANDSAT/LT05/C02/T1_L2/LT05_009056_19971024', 'Aestrella'],
  ['LANDSAT/LE07/C02/T1_L2/LE07_009057_20010112', 'A'],
  ['LANDSAT/LE07/C02/T1_L2/LE07_009057_20021014', 'A'],
  ['LANDSAT/LE07/C02/T1_L2/LE07_009057_20030102', 'A'],
  ['LANDSAT/LC08/C02/T1_L2/LC08_009056_20171218', 'A'],
  ['LANDSAT/LC08/C02/T1_L2/LC08_009056_20211213', 'A'],
  ['LANDSAT/LC09/C02/T1_L2/LC09_009056_20230618', 'A'],
  ['LANDSAT/LC08/C02/T1_L2/LC08_009057_20240815', 'A'],
  ['LANDSAT/LC09/C02/T1_L2/LC09_009056_20260509', 'A'],
  ['LANDSAT/LC09/C02/T1_L2/LC09_009056_20260728', 'Aestrella']
];

function bandasSR(id) {
  return /LT05|LE07/.test(id)
    ? ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']
    : ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'];
}

function enlace(img, nombre) {
  var url = img.getDownloadURL({
    name: nombre, region: aoi, scale: 30, crs: CRS,
    format: 'GEO_TIFF', filePerBand: false
  });
  print('DESCARGA|' + nombre + '|' + url);
}

ESCENAS.forEach(function (e) {
  var id = e[0];
  var img = ee.Image(id).select(bandasSR(id),
      ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'])
    .multiply(0.0000275).add(-0.2).toFloat();
  var corto = id.split('/').pop();
  enlace(img, corto + '_' + e[1]);
});

var mb = ee.Image('projects/mapbiomas-colombia/assets/LULC/COLECCION3/INTEGRACION/COLOMBIA-1');
enlace(mb.eq(34).toByte(), 'mapbiomas_c3_glaciar_1985_2024');

var dem = ee.ImageCollection('COPERNICUS/DEM/GLO30').filterBounds(aoi)
  .select('DEM').mosaic().toFloat();
enlace(dem, 'copernicus_dem_glo30');

print('Listo: ' + (ESCENAS.length + 2) + ' enlaces de descarga generados.');
