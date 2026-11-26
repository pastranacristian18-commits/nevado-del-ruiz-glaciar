/**************************************************************************
 * ANTARES Geospatial Lab · Proyecto #1 Nevados
 * Script 01 (v2) — Serie anual de superficie glaciar-nival, Landsat C2 L2
 *
 * CAMBIOS RESPECTO A v1 (ver 01_serie_glaciar_landsat_v1_descartado.js)
 *   v1 dio una serie físicamente imposible (p. ej. 4,24 km² en 2023 y
 *   0,42 km² en 2024) y cobertura válida < 0,9 en 38 de 41 años.
 *   Diagnóstico:
 *   (a) La máscara Fmask (bits "nube" y "nube dilatada") marca nieve/hielo
 *       brillante como nube y además dilata la máscara: borra el glaciar.
 *   (b) El percentil 25 del NDSI escoge las fechas más sucias (sombras,
 *       ceniza, nubes residuales) y subestima el hielo.
 *   (c) La cobertura se medía sobre toda la zona > 4400 m, no sobre la
 *       zona donde realmente puede haber glaciar.
 *   Solución v2:
 *   (a) Solo se enmascaran nubes de confianza ALTA (bits 8-9) y sombras;
 *       se elimina la dilatación.
 *   (b) Clasificación por FRECUENCIA: % de observaciones válidas del año
 *       en que el píxel es nieve/hielo. Glaciar = nieve en ≥ 50 % de las
 *       observaciones (persistente), con mínimo de observaciones.
 *   (c) Cobertura medida sobre la zona ≥ 4700 m y bandera "confiable".
 *
 * Preprocesamiento del proveedor: Landsat C2 L2 ya trae reflectancia de
 * superficie corregida atmosféricamente (USGS). Nosotros solo aplicamos
 * factores de escala, máscara de nubes, NDSI y compuestos.
 **************************************************************************/

// ------------------------------- CONFIGURACIÓN ---------------------------
var CONFIG = {
  nombre:        'Nevado_del_Ruiz',
  centro:        ee.Geometry.Point([-75.322, 4.895]),
  radio_m:       8000,
  cota_min_m:    4400,   // por debajo no se clasifica hielo persistente
  cota_qa_m:     4700,   // zona donde se mide la cobertura válida
  anio_ini:      1985,
  anio_fin:      2025,
  ndsi_umbral:   0.40,
  verde_min:     0.10,
  frec_min:      0.50,   // fracción de obs. con nieve para llamarlo glaciar
  min_obs:       3,
  cobertura_min: 0.80,   // por debajo, el año se marca como no confiable
  carpeta_drive: 'ANTARES_Nevados',
  crs_export:    'EPSG:32618'
};

var aoi = CONFIG.centro.buffer(CONFIG.radio_m).bounds();
Map.centerObject(aoi, 13);

// ------------------------------- TOPOGRAFÍA ------------------------------
var dem = ee.ImageCollection('COPERNICUS/DEM/GLO30')
  .filterBounds(aoi).select('DEM').mosaic().rename('elev');
var alta = dem.gte(CONFIG.cota_min_m);
var zonaQA = dem.gte(CONFIG.cota_qa_m);

// ------------------------------- LANDSAT ---------------------------------
var BANDAS = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'];

function escalar(img, nombres) {
  return img.select(nombres, BANDAS).multiply(0.0000275).add(-0.2);
}

function enmascarar(img, opt) {
  var qa = img.select('QA_PIXEL');
  var nubeAlta = qa.bitwiseAnd(1 << 3).neq(0)
    .and(qa.rightShift(8).bitwiseAnd(3).eq(3));   // nube, confianza alta
  var sombra = qa.bitwiseAnd(1 << 4).neq(0);
  var ndsi = opt.normalizedDifference(['green', 'swir1']).rename('ndsi');
  var nieve = ndsi.gt(CONFIG.ndsi_umbral)
    .and(opt.select('green').gt(CONFIG.verde_min)).rename('nieve');
  return ee.Image(opt.addBands(ndsi).addBands(nieve).toFloat()
    .updateMask(nubeAlta.or(sombra).not())
    .copyProperties(img, ['system:time_start', 'SPACECRAFT_ID']));
}

function prepTM_ETM(img) {
  return enmascarar(img, escalar(img,
    ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']));
}
function prepOLI(img) {
  return enmascarar(img, escalar(img,
    ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']));
}

var landsat = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').filterBounds(aoi).map(prepTM_ETM)
  .merge(ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterBounds(aoi).map(prepTM_ETM))
  .merge(ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(aoi).map(prepOLI))
  .merge(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterBounds(aoi).map(prepOLI));

var VACIA = ee.Image.constant([0, 0, 0, 0, 0, 0, 0, 0])
  .rename(BANDAS.concat(['ndsi', 'nieve'])).toFloat().updateMask(0);

// ------------------------------- CLASIFICACIÓN ANUAL ---------------------
function anual(y) {
  y = ee.Number(y);
  var ini = ee.Date.fromYMD(y, 1, 1);
  var col = landsat.filterDate(ini, ini.advance(1, 'year'));
  var c = col.merge(ee.ImageCollection([VACIA]));

  var nObs = c.select('nieve').count().rename('n_obs');
  var frec = c.select('nieve').mean().rename('frec_nieve');   // 0–1
  var valido = nObs.gte(CONFIG.min_obs);

  var hielo = frec.gte(CONFIG.frec_min).and(alta)
    .unmask(0).updateMask(valido).rename('hielo');

  var area = ee.Image.pixelArea();
  var stats = hielo.unmask(0).multiply(area).rename('a_hielo')
    .addBands(zonaQA.multiply(area).rename('a_qa'))
    .addBands(valido.unmask(0).and(zonaQA).multiply(area).rename('a_qa_valida'))
    .reduceRegion({reducer: ee.Reducer.sum(), geometry: aoi,
                   scale: 30, maxPixels: 1e9});

  var cobertura = ee.Number(stats.get('a_qa_valida'))
    .divide(ee.Number(stats.get('a_qa')));
  var fila = ee.Feature(null, {
    anio: y,
    area_km2: ee.Number(stats.get('a_hielo')).divide(1e6),
    cobertura_valida: cobertura,
    confiable: cobertura.gte(CONFIG.cobertura_min),
    n_escenas: col.size(),
    sensores: col.aggregate_array('SPACECRAFT_ID').distinct().sort().join(',')
  });

  var img = hielo.unmask(255).toByte()
    .addBands(nObs.toByte())
    .addBands(frec.multiply(100).unmask(255).toByte())
    .set('anio', y);
  return ee.Dictionary({fila: fila, img: img});
}

var anios = ee.List.sequence(CONFIG.anio_ini, CONFIG.anio_fin);
var res = anios.map(anual);
var tabla = ee.FeatureCollection(res.map(function (d) { return ee.Dictionary(d).get('fila'); }));
var imgs = ee.ImageCollection(res.map(function (d) { return ee.Dictionary(d).get('img'); }));
var tablaOK = tabla.filter(ee.Filter.eq('confiable', true));

// ------------------------------- CONSOLA ---------------------------------
print('Años confiables (cobertura ≥ ' + CONFIG.cobertura_min + ')', tablaOK.size());
print(ui.Chart.feature.byFeature(tablaOK, 'anio', ['area_km2'])
  .setChartType('ScatterChart')
  .setOptions({title: CONFIG.nombre + ' — superficie glaciar-nival (v2, solo años confiables)',
               hAxis: {title: 'Año', format: '####'}, vAxis: {title: 'km²'},
               pointSize: 5, legend: {position: 'none'},
               trendlines: {0: {type: 'linear', color: 'red', opacity: 0.4}}}));
print('Tabla (año área cobertura confiable n_escenas)',
  ee.List(tabla.toList(50).map(function (f) {
    f = ee.Feature(f);
    return ee.Number(f.get('anio')).format('%d')
      .cat(' ').cat(ee.Number(f.get('area_km2')).format('%.2f'))
      .cat(' ').cat(ee.Number(f.get('cobertura_valida')).format('%.2f'))
      .cat(' ').cat(ee.String(ee.Algorithms.If(f.get('confiable'), 'OK', '--')))
      .cat(' ').cat(ee.Number(f.get('n_escenas')).format('%d'));
  })).join(' | '));

// ------------------------------- MAPA ------------------------------------
function capaAnio(anio, banda) {
  return imgs.filter(ee.Filter.eq('anio', anio)).first().select(banda);
}
Map.addLayer(landsat.filterDate('2023-01-01', '2026-01-01').median(),
  {bands: ['swir1', 'nir', 'green'], min: 0, max: 0.5}, 'Landsat 2023–25 (hielo = cian)');
Map.addLayer(capaAnio(2023, 'frec_nieve').updateMask(capaAnio(2023, 'frec_nieve').lte(100)),
  {min: 0, max: 100, palette: ['#ffffff', '#9ecae1', '#08306b']}, 'Frecuencia de nieve 2023 (%)', false);
[2001, 2015, 2023].forEach(function (a, i) {
  var h = capaAnio(a, 'hielo');
  Map.addLayer(h.updateMask(h.eq(1)), {palette: [['#2166ac', '#fdae61', '#d7191c'][i]]}, 'Hielo ' + a);
});
Map.addLayer(ee.FeatureCollection('GLIMS/current').filterBounds(aoi)
  .style({color: 'yellow', fillColor: '00000000', width: 1}), {}, 'GLIMS (referencia)', false);
Map.addLayer(ee.Image().paint(aoi, 0, 2), {palette: ['black']}, 'AOI');

// ------------------------------- EXPORTACIONES ---------------------------
Export.table.toDrive({
  collection: tabla,
  description: CONFIG.nombre + '_serie_anual_v2',
  folder: CONFIG.carpeta_drive, fileFormat: 'CSV',
  selectors: ['anio', 'area_km2', 'cobertura_valida', 'confiable', 'n_escenas', 'sensores']
});
var nombres = function (p) {
  return anios.map(function (y) { return ee.String(p).cat(ee.Number(y).format('%d')); });
};
Export.image.toDrive({
  image: imgs.select('hielo').toBands().rename(nombres('hielo_')),
  description: CONFIG.nombre + '_hielo_anual_v2', folder: CONFIG.carpeta_drive,
  region: aoi, scale: 30, crs: CONFIG.crs_export, maxPixels: 1e9
});
Export.image.toDrive({
  image: imgs.select('frec_nieve').toBands().rename(nombres('frec_')),
  description: CONFIG.nombre + '_frecuencia_nieve_anual_v2', folder: CONFIG.carpeta_drive,
  region: aoi, scale: 30, crs: CONFIG.crs_export, maxPixels: 1e9
});
