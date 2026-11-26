# Registro de fuentes de datos

Estado: **V** = verificado en fuente oficial · **P** = pendiente de verificar.

| Fuente | Proveedor | Procesamiento del proveedor | Lo que hacemos nosotros | Resolución | Periodo | Licencia | Acceso | Estado |
|---|---|---|---|---|---|---|---|---|
| Landsat 5/7/8/9 Collection 2 Level 2 | USGS | Reflectancia de superficie (corrección atmosférica), QA_PIXEL (Fmask) | Factores de escala, máscara de nubes/sombras, NDSI, compuestos anuales | 30 m | 1985– | Dominio público (USGS) | GEE `LANDSAT/L*0*/C02/T1_L2` | P (licencia) |
| Sentinel-2 L2A Harmonized | ESA / Copernicus | Corrección atmosférica Sen2Cor | Máscara de nubes (Cloud Score+) | 10–20 m | 2017– | Copernicus, libre | GEE `COPERNICUS/S2_SR_HARMONIZED` | P |
| Copernicus DEM GLO-30 | ESA | DEM de superficie | Cotas, pendiente, orientación, hipsometría | 30 m | ~2011–2015 | Copernicus DEM, libre con atribución | GEE `COPERNICUS/DEM/GLO30` | P |
| MapBiomas Colombia Col. 3 — clase Glaciar y nival (34) | MapBiomas Colombia | Clasificación Random Forest sobre Landsat | Referencia de comparación (no verdad) | 30 m | 1985–2024 | P (CC-BY según una página; "no comercial" según otra) | GEE `projects/mapbiomas-colombia/...` | V (clase existe) / P (asset, licencia) |
| RGI 7.0 / GLIMS | RGI Consortium / NSIDC | Contornos glaciares digitalizados | Referencia independiente de contorno | Polígonos | ~2000 (varía) | CC BY 4.0 según guía RGI | NSIDC-0770 v7; GEE `GLIMS/current` | V (guía) / P (NSIDC) |
| IDEAM — informes de glaciares | IDEAM | Estimaciones oficiales de área | Referencia de área (solo cifras leídas en PDF) | — | Varios años | P | ideam.gov.co | P |
| ERA5-Land | ECMWF / Copernicus | Reanálisis | Temperatura, nieve, escorrentía, humedad del suelo | ~9 km | 1950– | Licencia Copernicus | GEE `ECMWF/ERA5_LAND/MONTHLY_AGGR` | P |
| CHIRPS | UCSB-CHC | Precipitación satélite + estaciones | Series de precipitación de cuencas | ~5 km | 1981– | P | GEE `UCSB-CHG/CHIRPS/DAILY` | P |
| MODIS LST | NASA | Temperatura de superficie | Anomalías térmicas | 1 km | 2000– | Libre (NASA) | GEE `MODIS/061/MOD11A2` | P |
| ONI (El Niño/La Niña) | NOAA CPC | Índice oceánico | Correlación con área glaciar | Mensual | 1950– | Dominio público (NOAA) | cpc.ncep.noaa.gov | P |
| HydroSHEDS | WWF / USGS | Cuencas y drenaje | Delimitación de cuencas | 15 arcsec | — | P | GEE `WWF/HydroSHEDS/*` | P |
| Caudales IDEAM (DHIME) | IDEAM | Mediciones en estaciones | Validación hidrológica | Diaria | Varía | P | dhime.ideam.gov.co | P |
