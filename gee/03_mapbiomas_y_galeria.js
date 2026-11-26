/**************************************************************************
 * ANTARES Geospatial Lab · Proyecto #1 Nevados
 * Script 03 — (A) Serie MapBiomas "Glaciar y nival" (clase 34)
 *             (B) Galería de escenas candidatas para selección visual
 *
 * Contexto: los scripts 01–02 mostraron que Fmask no sirve sobre el
 * glaciar del Ruiz (solo 5 de 2102 escenas "despejadas"). Por eso:
 *   (A) Usamos MapBiomas Colombia Col. 3 como SERIE A AUDITAR (no verdad).
 *       Asset según colombia.mapbiomas.org/en/herramientas (verificar).
 *   (B) Elegimos escenas a ojo con un criterio independiente de Fmask:
 *       fracción "oscura" (sin nube) de un ANILLO de roca/páramo entre
 *       4200 y 4700 m alrededor del glaciar. Si el anillo está despejado,
 *       es probable (no seguro) que la cumbre también: por eso se revisa
 *       cada miniatura visualmente antes de medir.
 **************************************************************************/

var CONFIG = {
  nombre:     'Nevado_del_Ruiz',
  centro:     ee.Geometry.Point([-75.322, 4.895]),
  radio_m:    8000,
  clase_glaciar: 34,
  mb_asset:   'projects/mapbiomas-colombia/assets/LULC/COLECCION3/INTEGRACION/COLOMBIA-1',
  anillo_min: 4200,
  anillo_max: 4700,
  azul_max:   0.15,   // azul < 0.15 en el anillo = superficie sin nube
  n_miniaturas: 40,
  carpeta_drive: 'ANTARES_Nevados'
};

var aoi = CONFIG.centro.buffer(CONFIG.radio_m).bounds();
Map.centerObject(aoi, 13);
var pxArea = ee.Image.pixelArea();
var dem = ee.ImageCollection('COPERNICUS/DEM/GLO30')
  .filterBounds(aoi).select('DEM').mosaic();

// ======================= (A) MAPBIOMAS GLACIAR Y NIVAL ===================
var info = ee.data.getAsset(CONFIG.mb_asset);
print('Tipo de asset MapBiomas', info.type);
var mb = (String(info.type).toUpperCase() === 'IMAGE')
  ? ee.Image(CONFIG.mb_asset)
  : ee.ImageCollection(CONFIG.mb_asset).filterBounds(aoi).mosaic();
print('Bandas MapBiomas (primeras y últimas)', mb.bandNames().slice(0, 3), mb.bandNames().slice(-3));

// Un solo reduceRegion para todas las bandas/años (evita el error de memoria)
var areasMB = mb.eq(CONFIG.clase_glaciar).multiply(pxArea)
  .reduceRegion({reducer: ee.Reducer.sum(), geometry: aoi, scale: 30, maxPixels: 1e10});
var serieMB = ee.FeatureCollection(mb.bandNames().map(function (b) {
  var anio = ee.Number.parse(ee.String(b).replace('[^0-9]', '', 'g'));
  return ee.Feature(null, {anio: anio,
    area_km2_mapbiomas: ee.Number(areasMB.get(b)).divide(1e6)});
}));
print(ui.Chart.feature.byFeature(serieMB, 'anio', ['area_km2_mapbiomas'])
  .setChartType('LineChart')
  .setOptions({title: CONFIG.nombre + ' — MapBiomas Col. 3, clase Glaciar y nival',
               hAxis: {format: '####'}, vAxis: {title: 'km²'}, pointSize: 3,
               legend: {position: 'none'}}));

var primera = mb.select(0), ultima = mb.select(mb.bandNames().size().subtract(1));
Map.addLayer(primera.eq(CONFIG.clase_glaciar).selfMask(), {palette: ['#2166ac']}, 'MapBiomas glaciar — primer año');
Map.addLayer(ultima.eq(CONFIG.clase_glaciar).selfMask(), {palette: ['#d7191c']}, 'MapBiomas glaciar — último año');

Export.table.toDrive({collection: serieMB, description: CONFIG.nombre + '_serie_mapbiomas_c3',
  folder: CONFIG.carpeta_drive, fileFormat: 'CSV', selectors: ['anio', 'area_km2_mapbiomas']});

// ======================= (B) GALERÍA DE ESCENAS CANDIDATAS ===============
var anillo = dem.gte(CONFIG.anillo_min).and(dem.lt(CONFIG.anillo_max)).selfMask();
var BANDAS = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'];

function preparar(img, nombres) {
  var opt = img.select(nombres, BANDAS).multiply(0.0000275).add(-0.2);
  var oscuro = opt.select('blue').lt(CONFIG.azul_max);
  var fr = oscuro.unmask(0).updateMask(anillo).reduceRegion({
    reducer: ee.Reducer.mean(), geometry: aoi, scale: 60, maxPixels: 1e9}).get('blue');
  var d = ee.Date(img.get('system:time_start'));
  return ee.Image(opt.copyProperties(img, ['system:time_start', 'SPACECRAFT_ID']))
    .set({anillo_despejado: fr, fecha: d.format('YYYY-MM-dd'), anio: d.get('year')});
}
function prepTM(i)  { return preparar(i, ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']); }
function prepOLI(i) { return preparar(i, ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']); }

var filtro = ee.Filter.lt('CLOUD_COVER', 70);
var col = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').filterBounds(aoi).filter(filtro).map(prepTM)
  .merge(ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterBounds(aoi).filter(filtro)
         .filterDate('1999-01-01', '2003-06-01').map(prepTM))   // L7 antes de la falla SLC
  .merge(ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(aoi).filter(filtro).map(prepOLI))
  .merge(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterBounds(aoi).filter(filtro).map(prepOLI));

var candidatas = col.filter(ee.Filter.gte('anillo_despejado', 0.6))
  .sort('anillo_despejado', false);

// Exportar la lista completa de candidatas (para documentar la selección)
Export.table.toDrive({
  collection: ee.FeatureCollection(candidatas.map(function (i) {
    return ee.Feature(null, i.toDictionary(['fecha', 'anio', 'SPACECRAFT_ID', 'anillo_despejado']));
  })),
  description: CONFIG.nombre + '_escenas_candidatas', folder: CONFIG.carpeta_drive,
  fileFormat: 'CSV', selectors: ['fecha', 'anio', 'SPACECRAFT_ID', 'anillo_despejado']});

// Miniaturas de las mejores candidatas, ordenadas por fecha
var top = candidatas.limit(CONFIG.n_miniaturas).sort('system:time_start');
var vis = {bands: ['swir1', 'nir', 'green'], min: 0, max: 0.5};
top.aggregate_array('system:index').evaluate(function (ids) {
  print('Galería: ' + ids.length + ' escenas candidatas (SWIR1-NIR-Verde: hielo = cian, nube = blanco)');
  ids.forEach(function (id) {
    var img = ee.Image(top.filter(ee.Filter.eq('system:index', id)).first());
    img.toDictionary(['fecha', 'SPACECRAFT_ID', 'anillo_despejado']).evaluate(function (p) {
      print(p.fecha + '  ' + p.SPACECRAFT_ID + '  anillo=' + p.anillo_despejado.toFixed(2) + '  id=' + id,
        ui.Thumbnail({image: img.visualize(vis).clip(aoi),
                      params: {region: aoi, dimensions: 220, format: 'png'}}));
    });
  });
});
