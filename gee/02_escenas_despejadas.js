/**************************************************************************
 * ANTARES Geospatial Lab · Proyecto #1 Nevados
 * Script 02 — Área glaciar-nival ESCENA POR ESCENA (solo días despejados)
 *
 * Por qué existe (historial de métodos)
 *   v1 (percentil 25 de NDSI) → serie imposible: Fmask borraba el glaciar.
 *   v2 (frecuencia anual de nieve) → 2023 ≈ 2001 y 2014 = 14,5 km²: las
 *       nubes de hielo (NDSI alto) y la nieve estacional se cuentan como
 *       glaciar; además la cobertura válida es baja casi todos los años.
 *   v3 (este script) → enfoque estándar en glaciología con óptico:
 *       1. Para cada escena Landsat se mide la fracción DESPEJADA de la
 *          zona glaciar (≥ 4700 m) según Fmask (nube, sombra, cirro, relleno).
 *       2. Solo se aceptan escenas con ≥ 95 % de la zona despejada.
 *       3. En cada escena aceptada se mide el área de nieve/hielo (NDSI).
 *       4. Por año: mediana, mínimo y máximo de las escenas aceptadas.
 *          El mínimo se acerca más al glaciar (menos nieve estacional);
 *          el rango max–min es una medida honesta de la variabilidad.
 *   Años sin escenas aceptadas quedan vacíos (no se inventan).
 **************************************************************************/

var CONFIG = {
  nombre:         'Nevado_del_Ruiz',
  centro:         ee.Geometry.Point([-75.322, 4.895]),
  radio_m:        8000,
  cota_min_m:     4400,
  cota_qa_m:      4700,
  anio_ini:       1985,
  anio_fin:       2025,
  ndsi_umbral:    0.40,
  verde_min:      0.10,
  despejado_min:  0.95,
  carpeta_drive:  'ANTARES_Nevados'
};

var aoi = CONFIG.centro.buffer(CONFIG.radio_m).bounds();
Map.centerObject(aoi, 13);

var dem = ee.ImageCollection('COPERNICUS/DEM/GLO30')
  .filterBounds(aoi).select('DEM').mosaic().rename('elev');
var alta = dem.gte(CONFIG.cota_min_m);
var zonaQA = dem.gte(CONFIG.cota_qa_m).selfMask();
var pxArea = ee.Image.pixelArea();

var BANDAS = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'];

function preparar(img, nombres) {
  var opt = img.select(nombres, BANDAS).multiply(0.0000275).add(-0.2);
  var qa = img.select('QA_PIXEL');
  var malo = qa.bitwiseAnd(1 << 0).neq(0)      // relleno (incl. franjas L7)
    .or(qa.bitwiseAnd(1 << 2).neq(0))          // cirro (solo OLI)
    .or(qa.bitwiseAnd(1 << 3).neq(0))          // nube
    .or(qa.bitwiseAnd(1 << 4).neq(0));         // sombra de nube
  var ndsi = opt.normalizedDifference(['green', 'swir1']).rename('ndsi');
  var nieve = ndsi.gt(CONFIG.ndsi_umbral)
    .and(opt.select('green').gt(CONFIG.verde_min)).rename('nieve');
  var limpio = malo.not().rename('limpio');

  var stats = limpio.updateMask(zonaQA).reduceRegion({
    reducer: ee.Reducer.mean(), geometry: aoi, scale: 30, maxPixels: 1e9});
  var area = nieve.and(alta).and(limpio).unmask(0).multiply(pxArea)
    .reduceRegion({reducer: ee.Reducer.sum(), geometry: aoi,
                   scale: 30, maxPixels: 1e9});

  return ee.Image(opt.addBands(ndsi).addBands(nieve).updateMask(limpio)
    .copyProperties(img, ['system:time_start', 'SPACECRAFT_ID']))
    .set({
      despejado: stats.get('limpio'),
      area_km2: ee.Number(area.get('nieve')).divide(1e6),
      anio: ee.Date(img.get('system:time_start')).get('year'),
      fecha: ee.Date(img.get('system:time_start')).format('YYYY-MM-dd')
    });
}
function prepTM(img)  { return preparar(img, ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']); }
function prepOLI(img) { return preparar(img, ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']); }

var fechas = [CONFIG.anio_ini + '-01-01', (CONFIG.anio_fin + 1) + '-01-01'];
var escenas = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').filterBounds(aoi).filterDate(fechas[0], fechas[1]).map(prepTM)
  .merge(ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterBounds(aoi).filterDate(fechas[0], fechas[1]).map(prepTM))
  .merge(ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(aoi).filterDate(fechas[0], fechas[1]).map(prepOLI))
  .merge(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterBounds(aoi).filterDate(fechas[0], fechas[1]).map(prepOLI));

var aceptadas = escenas.filter(ee.Filter.gte('despejado', CONFIG.despejado_min))
  .sort('system:time_start');

// Tabla por escena (todas, para auditar el filtro)
var tablaEscenas = ee.FeatureCollection(escenas.map(function (img) {
  return ee.Feature(null, img.toDictionary(['fecha', 'anio', 'SPACECRAFT_ID', 'despejado', 'area_km2']));
}));

// Resumen anual (solo escenas aceptadas)
var tablaAnual = ee.FeatureCollection(ee.List.sequence(CONFIG.anio_ini, CONFIG.anio_fin).map(function (y) {
  var a = aceptadas.filter(ee.Filter.eq('anio', y)).aggregate_array('area_km2');
  var n = a.size();
  return ee.Feature(null, {
    anio: y, n_escenas_ok: n,
    area_mediana: ee.Algorithms.If(n.gt(0), a.reduce(ee.Reducer.median()), null),
    area_min:     ee.Algorithms.If(n.gt(0), a.reduce(ee.Reducer.min()), null),
    area_max:     ee.Algorithms.If(n.gt(0), a.reduce(ee.Reducer.max()), null)
  });
})).filter(ee.Filter.gt('n_escenas_ok', 0));

// ------------------------------- CONSOLA ---------------------------------
print('Escenas totales / aceptadas', escenas.size(), aceptadas.size());
print(ui.Chart.feature.byFeature(
    ee.FeatureCollection(aceptadas.map(function (i) {
      return ee.Feature(null, {t: i.get('system:time_start'), area_km2: i.get('area_km2')});
    })), 't', ['area_km2'])
  .setChartType('ScatterChart')
  .setOptions({title: CONFIG.nombre + ' — área por escena despejada (≥ 95 %)',
               hAxis: {title: 'Fecha'}, vAxis: {title: 'km²'}, pointSize: 4,
               legend: {position: 'none'}}));
print('Resumen anual (año n mediana min max)',
  ee.List(tablaAnual.toList(50).map(function (f) {
    f = ee.Feature(f);
    return ee.Number(f.get('anio')).format('%d')
      .cat(' n=').cat(ee.Number(f.get('n_escenas_ok')).format('%d'))
      .cat(' med=').cat(ee.Number(f.get('area_mediana')).format('%.2f'))
      .cat(' min=').cat(ee.Number(f.get('area_min')).format('%.2f'))
      .cat(' max=').cat(ee.Number(f.get('area_max')).format('%.2f'));
  })).join(' | '));
print('Escenas aceptadas (fecha sensor despejado área)',
  ee.List(aceptadas.toList(500).map(function (i) {
    i = ee.Image(i);
    return ee.String(i.get('fecha')).cat(' ').cat(ee.String(i.get('SPACECRAFT_ID')))
      .cat(' ').cat(ee.Number(i.get('despejado')).format('%.2f'))
      .cat(' ').cat(ee.Number(i.get('area_km2')).format('%.2f'));
  })).join(' | '));

// ------------------------------- MAPA ------------------------------------
var ultima = ee.Image(aceptadas.sort('system:time_start', false).first());
Map.addLayer(ultima, {bands: ['swir1', 'nir', 'green'], min: 0, max: 0.5},
             'Última escena aceptada (hielo = cian)');
Map.addLayer(ultima.select('nieve').selfMask(), {palette: ['#d7191c']}, 'Nieve/hielo última escena');
Map.addLayer(zonaQA, {palette: ['#ffff00'], opacity: 0.2}, 'Zona QA ≥ 4700 m', false);
Map.addLayer(ee.FeatureCollection('GLIMS/current').filterBounds(aoi)
  .style({color: 'yellow', fillColor: '00000000', width: 1}), {}, 'GLIMS (referencia)', false);
print('Fecha de la última escena aceptada', ultima.get('fecha'));

// ------------------------------- EXPORTACIONES ---------------------------
Export.table.toDrive({collection: tablaEscenas, description: CONFIG.nombre + '_escenas_todas',
  folder: CONFIG.carpeta_drive, fileFormat: 'CSV',
  selectors: ['fecha', 'anio', 'SPACECRAFT_ID', 'despejado', 'area_km2']});
Export.table.toDrive({collection: tablaAnual, description: CONFIG.nombre + '_resumen_anual_escenas',
  folder: CONFIG.carpeta_drive, fileFormat: 'CSV',
  selectors: ['anio', 'n_escenas_ok', 'area_mediana', 'area_min', 'area_max']});
