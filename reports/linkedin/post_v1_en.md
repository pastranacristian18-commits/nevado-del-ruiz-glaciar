# LinkedIn post — v1 English (Nevado del Ruiz)

**Attach:** `reports/figuras/before_after_2003_2024_en.png` (image).

---

🏔️ Nevado del Ruiz, one of Colombia's last glaciated volcanoes, has lost about three quarters of its glacier in 40 years. Measuring that from space turned out to be much harder than I expected.

Over the past weeks I analysed 40 years of open satellite data for Ruiz as the first project of ANTARES Geospatial Lab, my portfolio of reproducible geospatial projects.

📉 What I found:
• MapBiomas Colombia records 14.7 km² of glacier in 1985 and 3.7 km² in 2024.
• My own outlines on clean Landsat scenes confirm the trend: 10.7 km² in 2003 → 4.35 km² in 2024.
• On the same day, Sentinel-2 and Landsat agree within 2–4 %.

🌋 What I didn't expect: volcanic ash hides the glacier.
In the dry season the "visible" ice drops to ~1 km², and months later it is back to ~4 km². The glacier isn't melting and regrowing; it's being buried by ash. Automatic maps measure visible ice, not necessarily glacier extent.

🌡️ Climate (1981–2025, ERA5-Land, CHIRPS and NOAA):
• Regional temperature is rising ~0.1 °C per decade.
• El Niño makes Ruiz warmer and drier.
• Does El Niño accelerate ice loss? The data suggest it, but it isn't statistically conclusive, and I'd rather say that than force the result.

⚠️ What failed: a standard automatic pipeline accepted only 5 of 2,102 Landsat scenes. It took three versions of the algorithm, visual scene selection and cross-sensor validation to get numbers I trust. Everything is documented, including the failed attempts.

My background is field spectroscopy (my thesis estimated sugarcane chlorophyll with VIS-NIR spectra and PLSR). I'm bringing the same obsession with validation to remote sensing.

I also tried machine learning to map the ice under the ash, and it turned into a lesson about spatial validation. That's the next post.

100 % open data: MapBiomas Colombia, USGS Landsat, Copernicus Sentinel-2 and ERA5-Land, CHIRPS, NOAA.

🔗 Code, processed data and the full methodology report: https://github.com/pastranacristian18-commits/nevado-del-ruiz-glaciar

Do you work with glaciers, volcanoes or remote sensing in the Andes? I'd love to hear your thoughts on the method.

#RemoteSensing #GoogleEarthEngine #GIS #Glaciers #ClimateChange #Colombia #OpenData #EarthObservation #MachineLearning
