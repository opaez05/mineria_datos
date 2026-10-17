# Documentación del Proyecto: Predicción de Brotes y Desabastecimiento

Esta carpeta contiene la documentación técnica y analítica del proyecto según las fases de la metodología **CRISP-DM**.

---

## 📚 Índice de Documentación

1. **[Fase 2: Análisis Exploratorio de Datos (EDA - Sesión 5)](eda_sesion5.md)**
   * Caracterización univariada mediante las tres familias de medidas (Tendencia central, Dispersión y Forma).
   * Cuantificación formal de valores atípicos (outliers de brotes) con la regla del Rango Intercuartílico (IQR).
   * Análisis bivariado con correlación de Pearson y regresión lineal ($y = mx + b$).
   * Tasa de riesgo de desabastecimiento hospitalario calculada mediante tablas de contingencia estandarizadas (`pd.crosstab(normalize="index")`).
   * Galería de 7 figuras de alta resolución generadas por `eda_proyecto.py`.

2. **[Reporte Completo de Auditoría y Propuesta CRISP-DM](../Reporte_CRISP_DM.md)**
   * Diagnóstico inicial de las fuentes SIVIGILA, IDEAM y SISMED.
   * Plan de mejora metodológica para las fases de Comprensión del Negocio, Datos y Preparación.

3. **[Informe de Laboratorio EDA (Rúbrica PEA)](../Reporte_EDA_Sesion5.md)**
   * Documento formal con la estructura académica de 6 apartados exigida para la entrega de la Sesión 5.

4. **[Fase 3: Escalamiento de Características](../escalamiento.py)**
   * Justificación matemática del uso de `StandardScaler` (temperatura, humedad) y `RobustScaler` (lluvias extremas y medicamentos con colas pesadas).
