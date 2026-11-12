# Reporte Final del Torneo Supervisado y Selección de Modelo

> **Script asociado:** [`04_torneo_comparacion.py`](04_torneo_comparacion.py)  
> **Base metodológica:** Sesión 8 (*Torneo de Clasificadores y Recomendación Técnica*)  
> **Problema de negocio:** Clasificar mensualmente el **`Nivel_Riesgo`** (`Riesgo Bajo`, `Riesgo Medio`, `Riesgo Alto`) de desabastecimiento de medicamentos asociados a **Dengue** en Colombia ($N = 1,522$; Train = $1,141$ / Test = $381$, `random_state=42`, `stratify=y`).

---

## 1. Tabla Comparativa Oficial del Torneo

Los tres algoritmos compitieron bajo **exactamente la misma partición estratificada** y sin fuga de datos (`Medicamentos_Vendidos` excluida de `X`).

### Ronda A · Configuraciones Estándar del Curso (Sesión 8)
| Modelo | Acc Train | Acc Test | Brecha | Precision Macro | Recall Macro | F1 Macro | Recall `Riesgo Alto` | `t_fit` (s) | `t_pred` (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Árbol de Decisión (`max_depth=4`)** | 0.6617 | **0.6693** | **-0.0076** | **0.7938** | 0.4964 | 0.5157 | 0.1778 | 0.0056 | **0.0009** |
| **Naive Bayes (`GaussianNB`)** | 0.5127 | 0.4593 | 0.0534 | 0.5250 | **0.5591** | 0.4585 | **0.7556** | **0.0036** | 0.0011 |
| **KNN (`StandardScaler, k=5`)** | 0.7739 | 0.6247 | 0.1492 | 0.5796 | 0.5467 | 0.5594 | 0.3556 | 0.0051 | 0.0165 |
| **KNN (`RobustScaler, k=5`)** | 0.7862 | 0.6299 | 0.1562 | 0.5874 | 0.5451 | **0.5601** | 0.3333 | 0.0160 | 0.0190 |

### Ronda B · Mejores Configuraciones Exploradas por Familia
| Modelo | Acc Train | Acc Test | Brecha | Precision Macro | Recall Macro | F1 Macro | Recall `Riesgo Alto` | `t_fit` (s) | `t_pred` (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Árbol de Decisión (`max_depth=8`)** | 0.7318 | **0.7165** | **0.0153** | **0.7682** | 0.5636 | 0.5961 | 0.2222 | 0.0094 | 0.0012 |
| **Árbol Balanceado (`max_depth=4, balanced`)** | 0.6512 | 0.5696 | 0.0816 | 0.5391 | 0.5268 | 0.5004 | **0.5333** | 0.0065 | **0.0008** |
| **Naive Bayes (`var_smoothing=1e-3`)** | 0.5942 | 0.5381 | 0.0562 | 0.4767 | 0.4529 | 0.4535 | 0.3556 | **0.0028** | 0.0009 |
| **KNN (`StandardScaler, k=11`)** | 0.7388 | 0.6824 | 0.0564 | 0.6776 | 0.5849 | 0.6126 | 0.3556 | 0.0042 | 0.0169 |
| **KNN (`RobustScaler + Manhattan + dist, k=7`)** | 1.0000 | 0.6772 | 0.3228 | 0.6761 | **0.5865** | **0.6144** | 0.3778 | 0.0078 | 0.0190 |

* **Evidencia visual:** [`torneo_comparacion_metricas.png`](../../../img/modelos/supervisado/torneo_comparacion_metricas.png) y [`torneo_matrices_confusion.png`](../../../img/modelos/supervisado/torneo_matrices_confusion.png).

---

## 2. Veredicto: Modelo Escogido

### 🏆 Ganador Seleccionado: **Árbol de Decisión (`DecisionTreeClassifier`)**
*(Configuración operativa recomendada: **`max_depth=8`** para máxima exactitud general (`0.7165`), complementado con **`max_depth=4`** cuando se requiera lectura directa en comité o auditoría logística).*

---

## 3. Justificación Integral de la Elección

Siguiendo los criterios de la Sesión 8 (desempeño en test, control de sobreajuste, explicabilidad, robustez ante la naturaleza de los datos y costo operativo), el **Árbol de Decisión** supera a **KNN** y **Naive Bayes** por cinco razones concretas y verificadas:

### 1. Mejor Desempeño Predictivo y Cero Sobreajuste
* En la **Ronda Estándar** (reglas de la Sesión 8), el Árbol (`max_depth=4`) alcanzó el mayor Accuracy Test (**`0.6693`**) frente a KNN (`0.6247` / `0.6299`) y Naive Bayes (`0.4593`), con una **brecha negativa de `-0.0076`** (mientras que KNN `k=5` mostró una brecha de sobreajuste de `~0.15`).
* En la **Ronda Optimizada**, el Árbol (`max_depth=8`) volvió a liderar con **`0.7165` de Accuracy Test** (+3.4 puntos por encima del mejor KNN `k=11` con `0.6824`, y +17.8 puntos por encima del mejor Naive Bayes con `0.5381`), manteniendo una brecha de generalización muy sana (`0.0153`).

### 2. Interpretabilidad y Trazabilidad en Salud Pública (Factor Decisivo)
* En gestión hospitalaria y prevención de desabastecimiento ante entidades como el **Ministerio de Salud o Secretarías Departamentales**, no basta con decir *"este departamento está en riesgo"*; hay que justificar **por qué** activar compras de emergencia o traslados de stock.
* El **Árbol de Decisión** entrega reglas explícitas auditables con umbrales exactos (ej.: `Casos_Reportados > 895.5` en departamentos de menor capacidad instalada $\rightarrow$ `Riesgo Alto`), mientras que Naive Bayes opera sobre productos de verosimilitudes gaussianas opacas y KNN únicamente responde por similitud geométrica en 40 dimensiones.
* Además, en su matriz de confusión (`max_depth=8`), el Árbol cometió **cero errores catastróficos** de clasificar un `Riesgo Alto` real como `Riesgo Bajo` (`0` de `45`), cosa que sí ocurrió en KNN (`2` de `45`) y Naive Bayes (`3` de `45`).

### 3. Inmunidad Natural ante Escalas Dispares y Outliers Epidémicos
* Como demostramos en la Fase 2 y Fase 3 (`escalamiento.py`), `Casos_Reportados` (asimetría $+3.89$) y `Lluvias_Acumuladas` (asimetría $+1.94$) tienen colas pesadas por brotes epidémicos reales y departamentos del Pacífico.
* El Árbol realiza particiones por umbrales invariantes a transformaciones monótonas de escala; **no se distorsiona** por las escalas ni por el $\text{IQR}=0$ de las 34 columnas binarias de departamento (problema que sí afectó a `RobustScaler` y `StandardScaler` en KNN y colapsó a `GaussianNB` hasta `0.3071` al escalar).

### 4. Descarte Técnico de Naive Bayes y KNN como Modelos Principales
* **Por qué no se eligió Naive Bayes:** Obtuvo la peor exactitud global (`0.4593`), violó el supuesto de normalidad (34 dummies `0/1` + casos asimétricos) y el de independencia (`Lluvias` y `Humedad` tienen $r = 0.712$). Además, su auditoría demostró **calibración crítica deficiente**: el **`93.2%` de sus errores (`192` de `206`) se emitieron con confianza $\ge 90\%$**, lo que lo vuelve peligroso para decisiones presupuestales automatizadas, aunque útil como *baseline* rápido.
* **Por qué no se eligió KNN:** Aunque con `StandardScaler` (`k=11`, `0.6824`) o distancia Manhattan (`k=7`, `0.6772`, `F1=0.6144`) fue un competidor sólido, exige un `Pipeline` sensible a las 34 dimensiones dispersas, carece de reglas explicables y su tiempo de inferencia (`0.0169s–0.0190s` en solo 381 registros) es **~15 veces más lento** que el del Árbol (`0.0009s–0.0012s`) por tener que recorrer el histórico en cada predicción.

### 5. Coherencia con la Arquitectura del Proyecto y Escalabilidad Futura
* El Árbol de Decisión elegido valida y conecta de forma natural con la arquitectura ya construida en [`src/05_modelado/`](../05_modelado/probar_modelo_desabastecimiento.py) y [`docs/README_arbol_decision_prediccion.md`](../../../docs/README_arbol_decision_prediccion.md), donde un solo árbol explica las reglas clínicas y un **ensamble de múltiples árboles (`Random Forest`)** reduce la varianza restante y mejora la detección de interacciones climáticas.

---

## 4. Limitaciones Honestas del Ganador y Próximos Pasos

1. **Sensibilidad en la clase minoritaria (`Riesgo Alto`, 11.9%):** El Árbol estándar prioriza exactitud global y obtiene un Recall de `0.2222` (`prof=8`) o `0.1778` (`prof=4`) en `Riesgo Alto`. **Mitigación inmediata:** ajustar pesos de clase (`class_weight="balanced"` elevó el Recall Alto a `0.5333`) o evolucionar a `RandomForestClassifier` / `GradientBoosting` con ajuste de umbral de decisión.
2. **Conexión con la Sesión 9 (Clustering No Supervisado):** En lugar de usar 34 columnas dummy dispersas de `Departamento`, el siguiente paso del curso consiste en aplicar **K-Means + Dendrograma jerárquico** para agrupar los departamentos por su perfil climático-epidemiológico y añadir la columna `segmento` al modelo supervisado, mejorando tanto su capacidad de generalización como su simplicidad.

