# Guía Técnica: Análisis Exploratorio de Datos (EDA - Sesión 5)
## Fase 2 de CRISP-DM: Entendimiento de los Datos

Este documento detalla la implementación y los resultados del análisis exploratorio formal ejecutado en el script [`eda_proyecto.py`](../eda_proyecto.py) sobre el dataset consolidado [`dataset_final_crisp_dm_mejorado.csv`](../datos_procesados/dataset_final_crisp_dm_mejorado.csv) (59,564 registros históricos).

---

## 1. Fundamentos Teóricos Aplicados (Sesión 5)

* **Cuarteto de Anscombe:** Los resúmenes estadísticos agregados describen, pero los gráficos revelan patrones no lineales, dispersiones heterogéneas y agrupamientos que las tablas ocultan.
* **Las Tres Familias de Medidas:**
  * *Tendencia Central:* Media, Mediana, Moda.
  * *Dispersión:* Varianza, Desviación Estándar ($\sigma$), Rango Intercuartílico (IQR).
  * *Forma:* Asimetría (*Skewness*) y Curtosis (*Kurtosis*).
* **Regla de Oro en Datos Asimétricos:** Con variables epidemiológicas que presentan una cola derecha pronunciada (*skewness* $> 1$), la media queda sesgada por brotes extremos. La **mediana** constituye la métrica más honesta y robusta para planificar el abastecimiento.
* **Cuantificación Formal de Outliers (Tukey / IQR):** Se identifican matemáticamente aquellos registros por encima de $Q_3 + 1.5 \times \text{IQR}$, clasificándolos en este dominio no como errores sino como **brotes epidemiológicos severos**.

---

## 2. Resumen Estadístico del Caso de Estudio: DENGUE ($N = 1,522$)

| Variable | Media | Mediana | Desv. Est. ($\sigma$) | Asimetría (*Skew*) | Curtosis (*Kurt*) | Diagnóstico de Forma |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Casos Reportados** | **158.78** | **50.50** | 286.81 | **+3.89** | **20.45** | Leptocúrtica extrema, cola derecha muy extendida. |
| **Medicamentos Vendidos**| 10,667.51 | 10,130.50 | 4,203.14 | +2.64 | 12.57 | Cola pesada por concentraciones poblacionales urbanas. |
| **Lluvias Acumuladas (mm)**| 189.48 | 152.45 | 140.58 | +1.94 | 6.04 | Asimetría positiva por departamentos del Pacífico. |
| **Temperatura Promedio (°C)**| 24.40 | 25.38 | 4.22 | -0.90 | 0.43 | Distribución simétrica / Mesocúrtica. |
| **Humedad Ambiente (%)** | 77.16 | 77.31 | 7.64 | -0.21 | -0.08 | Aproximadamente Normal. |

---

## 3. Detección y Análisis de Outliers

* **Primer Cuartil ($Q_1$):** 14.0 casos.
* **Tercer Cuartil ($Q_3$):** 159.8 casos.
* **Rango Intercuartílico ($\text{IQR}$):** 145.8 casos.
* **Umbral Superior de Brote ($Q_3 + 1.5 \times \text{IQR}$):** **378.4 casos mensuales**.
* **Registros de Brote Detectados:** **184 meses-departamento (12.1% de la serie)**.

### Departamentos con Mayor Frecuencia de Brotes Extremos:
1. **Valle del Cauca:** 23 meses con casos sobre el umbral (pico máximo: 1,947 casos).
2. **Meta:** 18 meses con casos sobre el umbral (pico máximo: 2,545 casos).
3. **Córdoba:** 16 meses con casos sobre el umbral (pico máximo: 738 casos).
4. **Norte de Santander:** 16 meses con casos sobre el umbral (pico máximo: 1,095 casos).
5. **Cesar:** 14 meses con casos sobre el umbral (pico máximo: 935 casos).

---

## 4. Modelado Bivariado y Multivariado

### Relación Casos vs Medicamentos
$$\text{Demanda\_Medicamentos} = 12.42 \times \text{Casos\_Reportados} + 8,695 \quad (r = 0.848)$$
* **Pendiente ($m = 12.42$):** Cada caso confirmado de Dengue incrementa la demanda en 12.42 unidades de medicamentos complementarios (sueros orales, analgésicos, antipiréticos).
* **Constante basal ($b = 8,695$):** Demanda estructural mensual en ausencia de epidemia.

### Matriz de Correlación de Pearson
* **Lluvias vs Humedad:** $r = 0.712$ (Alta correlación natural entre humedad atmosférica y pluviosidad).
* **Casos vs Medicamentos:** $r = 0.848$ (Fuerte sincronía entre notificaciones epidemiológicas y consumo de fármacos).
* **Temperatura vs Casos:** $r = 0.161$ (Correlación lineal contemporánea débil; biológicamente explicada por desfases temporales de maduración larvaria de 2 a 4 semanas).

---

## 5. Tabla de Contingencia de Riesgo Logístico (`pd.crosstab`)

Cruzando la demanda proyectada con la capacidad instalada departamental:

| Departamento | % Meses en Riesgo Alto | % Meses en Riesgo Medio | % Meses en Riesgo Bajo |
| :--- | :---: | :---: | :---: |
| **META** | **56.2%** | 39.6% | 4.2% |
| **CHOCÓ** | **38.3%** | 53.2% | 8.5% |
| **MAGDALENA** | **31.2%** | 56.2% | 12.5% |
| **SUCRE** | **29.2%** | 56.2% | 14.6% |
| **CASANARE** | **27.1%** | 62.5% | 10.4% |
| **CUNDINAMARCA** | **22.9%** | 68.8% | 8.3% |
| **TOLIMA** | **20.8%** | 47.9% | 31.2% |

---

## 6. Catálogo de Figuras Generadas

Las siguientes figuras se guardan automáticamente en `datos_procesados/` al ejecutar `python eda_proyecto.py`:

| Archivo | Tipo de Gráfico | Propósito Analítico |
| :--- | :--- | :--- |
| `fig1_hist_casos_dengue.png` | Histograma con Media vs Mediana | Visualizar la asimetría positiva y el desplazamiento de la media. |
| `fig2_box_casos_outliers.png` | Boxplot horizontal | Delimitar la regla IQR ($Q_1, Q_3, 1.5\text{IQR}$) y los 184 brotes atípicos. |
| `fig3_barras_departamentos_eventos.png` | Gráficos de barras ordenados | Jerarquizar los departamentos y patologías por carga acumulada. |
| `fig4_scatter_casos_medicamentos.png` | Dispersión + Recta de Tendencia | Cuantificar el multiplicador de demanda ($m = 12.42$) y correlación $r = 0.848$. |
| `fig5_heatmap_correlaciones.png` | Mapa de calor anotado | Identificar covarianzas y multicolinealidad con colormap bipolar `RdBu_r`. |
| `fig6_matriz_dispersion.png` | Matriz de dispersión (*Pairplot*) | Examinar combinaciones bivariadas simultáneas con diagonal de histogramas. |
| `fig7_tasa_riesgo_desabastecimiento.png` | Barras apiladas 100% | Contrastar la vulnerabilidad de abastecimiento por departamento. |

---

## 7. Instrucciones de Reproducción

```bash
# 1. Asegurar entorno activado
.\.venv\Scripts\Activate.ps1

# 2. Ejecutar análisis exploratorio
python eda_proyecto.py
```
