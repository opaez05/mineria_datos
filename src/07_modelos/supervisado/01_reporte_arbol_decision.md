# Reporte Técnico · Modelo 01: Árbol de Decisión (`DecisionTreeClassifier`)

> **Script asociado:** [`01_arbol_decision.py`](01_arbol_decision.py)  
> **Base metodológica:** Sesión 7 (*Clasificación I: Árboles de Decisión*, script guía `arbol_fuga.py`)  
> **Variable objetivo (`y`):** `Nivel_Riesgo` (`Riesgo Bajo`, `Riesgo Medio`, `Riesgo Alto`) sobre registros históricos de `DENGUE` ($N = 1,522$; Train = $1,141$ / Test = $381$).

---

## 1. Resumen Ejecutivo del Experimento

El **Árbol de Decisión** evaluó la capacidad de predecir el nivel de estrés del inventario departamental de medicamentos combinando variables epidemiológicas (`Casos_Reportados`), climáticas (`Temperatura_Promedio`, `Lluvias_Acumuladas`, `Humedad_Ambiente`), temporales (`ANO`, `mes`) y territoriales (`Departamento` codificado con `get_dummies`, 34 columnas), **excluyendo estrictamente `Medicamentos_Vendidos`** para evitar fuga de datos.

### Métricas del Modelo Legible Estándar (`max_depth=4`)
| Métrica | Valor Obtenido | Lectura |
| :--- | :---: | :--- |
| **Accuracy Train** | **0.6617** (66.2%) | Aprendizaje controlado sin memorización |
| **Accuracy Test** | **0.6693** (66.9%) | Generaliza ligeramente mejor que en entrenamiento |
| **Brecha (`Train - Test`)** | **-0.0076** | Cero sobreajuste (*overfitting*) |
| **Precision Macro (Test)** | **0.7938** | Alta confiabilidad cuando emite una alerta |
| **Recall Macro (Test)** | **0.4964** | Promedio entre clases afectado por desbalance |
| **F1 Macro (Test)** | **0.5157** | Balance moderado en las tres categorías |
| **Recall en `Riesgo Alto`** | **0.1778** (8 / 45) | Detecta pocos casos críticos por conservadurismo |
| **Tiempo `fit` / `predict`** | `0.0052s` / `0.0008s` | Inferencia prácticamente instantánea |

---

## 2. Diagnóstico de Profundidad y Sobreajuste (`max_depth`)

Siguiendo la metodología de `arbol_fuga.py`, se evaluaron seis profundidades sobre la misma partición estratificada:

| `max_depth` | Accuracy Train | Accuracy Test | Brecha (`Train - Test`) | F1 Macro (Test) | Recall `Riesgo Alto` | Diagnóstico |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `2` | 0.5925 | 0.5748 | 0.0177 | 0.2927 | 0.0000 | Subajuste severo: no logra aislar `Riesgo Alto` |
| `3` | 0.6319 | 0.6220 | 0.0099 | 0.3731 | 0.0000 | Aún corto para separar umbrales por inventario |
| `4` | 0.6617 | 0.6693 | -0.0076 | 0.5157 | 0.1778 | **Punto óptimo de legibilidad** (reglas claras y cero sobreajuste) |
| `5` | 0.6880 | 0.6798 | 0.0082 | 0.5306 | 0.1778 | Mejora marginal manteniendo brecha mínima |
| **`8`** | **0.7318** | **0.7165** | **0.0153** | **0.5961** | **0.2222** | **Máximo desempeño en test** con sobreajuste controlado |
| `sin limite` | **1.0000** | **0.6299** | **0.3701** | 0.5722 | 0.3778 | **Sobreajuste grave**: memorizó el 100% de Train y cayó en Test |

* **Evidencia gráfica:** Ver [`arbol_decision_profundidades.png`](../../../img/modelos/supervisado/arbol_decision_profundidades.png) y [`arbol_decision_dengue.png`](../../../img/modelos/supervisado/arbol_decision_dengue.png).

---

## 3. Reglas Extraídas e Importancia de Variables

### Importancia Relativa (`feature_importances_` con `max_depth=4`)
1. `Casos_Reportados`: **0.3816** (38.2%)
2. `Departamento_VALLE DEL CAUCA`: **0.1523** (15.2%)
3. `Departamento_ANTIOQUIA`: **0.1468** (14.7%)
4. `Departamento_CESAR`: **0.1190** (11.9%)
5. `Departamento_ATLANTICO`: **0.1095** (11.0%)
6. `Departamento_BOLIVAR`: **0.0908** (9.1%)

### Traducción de Reglas (`export_text`) a Lenguaje de Salud Pública
1. **Regla de Alerta Crítica (`Riesgo Alto`):**  
   > *"En departamentos fuera de Antioquia y Valle del Cauca (capacidades de inventario menores a 50,000 unidades), cuando los casos mensuales de Dengue superan **`895.5 casos`**, el territorio entra en **`Riesgo Alto`** de desabastecimiento."*  
   **Acción logística:** Activar compras de emergencia o reabastecimiento interdepartamental inmediato.
2. **Regla de Resiliencia por Stock Instalado (`Riesgo Bajo`):**  
   > *"Departamentos con inventarios robustos como **Antioquia** (80,000 u.) o **Valle del Cauca** (70,000 u. hasta **`1,570.5 casos`**), así como **Cesar, Atlántico y Bolívar** con **`<= 114.5 casos`**, se mantienen en **`Riesgo Bajo`**."*  
   **Acción logística:** Mantener monitoreo rutinario sin movilizar stock de contingencia.

---

## 4. Evaluación Crítica: Matriz de Confusión y Desbalance

Con `max_depth=4` sobre el conjunto Test ($n = 381$):
- **`Riesgo Bajo` (127 reales):** 42 aciertos, 85 clasificados como Medio, **0** como Alto (Precisión `0.955`).
- **`Riesgo Medio` (209 reales):** 205 aciertos (`98.1%` Recall), 2 como Bajo, 2 como Alto.
- **`Riesgo Alto` (45 reales):** **8 aciertos (`17.8%` Recall)**, 37 subestimados como `Riesgo Medio`, **0** subestimados hasta `Riesgo Bajo`.

> [!WARNING]
> **Hallazgo clave de riesgo en salud pública:** Al existir desbalance (`Riesgo Alto` representa solo el 11.9% de los registros), el árbol sin ponderación tiende a clasificar casos altos limítrofes dentro de la clase mayoritaria (`Riesgo Medio`). Cuando se probó `class_weight="balanced"` (con `max_depth=4`), el Accuracy Test bajó a `0.5696`, pero el **Recall en `Riesgo Alto` se triplicó de `0.1778` a `0.5333`**.

---

## 5. Sugerencias Técnicas para el Proyecto (Árbol de Decisión)

1. **Usar `max_depth` entre `5` y `8` para operación y `max_depth=4` para comités:** Si se prioriza precisión global (`71.7%`), `max_depth=8` generaliza mejor sin memorizar (`brecha = 0.0153`); si se requiere explicar reglas en una sola diapositiva o auditoría del Ministerio de Salud, `max_depth=4` es ideal.
2. **Mitigar Falsos Negativos con `class_weight` o umbral de probabilidad:** Para alertas tempranas hospitalarias donde omitir un desabastecimiento es costoso, se sugiere entrenar con `class_weight={ "Riesgo Alto": 2.5, "Riesgo Medio": 1.0, "Riesgo Bajo": 1.0 }` o `min_samples_leaf=5` para equilibrar sensibilidad sin sacrificar tanta precisión global.
3. **Inyectar la capacidad instalada como variable numérica (`inventario_referencia`) o usar `RandomForestClassifier`:** Actualmente el árbol tiene que ir aislando departamento por departamento (`VALLE`, `ANTIOQUIA`, `CESAR`, `ATLANTICO`, `BOLIVAR`) mediante dummies para deducir su inventario. Pasar a un ensamble (`RandomForestClassifier`) reduce la varianza entre ramas y captura simultáneamente las interacciones climáticas (`Humedad`, `Temperatura`, `Lluvias`) que quedaron ocultas en profundidades bajas.

