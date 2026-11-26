/**************************************************************************
 * ANTARES Geospatial Lab · Proyecto #1 Nevados
 * Script 05 — Sentinel-2 (10–20 m) 2017–2026: serie densa y caso 2023
 *
 * Por qué: Landsat no tiene escenas limpias suficientes para resolver la
 * caída de MapBiomas en 2023 (5,19 → 3,77 km²). Sentinel-2 da ~5 días de
 * revisita y 10 m en el visible.
 *
 * Nubes: Cloud Score+ (Google, modelo entrenado; banda cs_cdf), en lugar de
 * Fmask, que falló sobre el glaciar con Landsat. Píxel despejado: cs_cdf ≥ 0,6.
 * Preprocesamiento del proveedor: S2 L2A (Sen2Cor) ya en reflectancia de
 * superficie; colección "harmonized" ya corrige el offset de 2022 (PB 04.00).
 *
 * Salidas:
 *   - Lista de fechas con ≥ 90 % de la zona glaciar (≥ 4700 m) despejada,
 *     con área de nieve/hielo limpio (NDSI > 0,40) por fecha.
 *   - Galería 2022-06 → 2024-06 en color verdadero (ceniza = gris) y falso
 *     color SWIR1-NIR-Verde (hielo limpio = cian).
 **************************************************************************/

var CENTRO = ee.Geometry.Point([-75.322, 4.895]);
var circulo = CENTRO.buffer(6000);
var vista = CENTRO.buffer(3500).bounds();
var pxArea = ee.Image.pixelArea();
var dem = ee.ImageCollection('COPERNICUS/DEM/GLO30').filterBounds(circulo).select('DEM').mosaic();
var alta = dem.gte(4400);
var zona = dem.gte(4700).selfMask();

var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(circulo)
  .filterDate('2017-01-01', '2026-12-01')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 80))
  .linkCollection(ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED'), ['cs_cdf']);

// Un mosaico por día (el Ruiz puede caer en dos teselas)
var dias = s2.aggregate_array('system:time_start')
  .map(function (t) { return ee.Date(t).format('YYYY-MM-dd'); }).distinct();
var porDia = ee.ImageCollection(dias.map(function (d) {
  var ini = ee.Date.parse('YYYY-MM-dd', d);
  return s2.filterDate(ini, ini.advance(1, 'day')).mosaic()
    .set({fecha: d, 'system:time_start': ini.millis()});
}));

function evaluar(img) {
  var despejado = img.select('cs_cdf').gte(0.6).unmask(0);
  var fr = despejado.updateMask(zona).reduceRegion({
    reducer: ee.Reducer.mean(), geometry: circulo, scale: 20, maxPixels: 1e9}).get('cs_cdf');
  var g = img.select('B3').divide(10000), s = img.select('B11').divide(10000);
  var ndsi = g.subtract(s).divide(g.add(s));
  var hielo = ndsi.gt(0.40).and(g.gt(0.10)).and(alta).and(despejado);
  var a = hielo.multiply(pxArea).reduceRegion({
    reducer: ee.Reducer.sum(), geometry: circulo, scale: 20, maxPixels: 1e9}).values().get(0);
  return img.set({despejado: fr, area_km2: ee.Number(a).divide(1e6)});
}

var evaluadas = porDia.map(evaluar);
var buenas = evaluadas.filter(ee.Filter.gte('despejado', 0.90)).sort('system:time_start');

print('Días con imagen / días con ≥ 90 % de zona glaciar despejada', porDia.size(), buenas.size());
print('SERIE_S2', ee.List(buenas.toList(1000).map(function (i) {
  i = ee.Image(i);
  return ee.String(i.get('fecha')).cat(' ')
    .cat(ee.Number(i.get('despejado')).format('%.2f')).cat(' ')
    .cat(ee.Number(i.get('area_km2')).format('%.3f'));
})).join(' | '));

Export.table.toDrive({
  collection: ee.FeatureCollection(buenas.map(function (i) {
    return ee.Feature(null, i.toDictionary(['fecha', 'despejado', 'area_km2']));
  })),
  description: 'Nevado_del_Ruiz_serie_S2_cloudscoreplus', folder: 'ANTARES_Nevados',
  fileFormat: 'CSV', selectors: ['fecha', 'despejado', 'area_km2']});

// Galería del período crítico
var critico = buenas.filterDate('2022-06-01', '2024-07-01');
var visTC = {bands: ['B4', 'B3', 'B2'], min: 0, max: 4000, gamma: 1.2};
var visFC = {bands: ['B11', 'B8', 'B3'], min: 0, max: 5000};
critico.aggregate_array('fecha').evaluate(function (fechas) {
  print('Galería crítica: ' + fechas.length + ' fechas');
  fechas.forEach(function (f) {
    var img = ee.Image(critico.filter(ee.Filter.eq('fecha', f)).first());
    print('GAL|' + f,
      ui.Thumbnail({image: img.visualize(visTC).clip(vista), params: {region: vista, dimensions: 256, format: 'png'}}),
      ui.Thumbnail({image: img.visualize(visFC).clip(vista), params: {region: vista, dimensions: 256, format: 'png'}}));
  });
});
