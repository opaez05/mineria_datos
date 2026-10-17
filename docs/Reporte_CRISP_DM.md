# Reporte de Auditoría y Propuesta de Mejora: Proyecto de Minería de Datos (CRISP-DM)

Este documento presenta un análisis crítico del estado actual de tu proyecto bajo las primeras tres fases de la metodología **CRISP-DM** (Comprensión del Negocio, Comprensión de los Datos y Preparación de los Datos), junto con propuestas concretas para mejorar la calidad y validez del proyecto de cara a tu presentación académica.

---

## 📊 Estado Actual del Proyecto y Diagnóstico

Actualmente, el proyecto integra tres fuentes de datos:
1. **SIVIGILA (Salud Pública)**: Casos de eventos epidemiológicos por semana y departamento/municipio.
2. **IDEAM (Clima)**: Mediciones de sensores climáticos (temperatura, precipitación, humedad, etc.).
3. **SISMED (Medicamentos)**: Mediciones de comercialización de medicamentos.

### 🚨 Hallazgos Críticos (Zonas de Riesgo Académico)

1. **Uso de Datos Sintéticos para SISMED (Crítico)**:
   * **Problema**: En [`analisis_inicial.py`](file:///c:/Users/oscar/Documents/octavo_semestre/mineria_datos/analisis_inicial.py#L13-L16), los datos de medicamentos se generan aleatoriamente usando `np.random.randint(45000, 95000, size=12)`.
   * **Impacto**: Un proyecto de minería de datos pierde validez si una de las variables principales (e.g., demanda de medicamentos) es completamente aleatoria. Los algoritmos de modelado posterior solo encontrarán ruido o patrones falsos.
2. **Pérdida de Resolución Espacial en el Clima**:
   * **Problema**: Agrupas los datos del IDEAM únicamente por `mes` nacional: `df_ideam.groupby(['mes', 'DescripcionSensor'])['ValorObservado'].mean()`.
   * **Impacto**: Colombia es un país con una diversidad climática extrema. Promediar la temperatura de Bogotá (frío) con la de Barranquilla o Chocó (cálido/lluvioso) a nivel nacional genera un "clima promedio nacional" que no representa la realidad de ningún lugar. Las enfermedades ocurren localmente (e.g., el Dengue ocurre en zonas cálidas y húmedas).
3. **Aproximación Temporal de Semanas a Meses Imprecisa**:
   * **Problema**: El cálculo `((df_sivigila['SEMANA'] - 1) // 4) + 1` asume que todos los meses tienen exactamente 4 semanas (28 días). Esto significa que un año tendría 48 semanas en lugar de 52, y las semanas 49 a 52 son forzadas ("clipped") al mes 12.
   * **Impacto**: Distorsiona la estacionalidad de los eventos epidemiológicos, especialmente en los meses de noviembre y diciembre.

---

## 🛠️ Plan de Mejoras Propuesto (Paso a Paso por Fase)

### FASE 01: Comprensión del Negocio (Business Understanding)
* **Definición del Problema Real**:
  * Necesitas plantear una pregunta de negocio clara. Por ejemplo: *¿Cómo influyen las anomalías climáticas (temperatura y lluvia) en el aumento de casos de enfermedades de transmisión vectorial (como el Dengue) y cómo impacta esto la comercialización de medicamentos relacionados en cada departamento?*
* **Objetivo de Minería de Datos**:
  * Definir qué tipo de modelo se usará (e.g., Regresión para predecir casos, Clasificación para alertar sobre brotes, o Correlaciones temporales para logística de medicamentos).

### FASE 02: Comprensión de los Datos (Data Understanding)
* **Exploración de Datos Reales (EDA)**:
  * Presentar estadísticas descriptivas reales: número de registros, valores nulos, distribución de las temperaturas e histogramas de los eventos epidemiológicos más comunes.
  * **Integración de Históricos**: En lugar de usar solo SIVIGILA 2021, puedes consolidar la serie temporal concatenando los archivos de 2017, 2018, 2019 y 2021 que ya tienes en la carpeta [`datos`](file:///c:/Users/oscar/Documents/octavo_semestre/mineria_datos/datos).

### FASE 03: Preparación de los Datos (Data Preparation)

Para que el dataset final sea metodológicamente correcto, sugerimos los siguientes cambios en la lógica de preparación:

#### 1. Mapeo Temporal Preciso
En lugar de dividir semanas por 4, utiliza una función que convierta el año y la semana epidemiológica a una fecha o mes real utilizando el estándar ISO:
```python
# Mapeo preciso usando la fecha de notificación si está disponible,
# o calculando la fecha del lunes de esa semana epidemiológica.
df_sivigila['Fecha'] = pd.to_datetime(df_sivigila['ANO'].astype(str) + '-W' + df_sivigila['SEMANA'].astype(str) + '-1', format='%G-W%V-%u', errors='coerce')
df_sivigila['mes'] = df_sivigila['Fecha'].dt.month
```

#### 2. Agrupación Espacio-Temporal (Departamento + Mes)
Normaliza los nombres de los departamentos en ambos datasets (eliminando tildes y pasando a mayúsculas) y realiza la unión cruzando por **Departamento y Mes**, no solo por Mes:
```python
# Ejemplo de normalización
df_sivigila['Departamento_ocurrencia'] = df_sivigila['Departamento_ocurrencia'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
df_ideam['Departamento'] = df_ideam['Departamento'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

# Agrupar clima por departamento y mes
df_clima_dept = df_ideam.groupby(['Departamento', 'mes', 'DescripcionSensor'], as_index=False)['ValorObservado'].mean()
```

#### 3. Sustitución de Datos Sintéticos en SISMED
* Si no cuentas con un dataset de ventas de medicamentos detallado por mes en el archivo [`SISMED_LABORATORIOS.csv`](file:///c:/Users/oscar/Documents/octavo_semestre/mineria_datos/datos/SISMED_LABORATORIOS.csv) (que parece ser un catálogo de entidades), te sugerimos:
  * Explicar esta limitación en el documento (es totalmente válido en proyectos académicos declarar limitaciones de acceso a datos).
  * Crear un modelo de simulación más realista basado en reglas lógicas (e.g., las unidades vendidas de medicamentos para el dengue son directamente proporcionales a los casos reportados con un desfase de 1 semana, más un ruido controlado), en lugar de números completamente aleatorios.

---

## 📋 ¿Cómo Procedemos?

¿Deseas que implementemos estas mejoras directamente en un nuevo script estructurado (e.g., `preparacion_datos_mejorado.py`) que:
1. Concatene los años de SIVIGILA (2017, 2018, 2019, 2021).
2. Corrija el mapeo de semanas a meses.
3. Agrupe el clima por Departamento y Mes en lugar de promedio nacional.
4. Genere una simulación de SISMED coherente y justificada con los casos de salud pública.

Dime si te gustaría este enfoque o si prefieres ajustar algún aspecto de la propuesta.
