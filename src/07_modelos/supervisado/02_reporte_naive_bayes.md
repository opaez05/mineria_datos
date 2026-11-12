# Reporte Técnico · Modelo 02: Naive Bayes (`GaussianNB`)

> **Script asociado:** [`02_naive_bayes.py`](02_naive_bayes.py)  
> **Base metodológica:** Sesión 8 (*Clasificación II: Naive Bayes y K-Vecinos*, script guía `comparacion_modelos.py`)  
> **Variable objetivo (`y`):** `Nivel_Riesgo` (`Riesgo Bajo`, `Riesgo Medio`, `Riesgo Alto`) sobre registros históricos de `DENGUE` ($N = 1,522$; Train = $1,141$ / Test = $381$).

---

## 1. Resumen Ejecutivo del Experimento

Se implementó **`GaussianNB()`** bajo la misma partición estratificada del proyecto para evaluar un modelo probabilístico ligero como línea base (*baseline*). A diferencia de `TelecomUNO` (donde obtuvo `0.830` en test), en nuestro problema multiclase con 40 columnas (6 numéricas asimétricas + 34 dummies binarias), Naive Bayes sufrió fuertemente por el incumplimiento de sus supuestos estadísticos.

### Métricas del Modelo Base (`GaussianNB` sin escalar)
| Métrica | Valor Obtenido | Lectura |
| :--- | :---: | :--- |
| **Accuracy Train** | **0.5127** (51.3%) | Ajuste global bajo (menor incluso que predecir siempre la moda 54.8%) |
| **Accuracy Test** | **0.4593** (45.9%) | Desempeño deficiente como clasificador general |
| **Brecha (`Train - Test`)** | **0.0534** | Varianza moderada |
| **Precision Macro (Test)** | **0.5250** | Baja precisión en `Riesgo Alto` (`0.192`) |
| **Recall Macro (Test)** | **0.5591** | Impulsado por sobre-predicción de `Riesgo Alto` |
| **F1 Macro (Test)** | **0.4585** | El menor F1 entre las familias evaluadas |
| **Recall en `Riesgo Alto`** | **0.7556** (34 / 45) | Detecta 3 de cada 4 crisis, pero a costa de demasiadas falsas alarmas |
| **Tiempo `fit` / `predict`** | `0.0043s` / `0.0011s` | Entrenamiento más rápido del torneo |

---

## 2. Diagnóstico de Matriz de Confusión y Comportamiento

En Test ($n = 381$), según [`naive_bayes_confusion.png`](../../../img/modelos/supervisado/naive_bayes_confusion.png):
- **`Riesgo Bajo` (127 reales):** 80 aciertos (`63.0%`), 19 predichos como Medio, **28 falsas alarmas como `Riesgo Alto`**.
- **`Riesgo Medio` (209 reales):** apenas 61 aciertos (`29.2%`), 33 como Bajo y **115 falsas alarmas como `Riesgo Alto`**.
- **`Riesgo Alto` (45 reales):** 34 aciertos (`75.6%`), 8 como Medio y 3 subestimados como Bajo.

**Interpretación:** `GaussianNB` predijo `Riesgo Alto` para **177 de los 381 casos (46.5% del Test)** cuando en la realidad solo representan el 11.8%. En logística hospitalaria, activar compras de emergencia en casi la mitad del país cada mes destruiría el presupuesto y generaría fatiga de alertas.

---

## 3. Auditoría de Supuestos Teóricos en Nuestro Dataset

Los experimentos de [`02_naive_bayes.py`](02_naive_bayes.py) confirmaron exactamente las tres advertencias de la Sesión 8:

### A. Ruptura de Calibración de Probabilidades (`predict_proba`)
- **Confianza promedio en aciertos:** `0.9820` (98.2%)
- **Confianza promedio en errores:** **`0.9758` (97.6%)**
- **Errores con probabilidad $\ge 90\%$:** **`192` de `206` errores (`93.2%`)**

Como muestra [`naive_bayes_probabilidades.png`](../../../img/modelos/supervisado/naive_bayes_probabilidades.png), casi todas las predicciones (correctas o incorrectas) salen con probabilidades cercanas al 98–100%. Es un ejemplo empírico claro de que `GaussianNB` **no debe usarse para reportar probabilidades calibradas de desabastecimiento**.

### B. Impacto de Variables Dispersas (Dummies) y Correlación
| Variante Evaluada | Accuracy Train | Accuracy Test | F1 Macro | Recall `Riesgo Alto` |
| :--- | :---: | :---: | :---: | :---: |
| `GaussianNB crudo (default)` | 0.5127 | 0.4593 | 0.4585 | **0.7556** |
| `Pipeline(StandardScaler, GNB)` | 0.3243 | 0.3071 | 0.3247 | 0.8000 |
| `Pipeline(RobustScaler, GNB)` | 0.3243 | 0.3071 | 0.3247 | 0.8000 |
| `Pipeline(PowerTransformer, GNB)` | 0.3243 | 0.3071 | 0.3247 | 0.8000 |
| `GaussianNB (var_smoothing=1e-3)` | **0.5942** | 0.5381 | 0.4535 | 0.3556 |
| `GaussianNB (var_smoothing=1e-1)` | 0.5653 | **0.5643** | 0.3664 | 0.3333 |
| **`GaussianNB (solo 6 numéricas)`** | 0.5793 | 0.5249 | **0.4766** | 0.4222 |

**¿Por qué ocurrió esto?**
1. **34 dummies binarios (`0/1`) en `GaussianNB`:** Las variables One-Hot de `Departamento` no siguen una campana de Gauss; en departamentos poco frecuentes tienen varianza minúscula, por lo que multiplicar 34 densidades gaussianas casi nulas produce desbordamientos de verosimilitud y explica por qué escalarlas antes de `GaussianNB` empeoró el accuracy a `0.3071` (al cambiar el cálculo de `var_smoothing` relativo a la varianza máxima).
2. **Doble conteo por colinealidad:** En nuestro EDA (Sesión 5) demostramos que `Lluvias_Acumuladas` y `Humedad_Ambiente` tienen correlación de Pearson $r = 0.712$. Naive Bayes asume que son independientes y multiplica ambas evidencias dos veces.
3. **Asimetría extrema:** `Casos_Reportados` tiene asimetría $+3.89$ y curtosis $+20.45$, lejos de la normalidad que exige `GaussianNB`.

---

## 4. Sugerencias Técnicas para el Proyecto (Naive Bayes)

1. **Mantenerlo únicamente como línea base (*baseline*) de referencia rápida:** Su tiempo de entrenamiento (`0.0043s`) permite detectar de inmediato si un modelo más complejo realmente aporta valor sobre el azar/frecuencias marginales.
2. **Si se utiliza Naive Bayes en este dataset, separar tipos de variables o usar `var_smoothing` alto:** Eliminar las 34 columnas One-Hot de `Departamento` elevó el Accuracy Test de `0.4593` a **`0.5249`** y el F1 Macro a **`0.4766`**. Alternativamente, usar `CategoricalNB` para `Departamento` + `mes` y `GaussianNB` solo para variables climáticas transformadas (`log1p` en `Casos_Reportados` y `Lluvias_Acumuladas`), combinando sus verosimilitudes.
3. **No basar decisiones presupuestarias en sus probabilidades crudas:** Dado que el `93.2%` de sus errores ocurren con confianza $\ge 90\%$, si se usara para priorización, debe aplicarse calibración posterior (`CalibratedClassifierCV`) o emplearse solo para ordenar departamentos de mayor a menor riesgo relativo.

