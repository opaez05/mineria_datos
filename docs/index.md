# Documentación del Proyecto: Predicción de Brotes y Desabastecimiento

Esta carpeta consolida la documentación técnica, metodológica y académica del proyecto siguiendo el ciclo de vida **CRISP-DM**.

---

## 📚 Índice de Documentación Metodológica

1. **[Fase 2: Análisis Exploratorio de Datos (EDA - Sesión 5)](eda_sesion5.md)**
   * Caracterización univariada mediante las tres familias de medidas (Tendencia central, Dispersión y Forma).
   * Cuantificación formal de valores atípicos (outliers de brotes) con la regla del Rango Intercuartílico (IQR de Tukey).
   * Análisis bivariado con correlación de Pearson y regresión lineal ($y = mx + b$).
   * Tasa de riesgo de desabastecimiento hospitalario calculada mediante tablas de contingencia estandarizadas (`pd.crosstab(normalize="index")`).
   * Galería de 7 figuras de alta resolución generadas por `src/03_eda/eda_proyecto.py`.

2. **[Informe de Laboratorio EDA (Rúbrica PEA)](Reporte_EDA_Sesion5.md)**
   * Documento formal con la estructura académica de los apartados exigidos para la sustentación y entrega del avance analítico.
   * Evidencia estadística sustentada y acciones preventivas de salud pública.

3. **[Reporte de Auditoría y Evolución CRISP-DM](Reporte_CRISP_DM.md)**
   * Diagnóstico y trazabilidad metodológica de las fuentes SIVIGILA, IDEAM y SISMED.
   * Justificación técnica de las soluciones implementadas en ingesta, preparación y modelado predictivo.

4. **[Fase 3: Preparación y Escalamiento de Características](../src/04_transformacion/escalamiento.py)**
   * Justificación matemática de la estrategia híbrida:
     - `StandardScaler` (media 0, varianza 1) para variables de comportamiento gaussiano/simétrico (temperatura y humedad).
     - `RobustScaler` (basado en mediana e IQR) para variables asimétricas y con colas pesadas (precipitaciones extremas y consumo farmacéutico).

5. **[Fase 4 & 5: Modelado Predictivo e Inferencia Futura](../src/05_modelado/probar_modelo_desabastecimiento.py)**
   * Implementación de algoritmos `RandomForestRegressor` para predecir demandas inducidas y generar alertas tempranas de escasez.
   * Simulación prospectiva de escenarios estacionales para el año 2027 ([prediccion_futura_2027.py](../src/05_modelado/prediccion_futura_2027.py)).
