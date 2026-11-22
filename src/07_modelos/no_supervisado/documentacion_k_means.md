# Módulo 07 · Aprendizaje No Supervisado (`src/07_modelos/no_supervisado/`)

## 1. Descripción General
Este módulo implementa el algoritmo de agrupamiento **K-Means** sobre el conjunto de datos preprocesado (`dataset_escalado_standard_robust.csv`). El proceso se enfoca en segmentar los registros epidemiológicos y ambientales utilizando tres variables:
* `Casos_Reportados`
* `Temperatura_Promedio`
* `Humedad_Ambiente`

---

## 2. Evaluación y Selección de $k$
Se ejecutó un ciclo iterativo para evaluar valores de $k$ en un rango de 2 a 8, calculando la **Inercia** y el **Coeficiente de Silueta** tras estandarizar las variables con `StandardScaler()`:

| Valor de $k$ | Inercia | Coeficiente de Silueta |
| :---: | :---: | :---: |
| $k=2$ | 127,735 | 0.321 |
| $k=3$ | 89,846 | 0.341 |
| **$k=4$** | **63,937** | **0.375** |
| $k=5$ | 53,971 | 0.351 |
| $k=6$ | 44,957 | 0.363 |
| $k=7$ | 37,718 | 0.365 |
| $k=8$ | 33,504 | 0.364 |

Se configuró el modelo definitivo con **`k_elegido = 4`**, correspondiente al valor con mayor puntaje de silueta ($0.375$).

---

## 3. Entrenamiento y Perfilamiento (`groupby`)
Se entrenó el modelo final (`n_clusters=4`, `n_init=10`, `random_state=42`) y se asignó la etiqueta de clúster a cada registro del DataFrame. Posteriormente, se realizó el conteo de registros y el cálculo de promedios por grupo mediante `groupby`:

| Clúster | Cantidad de Registros | Casos Reportados (Media) | Temperatura Promedio (Media) | Humedad Ambiente (Media) |
| :---: | :---: | :---: | :---: | :---: |
| **0** | 18,211 | 23.3 | 0.5 | 0.8 |
| **1** | 833 | 1006.0 | -0.5 | 0.1 |
| **2** | 16,941 | 41.1 | -1.3 | 0.4 |
| **3** | 23,579 | 31.8 | 0.6 | -0.9 |