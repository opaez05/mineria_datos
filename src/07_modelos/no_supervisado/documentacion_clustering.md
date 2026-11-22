# Módulo 07 · Aprendizaje No Supervisado (`src/07_modelos/no_supervisado/`)


## 1. Descripción General
Este módulo ejecuta un agrupamiento jerárquico aglomerativo utilizando las funciones `linkage` y `dendrogram` de la librería `scipy.cluster.hierarchy` sobre el archivo `dataset_escalado_standard_robust.csv`.

---

## 2. Procesamiento Realizado
1. **Selección de Variables y Muestreo:** Se seleccionaron las columnas `Casos_Reportados`, `Temperatura_Promedio` y `Humedad_Ambiente`, y se extrajo una muestra aleatoria de **60 registros** (`random_state=42`) para permitir la visualización del árbol.
2. **Escalado y Matriz de Enlace:** Se aplicó `StandardScaler()` sobre la muestra y se calculó la matriz de enlace (`Z`) empleando el método de varianza mínima de **Ward** (`method="ward"`).
3. **Extracción de Métricas y Visualización:** Se imprimieron en consola las distancias de las primeras cinco fusiones y de la última unión, y se generó la gráfica del dendrograma guardándola en el archivo `dendrograma.png`.

---

## 3. Resultados Obtenidos
* **Última fusión registrada:** Distancia de Ward igual a **9.4**.
* **Salida gráfica:** Archivo `dendrograma.png` con la representación jerárquica de las 60 muestras agrupadas según su similitud.