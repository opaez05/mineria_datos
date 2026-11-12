# Módulo 07 · Aprendizaje Supervisado (`src/07_modelos/supervisado/`)

Este módulo implementa el **Torneo Oficial de Clasificación Supervisada** correspondiente a las **Sesiones 7 y 8** del curso de Minería de Datos, aplicado al proyecto integrado de **Predicción de Brotes de Dengue y Riesgo de Desabastecimiento de Medicamentos en Colombia**.

---

## 1. Estructura y Orden de Ejecución

| Orden | Archivo | Propósito | Referencia de Clase |
| :---: | :--- | :--- | :--- |
| **00** | [`00_preparacion_supervisado.py`](00_preparacion_supervisado.py) | Auditoría de calidad (`DENGUE`, $N=1,522$), construcción del target `Nivel_Riesgo` sin fuga de datos, codificación `get_dummies` y partición única compartida (`75%/25%`, `random_state=42`, `stratify=y`). | Regla de oro de comparabilidad (Sesiones 7–8) |
| **01** | [`01_arbol_decision.py`](01_arbol_decision.py) | Entrenamiento de `DecisionTreeClassifier`, barrido de `max_depth` (`2..None`), extracción de reglas (`export_text`), importancia de variables, gráfica del árbol y prueba con `class_weight="balanced"`. | Sesión 7 (`arbol_fuga.py`) |
| **01R** | [`01_reporte_arbol_decision.md`](01_reporte_arbol_decision.md) | Análisis de sobreajuste, traducción de reglas al negocio y sugerencias técnicas del Árbol de Decisión. | Informe técnico Modelo 1 |
| **02** | [`02_naive_bayes.py`](02_naive_bayes.py) | Entrenamiento de `GaussianNB()`, auditoría de calibración de probabilidades (`predict_proba`), verificación de invariancia al escalamiento y sensibilidad a `var_smoothing`. | Sesión 8 (`comparacion_modelos.py`) |
| **02R** | [`02_reporte_naive_bayes.md`](02_reporte_naive_bayes.md) | Análisis de supuestos estadísticos (colinealidad clima/no gaussianidad), sobreconfianza y sugerencias técnicas de Naive Bayes. | Informe técnico Modelo 2 |
| **03** | [`03_knn.py`](03_knn.py) | Entrenamiento de `KNeighborsClassifier` dentro de `make_pipeline` (comparando sin escalar vs `StandardScaler`, `RobustScaler`, `MinMaxScaler`), barrido de `k`, `weights="distance"`, Manhattan y tiempos `fit/predict`. | Sesión 8 (`comparacion_modelos.py`) |
| **03R** | [`03_reporte_knn.md`](03_reporte_knn.md) | Análisis de escalado en alta dimensionalidad (40 features), elección de `k` y sugerencias técnicas de KNN. | Informe técnico Modelo 3 |
| **04** | [`04_torneo_comparacion.py`](04_torneo_comparacion.py) | Torneo unificado de los 3 clasificadores (Ronda Estándar de Sesión 8 y Ronda Optimizada) con métricas completas y matrices de confusión comparadas. | Sesión 8 (Torneo final) |
| **04R** | [`04_seleccion_modelo_final.md`](04_seleccion_modelo_final.md) | **Veredicto final:** tabla comparativa consolidada, modelo seleccionado (**Árbol de Decisión**) y justificación técnica, operativa y de interpretabilidad. | Decisión final del módulo |

---

## 2. Cómo Ejecutar los Scripts

Desde la raíz del repositorio (`PROYECTO/`):

```powershell
# 0. Verificar auditoría y partición única compartida
.\.venv\Scripts\python.exe src/07_modelos/supervisado/00_preparacion_supervisado.py

# 1. Ejecutar Modelo 1: Árbol de Decisión
.\.venv\Scripts\python.exe src/07_modelos/supervisado/01_arbol_decision.py

# 2. Ejecutar Modelo 2: Naive Bayes
.\.venv\Scripts\python.exe src/07_modelos/supervisado/02_naive_bayes.py

# 3. Ejecutar Modelo 3: KNN
.\.venv\Scripts\python.exe src/07_modelos/supervisado/03_knn.py

# 4. Ejecutar Torneo Comparativo Final
.\.venv\Scripts\python.exe src/07_modelos/supervisado/04_torneo_comparacion.py
```

---

## 3. Gráficas Generadas

Todas las evidencias visuales se exportan automáticamente en [`img/modelos/supervisado/`](../../../img/modelos/supervisado):
- `arbol_decision_profundidades.png` · Curva de sobreajuste Train vs Test por `max_depth`.
- `arbol_decision_dengue.png` · Diagrama visual completo del árbol podado (`max_depth=4`).
- `arbol_decision_confusion.png` · Matriz de confusión del Árbol de Decisión.
- `naive_bayes_probabilidades.png` · Auditoría de sobreconfianza en `predict_proba`.
- `naive_bayes_confusion.png` · Matriz de confusión de `GaussianNB`.
- `knn_curva_k_escalado.png` · Curva de desempeño de KNN según el número de vecinos `k`.
- `knn_confusion.png` · Matriz de confusión de KNN (`RobustScaler, k=7`).
- `torneo_comparacion_metricas.png` · Comparativa lado a lado (Ronda Estándar y Ronda Optimizada).
- `torneo_matrices_confusion.png` · Comparativa de matrices de confusión del mejor representante por familia.

---

## 4. Síntesis del Veredicto

* **Modelo ganador:** **Árbol de Decisión (`DecisionTreeClassifier`)** — líder tanto en la Ronda Estándar (`max_depth=4`, **0.6693** Acc Test, brecha `-0.0076`) como en la Ronda Optimizada (`max_depth=8`, **0.7165** Acc Test, `0` errores graves de `Riesgo Alto` clasificados como `Riesgo Bajo`), con reglas auditables en salud pública e inferencia instantánea (`~0.001s`).
* El detalle completo y las razones de descarte de KNN y Naive Bayes se documentan en [`04_seleccion_modelo_final.md`](04_seleccion_modelo_final.md).

