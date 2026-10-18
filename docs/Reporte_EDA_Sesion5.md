# INFORME DE ANÁLISIS EXPLORATORIO DE DATOS (EDA)
## Metodología CRISP-DM – Fase 2: Entendimiento de los Datos (Cierre Avance 1)
### Proyecto: Sistema Inteligente de Alerta Temprana para Predicción de Brotes Epidemiológicos y Prevención del Desabastecimiento de Medicamentos en Colombia


### 1.1. Pregunta Central de Negocio
> **¿De qué manera las fluctuaciones climáticas regionales (temperatura, precipitación y humedad relativa) inciden en la dinámica de propagación de enfermedades de transmisión vectorial (específicamente Dengue) en Colombia, y cómo impacta este comportamiento la demanda inducida de medicamentos esenciales para anticipar puntos críticos de desabastecimiento hospitalario en los diferentes departamentos?**

### 1.2. Objetivos del Análisis Exploratorio (Sesión 5)
1. **Evaluar la calidad y estructura** de la base de datos integrada (59,564 registros históricos mensuales a nivel departamental, 2017–2021).
2. **Caracterizar el comportamiento univariado** de los eventos de salud pública y variables meteorológicas mediante las tres familias de medidas estadísticas: Tendencia Central, Dispersión y Forma (asimetría y curtosis).
3. **Cuantificar formalmente los valores atípicos (outliers)** a través de la regla del Rango Intercuartílico (IQR de Tukey), identificando brotes epidémicos reales versus ruido.
4. **Analizar relaciones bivariadas y multivariadas**, modelando la correlación de Pearson, rectas de tendencia y matrices de dispersión entre variables climáticas, incidencia de casos y consumo farmacéutico.
5. **Calcular la tasa departamental de riesgo logístico** mediante tablas de contingencia estandarizadas (`pd.crosstab(normalize="index")`), derivando hallazgos accionables para la toma de decisiones preventivas.

---

## 2. Auditoría de Calidad de Datos (15%)

El dataset analizado corresponde al consolidado unificado en `datos_procesados/dataset_final_crisp_dm_mejorado.csv`, derivado del pipeline de extracción, limpieza y normalización espaciotemporal de SIVIGILA, IDEAM y SISMED.

```
Dimensiones del Dataset: 59,564 observaciones x 10 columnas
Nulos globales: 0 (Dataset 100% verificado e imputado)
Granularidad: Departamento - Año - Mes - Código Evento SIVIGILA
```

### 2.1. Detección y Cuantificación de Outliers mediante Regla IQR (Tukey)
Siguiendo las directrices pedagógicas de la Sesión 5, los outliers no se evalúan de manera cualitativa o subjetiva ("se ven raros"), sino mediante el cálculo matemático del Rango Intercuartílico:
$$\text{IQR} = Q_3 - Q_1$$
$$\text{Límite Superior} = Q_3 + 1.5 \times \text{IQR}$$
$$\text{Límite Inferior} = \max(0, Q_1 - 1.5 \times \text{IQR})$$

#### Aplicación a la Variable Crítica: Casos Reportados de Dengue ($N = 1,522$)
* **Primer Cuartil ($Q_1$ - Percentil 25):** 14.0 casos mensuales.
* **Tercer Cuartil ($Q_3$ - Percentil 75):** 159.8 casos mensuales.
* **Rango Intercuartílico ($\text{IQR}$):** $159.8 - 14.0 = 145.8$ casos.
* **Límite Superior Teórico:** $159.8 + (1.5 \times 145.8) = \mathbf{378.4\text{ casos}}$.
* **Registros clasificados como Outliers:** **184 meses-departamento (12.1% del total)**.

> **Decisión de Negocio y Minería:** En epidemiología, estos 184 registros **NO son errores de digitación ni ruido instrumental**, sino **brotes epidémicos severos** (con picos que alcanzan hasta 2,752 casos mensuales en Atlántico y 2,545 en Meta). Eliminar estos datos destruiría la señal predictiva de alarma que el sistema requiere para prever desabastecimientos. Por lo tanto, se conservan y sustentan la necesidad de usar escaladores robustos a la mediana (`RobustScaler`) en la Fase de Modelado.

---

## 3. Análisis Univariado: Tres Familias de Medidas (25%)

### 3.1. Tendencia Central, Dispersión y Forma
La tabla siguiente resume la caracterización estadística formal del caso de estudio prioritario (Dengue, $N=1,522$):

| Variable Analizada | Media | Mediana | Desv. Estándar ($\sigma$) | Asimetría (*Skewness*) | Curtosis (*Kurtosis*) | Interpretación de Forma |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Casos Reportados** | **158.78** | **50.50** | 286.81 | **+3.89** | **20.45** | Asimetría positiva extrema; colas pesadas (Leptocúrtica). |
| **Medicamentos Vendidos** | 10,667.51 | 10,130.50 | 4,203.14 | +2.64 | 12.57 | Cola derecha extendida por capitales densamente pobladas. |
| **Lluvias Acumuladas (mm)**| 189.48 | 152.45 | 140.58 | +1.94 | 6.04 | Asimetría derecha; régimen pluviométrico bimodal y Pacífico. |
| **Temperatura Promedio (°C)**| 24.40 | 25.38 | 4.22 | -0.90 | 0.43 | Distribución aproximadamente simétrica / Mesocúrtica. |
| **Humedad Ambiente (%)** | 77.16 | 77.31 | 7.64 | -0.21 | -0.08 | Distribución casi simétrica / Normal. |

### 3.2. Regla de Oro Estadística Demostrada: "Media vs Mediana"
Tal como se enfatizó en la Sesión 5 con el cuarteto de Anscombe y la teoría de distribuciones asimétricas:
* En **Casos Reportados**, la media (158.8) triplica a la mediana (50.5). Esto ocurre porque el 12.1% de brotes extremos arrastra la media hacia arriba.
* **Conclusión técnica:** Reportar únicamente la media genera falsas expectativas de demanda promedio y sesga la planeación logística. La **mediana (50.5 casos/mes)** representa fielmente el comportamiento típico de un departamento colombiano en condiciones endémicas estándar.

### 3.3. Interpretación Visual del Histograma y Boxplot
* **Figura 1 (`fig1_hist_casos_dengue.png`):** El histograma confirma la masa principal acumulada entre 0 y 150 casos, con una cola derecha que se extiende hasta más de 2,700 casos. La línea discontinua roja (Media: 158.8) queda notablemente desplazada a la derecha de la línea continua verde (Mediana: 50.5), sello visual inequívoco de asimetría positiva.
* **Figura 2 (`fig2_box_casos_outliers.png`):** El diagrama de caja y bigotes evidencia un 50% central de los datos condensado en el rango intercuartílico de 14 a 160 casos, mientras que una constelación densa de círculos rojos fuera del bigote superior superior a 378 casos delimita visualmente los periodos de crisis hospitalaria.

---

## 4. Análisis Bivariado y Multivariado (25%)

### 4.1. Análisis Categórico Ordenado por Frecuencia
* **Figura 3 (`fig3_barras_departamentos_eventos.png`):** 
  * Cumpliendo con la buena práctica de la Sesión 5 (*"el orden de las barras ya es información; jamás graficar alfabéticamente"*), los departamentos se ordenan por su mediana y volumen acumulado.
  * **Top 5 en carga endémica de Dengue:** Valle del Cauca (Mediana = 322.5 casos), Antioquia (Mediana = 283.0), Tolima (Mediana = 237.5), Norte de Santander (Mediana = 191.5) y Santander (Mediana = 175.0).
  * A nivel nacional, el Dengue se consolida como la 4ª patología con mayor volumen acumulado en Colombia (>241,000 casos en el periodo analizado), superado únicamente por agresiones de animales potencialmente transmisores de rabia, violencia intrafamiliar y varicela.

### 4.2. Dispersión y Recta de Tendencia: Relación Casos vs Medicamentos
* **Figura 4 (`fig4_scatter_casos_medicamentos.png`):**
  * Coeficiente de correlación de Pearson: **$r = 0.848$** (Asociación lineal muy fuerte y positiva).
  * Ecuación ajustada por mínimos cuadrados:
    $$\text{Demanda\_Medicamentos} = 12.42 \times \text{Casos\_Reportados} + 8,695$$
  * **Interpretación de Negocio:** Por cada caso adicional de Dengue reportado en un departamento durante un mes, la demanda de medicamentos asociados (analgésicos, antipiréticos, sales de rehidratación oral y fluidoterapia) se incrementa en promedio en **12.42 unidades**. La constante base (intercepto en ~8,695 unidades) refleja el consumo basal farmacéutico fijo de las instituciones de salud para atención sintomática rutinaria.

### 4.3. Distinción Rigurosa: Correlación vs Causalidad
* **Clima vs Casos:** La correlación lineal simple entre Temperatura y Casos de Dengue es de $r = 0.161$ (positiva débil) y Lluvias de $r = -0.141$. 
* **Lección de la Sesión 5:** Un coeficiente lineal modesto no implica ausencia de relación; el ciclo de vida del vector *Aedes aegypti* tiene retardos no lineales (las lluvias estancadas y la temperatura tardan entre 2 y 4 semanas en traducirse en mosquitos adultos e infecciones). Confundir la falta de correlación lineal estricta con falta de causalidad biológica sería un error fatal en el modelado.

### 4.4. Mapa de Calor y Matriz de Dispersión
* **Figura 5 (`fig5_heatmap_correlaciones.png`):**
  * Presenta la matriz de Pearson completa con gradiente `RdBu_r` centrado en 0.
  * Se identifica una fuerte correlación entre Lluvias Acumuladas y Humedad Ambiente ($r = 0.712$), advirtiendo potencial colinealidad que debe gestionarse en modelos lineales.
* **Figura 6 (`fig6_matriz_dispersion.png`):**
  * Muestra los cruces bivariados simultáneos de las 4 variables clave del proyecto con sus histogramas en la diagonal, permitiendo detectar visualmente agrupamientos bimodales en la temperatura según altitud regional.

### 4.5. Cruce de Contingencia Estandarizado: Tasa de Riesgo de Desabastecimiento
Aplicando la metodología del ejercicio oficial de la Sesión 5 (`pd.crosstab(normalize="index")`), se categorizó el índice de presión hospitalaria (demanda sobre inventario instalado):

| Departamento | Tasa Riesgo Alto (%) | Tasa Riesgo Medio (%) | Tasa Riesgo Bajo (%) | Evaluación Logística |
| :--- | :---: | :---: | :---: | :--- |
| **META** | **56.2%** | 39.6% | 4.2% | **Zona Crítica:** Más de la mitad del tiempo en riesgo de quiebre. |
| **CHOCÓ** | **38.3%** | 53.2% | 8.5% | **Vulnerable:** Baja capacidad instalada de almacenamiento. |
| **MAGDALENA** | **31.2%** | 56.2% | 12.5% | **Alta Estacionalidad:** Picos coincidentes con temporadas secas/calurosas. |
| **SUCRE** | **29.2%** | 56.2% | 14.6% | **Fragilidad en Red Periférica.** |
| **CASANARE** | **27.1%** | 62.5% | 10.4% | **Demanda desproporcionada vs Stock.** |
| **CUNDINAMARCA** | 22.9% | 68.8% | 8.3% | Riesgo moderado-alto. |
| **TOLIMA** | 20.8% | 47.9% | 31.2% | Alta endemia pero mayor inventario base. |
| **HUILA** | 18.8% | 52.1% | 29.2% | Control epidemiológico moderado. |
| **PUTUMAYO** | 18.8% | 75.0% | 6.2% | Concentrado en zona de alerta media. |
| **LA GUAJIRA** | 14.6% | 68.8% | 16.7% | Riesgo mitigado por baja pluviosidad. |

---

## 5. Hallazgos Accionables y Recomendaciones de Negocio (20%)

Siguiendo el estándar de evaluación exigido: **Hallazgo + Evidencia Estadística/Gráfica + Acción Sugerida**.

### 📌 Hallazgo 1: Concentración Crítica de Desabastecimiento en Departamentos de la Orinoquía y Pacífico
* **Evidencia Estadística:** El cruce de contingencia (`pd.crosstab`) reveló que **Meta presenta una tasa de riesgo alto del 56.2%** de sus periodos evaluados, seguido por **Chocó con un 38.3%**, a pesar de no ser los departamentos con mayor población absoluta de Colombia.
* **Acción de Negocio / Salud Pública:** El Ministerio de Salud y los operadores logísticos no deben distribuir reservas de medicamentos basándose exclusivamente en el censo poblacional general, sino mediante un **factor de corrección por tasa histórica de presión epidemiológica**, creando un *stock regulador descentralizado* en Villavicencio y Quibdó con 45 días de anticipación al inicio del ciclo de lluvias.

### 📌 Hallazgo 2: Factor Multiplicador Lineal entre Brotes y Demanda Farmacéutica
* **Evidencia Estadística:** La recta de regresión de mínimos cuadrados evidenció un coeficiente de determinación fuerte ($r = 0.848$) con una pendiente de **$m = 12.42$ medicamentos por cada caso reportado**, partiendo de un consumo basal estructural de ~8,700 unidades.
* **Acción de Negocio / Salud Pública:** Configurar un **gatillo de reabastecimiento automático (Trigger Logístico)** en el software de compras hospitalarias: cuando el monitoreo semanal de SIVIGILA detecte que los casos superan el umbral de brote IQR ($>378$ casos en el mes), el sistema debe despachar inmediatamente una orden de compra extraordinaria calculada exactamente como $\Delta \text{Pedidos} = 12.5 \times \text{Casos Estimados}$, evitando compras de pánico tardías a sobrecosto.

### 📌 Hallazgo 3: Naturaleza Leptocúrtica de las Crisis y Justificación de Preprocesamiento
* **Evidencia Estadística:** Los casos reportados presentan un coeficiente de asimetría de **$+3.89$** y una curtosis extrema de **$20.45$**, con 184 periodos catalogados matemáticamente como outliers superiores según la regla de Tukey.
* **Acción de Negocio / Salud Pública:** Prohibir el uso de promedios simples en los comités de planeación presupuestal hospitalaria (que distorsionan las compras hacia arriba en meses de calma y hacia abajo en meses de crisis). En la arquitectura de Machine Learning del proyecto, esto valida de forma irrefutable la adopción de `RobustScaler` (basado en mediana y rango intercuartílico) sobre los datos antes de alimentar el algoritmo `RandomForest`, garantizando que los picos epidémicos no distorsionen los pesos de los árboles de decisión.

---

## 6. Anexos y Reproducibilidad Técnica (5%)

Todo el análisis, cálculos matemáticos y figuras de alta resolución fueron generados mediante el script profesional reproducible:
* **Script Principal:** [`src/03_eda/eda_proyecto.py`](../src/03_eda/eda_proyecto.py)
* **Dataset Fuente:** [`dataset_final_crisp_dm_mejorado.csv`](../datos_procesados/dataset_final_crisp_dm_mejorado.csv)
* **Figuras Exportadas:** Guardadas en formato PNG con resolución para publicación académica en [`datos_procesados/`](../datos_procesados):
  1. `fig1_hist_casos_dengue.png` (Histograma con Media vs Mediana)
  2. `fig2_box_casos_outliers.png` (Boxplot horizontal con regla IQR y detección de brotes)
  3. `fig3_barras_departamentos_eventos.png` (Barras bivariadas ordenadas por frecuencia)
  4. `fig4_scatter_casos_medicamentos.png` (Dispersión y recta de ajuste $y = mx + b$)
  5. `fig5_heatmap_correlaciones.png` (Mapa de calor de correlaciones Pearson RdBu_r)
  6. `fig6_matriz_dispersion.png` (Scatter matrix multivariada con diagonal hist)
  7. `fig7_tasa_riesgo_desabastecimiento.png` (Tasa de riesgo de inventario cruzada por departamento)

### Instrucciones de Ejecución:
```bash
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Opción 1: Ejecutar directamente el módulo EDA
python src/03_eda/eda_proyecto.py

# Opción 2: Ejecutar mediante el orquestador CRISP-DM
python main.py --fase eda
```
El script se ejecuta de forma totalmente autónoma, sin abrir ventanas emergentes bloqueantes (`matplotlib.use('Agg')`), e imprime en consola la bitácora completa de resultados estadísticos.
