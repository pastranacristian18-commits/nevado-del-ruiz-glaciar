/**************************************************************************
 * ANTARES Geospatial Lab · Proyecto #1 Nevados
 * Script 01 — Serie anual de área glaciar/nival con Landsat C2 L2 (1985–2025)
 *
 * Qué hace
 *   1. Define el área de estudio (Nevado del Ruiz) y una máscara de altura.
 *   2. Une Landsat 5, 7, 8 y 9 (Collection 2, Level 2 = reflectancia de
 *      superficie ya corregida atmosféricamente por USGS; aquí solo aplicamos
 *      factores de escala y máscara de nubes).
 *   3. Calcula NDSI y un compuesto anual por percentil bajo (reduce la nieve
 *      transitoria: el glaciar es lo que persiste todo el año).
 *   4. Clasifica hielo/nieve persistente con umbral (BASELINE, sin ML).
 *   5. Calcula área por año + métricas de calidad (cobertura válida, n° obs).
 *   6. Exporta tabla CSV y pilas de mapas anuales a Google Drive.
 *
 * Qué NO hace todavía (fases siguientes)
 *   - No distingue glaciar de nieve estacional persistente: reportamos
 *     "superficie glaciar-nival" (igual criterio que la clase de MapBiomas).
 *   - No corrige ceniza volcánica (el Ruiz es volcán activo: la ceniza baja
 *     el NDSI y puede subestimar el área). Lo evaluaremos en la fase de ML.
 *   - No armoniza TM/ETM+ con OLI (efecto pequeño en NDSI; se probará).
 **************************************************************************/

// ------------------------------- CONFIGURACIÓN ---------------------------
var CONFIG = {
  nombre:        'Nevado_del_Ruiz',
  centro:        ee.Geometry.Point([-75.322, 4.895]), // cumbre aprox. (WGS84)
  radio_m:       8000,      // ventana de análisis alrededor de la cumbre
  cota_min_m:    4400,      // por debajo no se considera hielo persistente
  anio_ini:      1985,
  anio_fin:      2025,
  ndsi_umbral:   0.40,      // umbral clásico de NDSI para nieve/hielo
  verde_min:     0.10,      // reflectancia verde mínima (excluye agua oscura)
  percentil:     25,        // percentil anual de NDSI
  min_obs:       3,         // obs. válidas mínimas por píxel y año
  carpeta_drive: 'ANTARES_Nevados',
  crs_export:    'EPSG:32618' // UTM 18N
};

var aoi = CONFIG.centro.buffer(CONFIG.radio_m).bounds();
Map.centerObject(aoi, 12);

// ------------------------------- TOPOGRAFÍA ------------------------------
var dem = ee.ImageCollection('COPERNICUS/DEM/GLO30')
  .filterBounds(aoi).select('DEM').mosaic().rename('elev');
var alta = dem.gte(CONFIG.cota_min_m).rename('alta');   // 1 = zona alta

// ------------------------------- LANDSAT ---------------------------------
var BANDAS = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'];

function escalar(img, nombres) {
  // Factores oficiales Collection 2 L2: SR = DN * 0.0000275 - 0.2
  return img.select(nombres, BANDAS).multiply(0.0000275).add(-0.2);
}

function enmascarar(img, opt) {
  var qa = img.select('QA_PIXEL');
  var nube = qa.bitwiseAnd(1 << 1).neq(0)     // nube dilatada
    .or(qa.bitwiseAnd(1 << 3).neq(0))         // nube
    .or(qa.bitwiseAnd(1 << 4).neq(0));        // sombra de nube
  // OJO: NO enmascaramos el bit 5 (nieve) ni la saturación radiométrica:
  // sobre nieve las bandas visibles de TM/ETM+ se saturan con frecuencia y
  // enmascararlas borraría justamente el glaciar.
  var ndsi = opt.normalizedDifference(['green', 'swir1']).rename('ndsi');
  return ee.Image(opt.addBands(ndsi).toFloat()
    .updateMask(nube.not())
    .copyProperties(img, ['system:time_start', 'SPACECRAFT_ID']));
}

function prepTM_ETM(img) {   // Landsat 5 y 7
  return enmascarar(img, escalar(img,
    ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']));
}
function prepOLI(img) {      // Landsat 8 y 9
  return enmascarar(img, escalar(img,
    ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']));
}

var l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').filterBounds(aoi).map(prepTM_ETM);
var l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterBounds(aoi).map(prepTM_ETM);
var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(aoi).map(prepOLI);
var l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterBounds(aoi).map(prepOLI);
var landsat = l5.merge(l7).merge(l8).merge(l9);

// Imagen vacía (todo enmascarado) para que los años sin escenas no rompan
var VACIA = ee.Image.constant([0, 0, 0, 0, 0, 0, 0])
  .rename(BANDAS.concat(['ndsi'])).toFloat().updateMask(0);

// ------------------------------- COMPUESTO ANUAL -------------------------
function anual(y) {
  y = ee.Number(y);
  var ini = ee.Date.fromYMD(y, 1, 1);
  var col = landsat.filterDate(ini, ini.advance(1, 'year'));
  var colSegura = col.merge(ee.ImageCollection([VACIA]));

  var nObs  = colSegura.select('ndsi').count().rename('n_obs');
  var ndsiP = colSegura.select('ndsi')
    .reduce(ee.Reducer.percentile([CONFIG.percentil])).rename('ndsi_p');
  var verde = colSegura.select('green').median().rename('green_med');

  var valido = nObs.gte(CONFIG.min_obs).and(alta);
  var hielo = ndsiP.gt(CONFIG.ndsi_umbral)
    .and(verde.gt(CONFIG.verde_min))
    .and(alta)
    .unmask(0).updateMask(valido).rename('hielo');

  var area = ee.Image.pixelArea();
  var stats = hielo.unmask(0).multiply(area).rename('a_hielo')
    .addBands(alta.multiply(area).rename('a_alta'))
    .addBands(valido.unmask(0).multiply(area).rename('a_valida'))
    .reduceRegion({
      reducer: ee.Reducer.sum(), geometry: aoi, scale: 30, maxPixels: 1e9
    });

  var sensores = col.aggregate_array('SPACECRAFT_ID').distinct().sort();
  var fila = ee.Feature(null, {
    anio:            y,
    area_km2:        ee.Number(stats.get('a_hielo')).divide(1e6),
    cobertura_valida: ee.Number(stats.get('a_valida'))
                       .divide(ee.Number(stats.get('a_alta'))),
    n_escenas:       col.size(),
    sensores:        sensores.join(',')
  });

  var img = hielo.unmask(255).toByte()           // 255 = sin dato
    .addBands(nObs.toByte().rename('n_obs'))
    .addBands(ndsiP.unmask(-9).toFloat())
    .set('anio', y);

  return ee.Dictionary({fila: fila, img: img});
}

var anios = ee.List.sequence(CONFIG.anio_ini, CONFIG.anio_fin);
var resultados = anios.map(anual);
var tabla = ee.FeatureCollection(resultados.map(function (d) {
  return ee.Dictionary(d).get('fila');
}));
var imgs = ee.ImageCollection(resultados.map(function (d) {
  return ee.Dictionary(d).get('img');
}));

// ------------------------------- RESULTADOS EN CONSOLA -------------------
print('Tabla anual (revisa cobertura_valida: < 0.9 = año poco confiable)', tabla);
print(ui.Chart.feature.byFeature(tabla, 'anio', ['area_km2'])
  .setChartType('LineChart')
  .setOptions({
    title: CONFIG.nombre + ' — superficie glaciar-nival (baseline NDSI)',
    hAxis: {title: 'Año', format: '####'},
    vAxis: {title: 'km²'},
    pointSize: 4, legend: {position: 'none'}
  }));
print(ui.Chart.feature.byFeature(tabla, 'anio', ['cobertura_valida'])
  .setChartType('ColumnChart')
  .setOptions({title: 'Control de calidad: fracción de zona alta con ≥ '
               + CONFIG.min_obs + ' obs. válidas', vAxis: {min: 0, max: 1}}));

// ------------------------------- MAPA ------------------------------------
var hieloDe = function (anio) {
  return imgs.filter(ee.Filter.eq('anio', anio)).first().select('hielo')
    .updateMask(imgs.filter(ee.Filter.eq('anio', anio)).first()
    .select('hielo').eq(1));
};
var falsoColor = landsat.filterDate('2024-01-01', '2026-01-01').median();
Map.addLayer(falsoColor, {bands: ['swir1', 'nir', 'green'], min: 0, max: 0.5},
             'Landsat 2024–25 (SWIR1-NIR-Verde: hielo = cian)');
Map.addLayer(dem, {min: 3000, max: 5300, palette: ['#2b1d0e', '#ffffff']},
             'Copernicus DEM', false);
Map.addLayer(hieloDe(1989), {palette: ['#1f78b4']}, 'Hielo 1989');
Map.addLayer(hieloDe(2025), {palette: ['#e31a1c']}, 'Hielo 2025');
// Contornos de referencia GLIMS (solo visual; si el asset falla, comenta esta línea)
Map.addLayer(ee.FeatureCollection('GLIMS/current').filterBounds(aoi)
             .style({color: 'yellow', fillColor: '00000000', width: 1}),
             {}, 'GLIMS (referencia)');
Map.addLayer(ee.Image().paint(aoi, 0, 2), {palette: ['black']}, 'AOI');

// ------------------------------- EXPORTACIONES ---------------------------
Export.table.toDrive({
  collection: tabla,
  description: CONFIG.nombre + '_serie_anual_baseline_NDSI',
  folder: CONFIG.carpeta_drive,
  fileFormat: 'CSV',
  selectors: ['anio', 'area_km2', 'cobertura_valida', 'n_escenas', 'sensores']
});

var renombrar = function (prefijo) {
  return anios.map(function (y) {
    return ee.String(prefijo).cat(ee.Number(y).format('%d'));
  });
};
Export.image.toDrive({
  image: imgs.select('hielo').toBands().rename(renombrar('hielo_')),
  description: CONFIG.nombre + '_mascaras_hielo_anuales',
  folder: CONFIG.carpeta_drive,
  region: aoi, scale: 30, crs: CONFIG.crs_export, maxPixels: 1e9
});
Export.image.toDrive({
  image: imgs.select('n_obs').toBands().rename(renombrar('nobs_')),
  description: CONFIG.nombre + '_n_observaciones_anuales',
  folder: CONFIG.carpeta_drive,
  region: aoi, scale: 30, crs: CONFIG.crs_export, maxPixels: 1e9
});
