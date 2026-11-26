# Machine Learning: ¿hielo bajo ceniza? — resultados v1

Fecha: 2026-11-26 · Script: `python/ml_hielo_bajo_ceniza.py` · Datos: `gee/07_descargas_ml_termico.js` · Figura: `reports/figuras/ml_hielo_bajo_ceniza.png` · Métricas: `data/processed/ml_*.csv`, `validation/ml_resultados.txt`

## Pregunta
¿Pueden modelos de Machine Learning con variables espectrales, térmicas y topográficas detectar el glaciar del Ruiz cuando está cubierto de ceniza, donde el índice NDSI falla?

## Diseño
- **Escenas:** 9 Landsat 8/9 (6 bandas SR + temperatura de brillo B10): 5 con ceniza (2020-01, 2023-12, 2024-01, 2025-01 ×2) y 4 limpias (2017-12, 2023-06, 2024-08, 2026-07).
- **Etiquetas:** contorno semiautomático de la escena limpia (propio, o el de 2024-08-15 para las escenas con ceniza, a 5–8 meses). Franja de 60 m a cada lado del borde excluida. 2020-01 sin etiqueta (solo aplicación).
- **Variables:** S = espectral (6 bandas, NDSI, NDWI, rojo/SWIR1, brillo, textura NIR); ST = S + anomalía térmica; STT = ST + cota, pendiente, orientación.
- **Modelos:** NDSI > 0,40 (línea base), regresión logística, Random Forest, XGBoost. Muestreo balanceado de 8000 píxeles por escena; semilla fija.
- **Validación A:** dejar una escena fuera. **Validación B:** dejar un sector fuera (4 cuadrantes alrededor de la cumbre, margen de 300 m; las predicciones fuera-de-sector se unen en un mapa completo y se evalúan juntas).

## Resultados (escenas con ceniza)

| Modelo | Variables | F1 (A: escena fuera) | F1 (B: sector fuera) | Error de área B |
|---|---|---:|---:|---:|
| NDSI > 0,40 | — | 0,28 | 0,25 | −86 % |
| XGBoost | S | 0,60 | 0,25 | −14 % |
| XGBoost | ST | 0,61 | 0,21 | +3 % |
| XGBoost | STT | **0,88** | 0,26 | −32 % |
| Random Forest | STT | 0,85 | 0,27 | −28 % |
| Logística | STT | 0,74 | 0,34 | −17 % |

**Importancia por permutación** (Random Forest STT, prueba en 2024-01-04): cota 0,29 ≫ anomalía térmica 0,065 ≈ rojo/SWIR1 0,063 > pendiente 0,04 > resto ≈ 0.

## Interpretación
1. **El éxito aparente (F1 = 0,88) es en gran parte fuga de información espacial.** Todas las escenas con ceniza comparten la misma referencia (ago-2024) y la variable más importante es la **cota**: el modelo aprendió *dónde* está el glaciar, no *cómo* se ve el hielo bajo ceniza.
2. **Cuando el sector no se vio en el entrenamiento (B), todos los modelos caen a F1 ≈ 0,2–0,3, al nivel de la línea base.** Las predicciones aciertan el área total mejor que el NDSI (−3 % a −32 % frente a −86 %), pero ubican el hielo en sitios equivocados: falsos positivos sobre roca con ceniza y artefactos en los límites de sector.
3. **La señal térmica aporta poco** (+0,01 a +0,05 de F1 en A; nada en B). A 100 m de resolución nativa y con ceniza también fría en altura, no separa bien hielo cubierto de roca cubierta.
4. **Aplicación a 2020-01-09:** NDSI 2,79 km²; modelos 5,7–7,0 km² (MapBiomas 2020: 6,32 km²). Parece coherente, pero dado el punto 2 **no es una estimación confiable**: refleja sobre todo el "prior" topográfico.

## Conclusión
**Con estos datos, el Machine Learning no resuelve el problema del hielo bajo ceniza de forma generalizable.** Mejora al NDSI solo cuando puede apoyarse en la geometría conocida del glaciar. Es un resultado negativo, pero informativo: separa un acierto real de uno producido por fuga de información, que es justamente el error más común en ML aplicado a teledetección.

## Qué haría falta (siguiente iteración)
- **Etiquetas independientes del hielo cubierto:** digitalización sobre imágenes de alta resolución o datos de campo (Nivel 2), no contornos de otra fecha.
- **Sentinel-1 (radar):** la señal de radar no depende de la reflectancia superficial y podría distinguir hielo bajo una capa delgada de ceniza.
- **Información multitemporal:** cambio respecto a la última escena limpia, en lugar de una sola fecha.
- **Prueba de transferencia a otro glaciar** (Santa Isabel, Tolima) para descartar la memorización de la ubicación.
- **Variables topográficas fuera** o normalizadas, salvo que se valide su transferencia.

## Limitaciones
Etiquetas aproximadas (contorno de otra fecha); solo 4 escenas con ceniza y una sola referencia; los contornos de referencia son semiautomáticos (NDSI), lo que hace circular la evaluación en escenas limpias (NDSI F1 = 0,998 por construcción); térmico de 100 m remuestreado a 30 m.
