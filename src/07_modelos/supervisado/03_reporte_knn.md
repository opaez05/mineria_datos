# Reporte Técnico · Modelo 03: K-Vecinos Más Cercanos (`KNeighborsClassifier`)

> **Script asociado:** [`03_knn.py`](03_knn.py)  
> **Base metodológica:** Sesión 8 (*Clasificación II: Naive Bayes y K-Vecinos*, script guía `comparacion_modelos.py`)  
> **Variable objetivo (`y`):** `Nivel_Riesgo` (`Riesgo Bajo`, `Riesgo Medio`, `Riesgo Alto`) sobre registros históricos de `DENGUE` ($N = 1,522$; Train = $1,141$ / Test = $381$).

---

## 1. Resumen Ejecutivo del Experimento

El clasificador **KNN** predice el nivel de riesgo de un registro departamento-mes buscando los $k$ registros históricos más cercanos en el espacio de 40 dimensiones (`ANO`, `mes`, clima, `Casos_Reportados` y 34 dummies de `Departamento`). Los experimentos validaron de manera contundente la regla de la Sesión 8: **"la distancia manda a escalar"**, y mostraron cómo el diseño del espacio de características afecta a la distancia euclidiana frente a Manhattan.

---

## 2. Impacto Crítico del Escalamiento dentro de `Pipeline` (`k=5`)

Cumpliendo la regla de cero fuga de datos (`make_pipeline` ajusta el escalador **únicamente sobre `X_train`**), los resultados fueron:

| Configuración (`k=5`) | Accuracy Train | Accuracy Test | F1 Macro (Test) | Recall `Riesgo Alto` | `t_fit` (s) | `t_predict` (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **KNN SIN escalar (crudo)** | 0.6889 | **0.5171** | 0.4525 | 0.3556 | 0.0030 | 0.0131 |
| `Pipeline(StandardScaler, KNN)` | 0.7739 | **0.6247** | 0.5594 | 0.3556 | 0.0070 | 0.0124 |
| `Pipeline(RobustScaler, KNN)` | 0.7862 | **0.6299** | 0.5601 | 0.3333 | 0.0069 | 0.0133 |
| `Pipeline(MinMaxScaler, KNN)` | 0.7765 | **0.6404** | **0.5815** | **0.4000** | 0.0060 | 0.0142 |

* **Evidencia contundente:** Sin escalamiento, `Casos_Reportados` (rango hasta 2,752), `ANO` (~2017–2021) y `Lluvias_Acumuladas` (hasta 1,090 mm) aplastan por completo al `mes`, a la `Temperatura_Promedio` y a los indicadores de `Departamento`. Escalar dentro del `Pipeline` eleva la exactitud en Test entre **+10.8 y +12.3 puntos porcentuales** (`0.5171` $\rightarrow$ `0.6247` / `0.6404`).

---

## 3. Efecto del Parámetro `k` (Sesgo vs. Varianza)

El barrido de valores impares de $k$ demostró el comportamiento clásico entre memorización y dilución (ver [`knn_curva_k_escalado.png`](../../../img/modelos/supervisado/knn_curva_k_escalado.png)):

### A. Con `Pipeline(RobustScaler, KNN)`
| `k` | Accuracy Train | Accuracy Test | Brecha (`Train - Test`) | F1 Macro | Recall `Riesgo Alto` | Diagnóstico |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `1` | **1.0000** | 0.6325 | **0.3675** | 0.5812 | 0.4000 | **Memorización pura** (sobreajuste máximo) |
| `3` | 0.8037 | 0.6509 | 0.1528 | **0.5984** | **0.4667** | Mayor sensibilidad a brotes locales |
| `5` | 0.7862 | 0.6299 | 0.1562 | 0.5601 | 0.3333 | Estabilidad intermedia |
| **`7`** | 0.7695 | **0.6614** | 0.1081 | 0.5828 | 0.3333 | **Óptimo con `RobustScaler`** |
| `15` | 0.7187 | 0.6457 | 0.0730 | 0.5487 | 0.2667 | Brecha baja, pierde señal crítica |
| `51` | 0.6652 | 0.5827 | 0.0825 | 0.4642 | 0.2222 | Subajuste: vecindario demasiado amplio |
| `101` | 0.6223 | 0.5407 | 0.0816 | 0.4075 | 0.2000 | Dilución casi a la moda global (54.8%) |

### B. Con `Pipeline(StandardScaler, KNN)` (Comparación del curso)
Con `StandardScaler`, el mejor desempeño se alcanzó en **`k=11`**:
- **Accuracy Train:** `0.7388` | **Accuracy Test:** **`0.6824`** | **F1 Macro:** **`0.6126`** | **Recall `Riesgo Alto`:** `0.3556`.

**¿Por qué `StandardScaler` con `k=11` superó a `RobustScaler` con `k=11` (`0.6824` vs `0.6325`)?**  
En nuestra matriz `X` hay **34 columnas binarias `0/1` de `Departamento`**. Para una columna binaria con pocos `1`s, tanto $Q_1$ como $Q_3$ valen `0`, por lo que su $\text{IQR} = 0$ y `RobustScaler` la deja sin escalar (escala = `1.0`), mientras que `StandardScaler` divide por su desviación estándar ($\sigma < 0.2$), amplificando la coincidencia de departamento en la distancia euclidiana. Esto confirma una regla de ingeniería importante: `RobustScaler` debe aplicarse de forma selectiva a variables numéricas continuas con outliers (como hicimos en `src/04_transformacion/escalamiento.py`), no indiscriminadamente a columnas One-Hot.

---

## 4. Variantes Avanzadas (Práctica Independiente de Sesión 8)

Siguiendo la tarea propuesta en la Sesión 8 (`weights="distance"` y métricas de distancia para `k=7`):

| Variante (`k=7`) | Accuracy Train | Accuracy Test | F1 Macro | Recall `Riesgo Alto` | `t_predict` (s) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `RobustScaler + Euclidean + uniform` | 0.7695 | 0.6614 | 0.5828 | 0.3333 | 0.0128 |
| `RobustScaler + Euclidean + distance` | 1.0000 | 0.6614 | 0.5874 | 0.3333 | 0.0130 |
| **`RobustScaler + Manhattan + distance`** | 1.0000 | **0.6772** | **0.6144** | **0.3778** | 0.0155 |
| `StandardScaler + Euclidean + distance` | 1.0000 | 0.6693 | 0.5941 | 0.3111 | 0.0166 |
| `RobustScaler + k=5 + distance (solo 6 numéricas)` | 1.0000 | 0.5643 | 0.4808 | 0.2667 | 0.0071 |

* **Observación de costo en producción:** Aunque `fit` es rápido (`0.004s–0.007s` por ser un algoritmo perezoso/*lazy*), **`predict()` tarda `0.012s–0.019s` en solo 381 filas** (~15 a 20 veces más lento que el Árbol de Decisión y Naive Bayes), porque cada predicción calcula distancias contra las 1,141 filas de entrenamiento.

---

## 5. Sugerencias Técnicas para el Proyecto (KNN)

1. **Aplicar `ColumnTransformer` híbrido dentro del `Pipeline`:** Escalar `Temperatura_Promedio` y `Humedad_Ambiente` con `StandardScaler`, `Lluvias_Acumuladas` y `Casos_Reportados` con `RobustScaler`, y dejar las dummies de `Departamento` (o usar `MinMaxScaler`) para no mezclar $\text{IQR}=0$ con variables continuas.
2. **Usar `metric="manhattan"` y `weights="distance"` en alta dimensionalidad:** Con 40 dimensiones (incluyendo 34 dummies dispersas), la distancia Manhattan (`L1`) mejoró el F1 Macro de `0.5828` a **`0.6144`** y el Recall de `Riesgo Alto` de `0.3333` a **`0.3778`**, mitigando la maldición de la dimensionalidad frente a la norma Euclidiana (`L2`).
3. **Reducir dimensionalidad antes de KNN:** En lugar de 34 columnas One-Hot por departamento, reemplazar `Departamento` por variables continuas significativas (por ejemplo, la capacidad de inventario del departamento o el clúster territorial de la Sesión 9) reduciría el espacio de 40 a ~7 dimensiones densas, mejorando tanto la precisión de los vecindarios como la velocidad de `predict()`.

