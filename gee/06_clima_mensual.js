/**************************************************************************
 * ANTARES Geospatial Lab · Proyecto #1 Nevados
 * Script 06 — Clima mensual 1981–2025 sobre el Nevado del Ruiz
 *
 * Variables
 *   ERA5-Land (reanálisis, ~9 km, mensual): temperatura a 2 m, precipitación
 *     total, nevada (agua equivalente).
 *   CHIRPS (satélite + estaciones, ~5 km, péntadas): precipitación.
 *   Isoterma 0 °C ESTIMADA = cota media de la celda ERA5 + T2m / 0,0065
 *     (gradiente estándar 6,5 °C/km). Es una aproximación, no una medición.
 *
 * Limitación: una celda de ERA5-Land promedia ~9 km de terreno muy
 * heterogéneo (de ~3500 a 5300 m). Por eso se analizan ANOMALÍAS y
 * TENDENCIAS, no valores absolutos en la cumbre.
 **************************************************************************/

var CENTRO = ee.Geometry.Point([-75.322, 4.895]);
var circulo = CENTRO.buffer(6000);
var ini = '1981-01-01', fin = '2026-01-01';

var era = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').filterDate(ini, fin)
  .select(['temperature_2m', 'total_precipitation_sum', 'snowfall_sum']);
var proyEra = era.first().projection();

// Cota media de la celda ERA5 que contiene la cumbre (Copernicus DEM)
var dem = ee.ImageCollection('COPERNICUS/DEM/GLO30').filterBounds(CENTRO.buffer(20000)).select('DEM').mosaic();
var cotaCelda = ee.Number(dem.setDefaultProjection('EPSG:4326', null, 30)
  .reduceResolution({reducer: ee.Reducer.mean(), maxPixels: 65535})
  .reproject(proyEra)
  .reduceRegion({reducer: ee.Reducer.first(), geometry: CENTRO, scale: 11132}).values().get(0));
print('COTA_CELDA_ERA5', cotaCelda);

var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD').filterDate(ini, fin);

var meses = ee.List.sequence(0, 12 * 45 - 1).map(function (k) {
  return ee.Date(ini).advance(k, 'month');
});

var filas = meses.map(function (d) {
  d = ee.Date(d);
  var e = era.filterDate(d, d.advance(1, 'month')).first();
  var ve = e.reduceRegion({reducer: ee.Reducer.mean(), geometry: CENTRO, scale: 11132});
  var pc = chirps.filterDate(d, d.advance(1, 'month')).sum()
    .reduceRegion({reducer: ee.Reducer.mean(), geometry: circulo, scale: 5566}).get('precipitation');
  var t = ee.Number(ve.get('temperature_2m')).subtract(273.15);
  return d.format('YYYY-MM')
    .cat(' ').cat(t.format('%.2f'))
    .cat(' ').cat(ee.Number(ve.get('total_precipitation_sum')).multiply(1000).format('%.1f'))
    .cat(' ').cat(ee.Number(ve.get('snowfall_sum')).multiply(1000).format('%.2f'))
    .cat(' ').cat(ee.Number(pc).format('%.1f'));
});
print('CLIMA (mes T2m_C precip_era5_mm nevada_era5_mm precip_chirps_mm)');
print('CLIMA_TXT', ee.List(filas).join(' | '));
