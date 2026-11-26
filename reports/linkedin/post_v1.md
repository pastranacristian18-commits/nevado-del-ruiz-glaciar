# Post LinkedIn — borrador v1 (Nevado del Ruiz)

**Adjuntar:** `carrusel_ruiz.pdf` (como documento) — o `antes_despues_2003_2024.png` si prefieres una sola imagen.
**Antes de publicar:** revisar cifras con el autor; enlace al repositorio cuando exista.

---

🏔️ El Nevado del Ruiz perdió cerca de 3/4 de su glaciar en 40 años. Pero medirlo con satélites fue más difícil de lo que pensaba.

Durante las últimas semanas analicé 40 años de imágenes satelitales abiertas del Ruiz como primer proyecto de ANTARES Geospatial Lab, mi portafolio de proyectos geoespaciales reproducibles.

📉 Lo que encontré:
• MapBiomas Colombia registra 14,7 km² de glaciar en 1985 y 3,7 km² en 2024.
• Mis contornos en escenas limpias de Landsat confirman la tendencia: 10,7 km² en 2003 → 4,35 km² en 2024.
• Sentinel-2 y Landsat, el mismo día, coinciden con diferencias de 2–4 %.

🌋 Lo que no esperaba: la ceniza del volcán esconde el glaciar.
En temporada seca el hielo "visible" cae a ~1 km², y meses después vuelve a ~4 km². No se derrite y reaparece: lo tapa la ceniza. Los mapas automáticos miden hielo visible, no necesariamente glaciar.

🌡️ Clima (1981–2025, ERA5-Land, CHIRPS y NOAA):
• La temperatura de la región sube ~0,1 °C por década.
• El Niño hace al Ruiz más cálido y más seco.
• ¿El Niño acelera la pérdida de hielo? Los datos lo sugieren, pero no es estadísticamente concluyente. Prefiero decirlo así que forzar el resultado.

⚠️ Lo que falló: un método automático estándar aceptó solo 5 de 2.102 escenas Landsat. Necesité tres versiones del algoritmo, selección visual de escenas y validación entre sensores para tener números en los que confío. Todo está documentado, incluidos los intentos fallidos.

Vengo de la espectroscopía de campo (mi tesis fue sobre clorofila en caña de azúcar con VIS-NIR y PLSR). Esa misma obsesión por la validación es la que estoy llevando a la teledetección.

Siguiente paso: Machine Learning para mapear el hielo bajo la ceniza, comparado contra el método clásico como línea base.

Datos 100 % abiertos: MapBiomas Colombia, USGS Landsat, Copernicus Sentinel-2 y ERA5-Land, CHIRPS, NOAA.

🔗 Código, datos procesados e informe metodológico completo: https://github.com/pastranacristian18-commits/nevado-del-ruiz-glaciar

¿Trabajas con glaciares, volcanes o teledetección en los Andes? Me encantaría conocer tu opinión sobre el método.

#Teledetección #GoogleEarthEngine #QGIS #Glaciares #CambioClimático #Colombia #DatosAbiertos #SIG #MapBiomas

---

## Checklist antes de publicar
- [ ] Revisar y, si quieres, editar los contornos en QGIS (son semiautomáticos, con revisión visual preliminar).
- [ ] Confirmar que estás cómodo con cada cifra (todas vienen de `validation/`).
- [ ] No citar la cifra del IDEAM hasta leerla en el PDF original.
- [ ] Verificar la licencia de MapBiomas Colombia antes de reutilizar sus mapas en imágenes.
- [x] Repositorio en GitHub enlazado.
