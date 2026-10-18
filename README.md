# Predicción de Brotes Epidemiológicos y Prevención de Desabastecimiento de Medicamentos

Este proyecto de minería de datos tiene como objetivo analizar la correlación entre factores climáticos (temperatura, precipitación y humedad) y la ocurrencia de eventos epidemiológicos (como el Dengue y la Malaria) en los diferentes departamentos de Colombia. Con esta información, el sistema estima la demanda de medicamentos asociados para alertar de forma temprana sobre posibles riesgos de desabastecimiento.

El desarrollo sigue la metodología estándar **CRISP-DM** (implementado formalmente en sus fases de **Comprensión del Negocio, Comprensión de los Datos (EDA), Preparación/Escalamiento y Modelado Predictivo con Machine Learning**, contando adicionalmente con validación prospectiva de escenarios futuros 2027 y módulos de prototipado geoespacial).

---

## 📋 Estructura del Proyecto

El repositorio adopta el estándar **CRISP-DM** modular desacoplado en capas de ingeniería:

```text
PROYECTO/
│
├── main.py                               # Orquestador maestro único del pipeline
├── README.md                             # Guía general de instalación y ejecución
├── requirements.txt                      # Dependencias del proyecto
│
├── src/                                  # CÓDIGO FUENTE MODULARIZADO POR FASES CRISP-DM
│   ├── 01_ingesta/                       # Fase 1: Auditoría y calidad de datos crudos
│   │   ├── analisis_inicial.py
│   │   └── obtener_sismed_filtrado.py
│   ├── 02_preparacion/                   # Fase 2: Integración y limpieza SIVIGILA + IDEAM + SISMED
│   │   └── preparacion_datos_mejorado.py
│   ├── 03_eda/                           # Fase 2 (Entendimiento): Análisis Exploratorio de Datos (Sesión 5)
│   │   └── eda_proyecto.py
│   ├── 04_transformacion/                # Fase 3 (Preparación): Escalamiento StandardScaler + RobustScaler
│   │   ├── escalamiento.py
│   │   └── transformacion.py
│   └── 05_modelado/                      # Fase 4 & 5 (Modelado y Evaluación): ML RandomForest y Pronósticos 2027
│       ├── probar_modelo_desabastecimiento.py
│       └── prediccion_futura_2027.py
│
├── scripts/                              # MÓDULO DE EXPERIMENTACIÓN Y EXTENSIONES FUTURAS
│   ├── ejemplo_mapa.py                   # Prototipo de georreferenciación interactiva (Plotly Express)
│   ├── descarga_nasa.py                  # Conector de datos satelitales climáticos (NASA POWER API)
│   ├── espiar_sismed.py                  # Utilitario de auditoría de catálogos SISMED
│   └── prueba.py                         # Pruebas unitarias y de integración
│
├── docs/                                 # DOCUMENTACIÓN TÉCNICA Y ACADÉMICA
│   ├── index.md                          # Índice general de documentación
│   ├── eda_sesion5.md                    # Guía técnica de la Sesión 5 (EDA)
│   ├── Reporte_EDA_Sesion5.md            # Informe formal de laboratorio (Rúbrica PEA)
│   └── Reporte_CRISP_DM.md               # Informe de auditoría CRISP-DM Fases 1 a 4
│
├── datos/                                # CAPA BRONZE: Fuentes crudas inmutables
└── datos_procesados/                     # CAPA SILVER & GOLD: Datasets y artefactos derivados
    ├── dataset_final_crisp_dm_mejorado.csv   # Dataset integrado (Silver)
    ├── dataset_escalado_standard_robust.csv  # Dataset escalado (Gold)
    ├── figuras/                          # Gráficas generadas organizadas por fase
    └── reportes/                         # Reportes y métricas exportadas
```

---

## 🛠️ Guía de Instalación y Uso

Sigue estos pasos para clonar, instalar y ejecutar el proyecto en tu máquina local:

### 1. Clonar el Repositorio
Abre tu terminal (PowerShell, Git Bash o CMD) y clona el proyecto:
```bash
git clone <URL_DE_TU_REPOSITORIO>
cd mineria_datos
```

### 2. Configurar el Entorno Virtual
Crea un entorno virtual de Python para aislar las dependencias del proyecto:

**En Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**En Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar las Dependencias
Con el entorno virtual activado, instala todas las librerías necesarias:
```bash
pip install -r requirements.txt
```

---

## 🚀 Flujo de Ejecución

El proyecto ofrece dos modalidades de ejecución:

### Opción A: Ejecución Unificada con Orquestador Maestro (Recomendado)
Puedes auditar el estado del linaje de datos, correr el pipeline completo de punta a punta o ejecutar cualquier fase individual sin memorizar scripts:

```bash
# Ver estado actual de datos y artefactos
python main.py --status

# Ejecutar el pipeline completo de principio a fin (End-to-End)
python main.py --all

# O ejecutar una fase puntual para defenderla en clase:
python main.py --fase eda          # Sesión 5: Análisis Exploratorio de Datos
python main.py --fase escalamiento # Fase 3: Escalamiento StandardScaler + RobustScaler
python main.py --fase modelado     # Fase 4: Modelo RandomForest y alertas
python main.py --fase prediccion   # Fase 5: Inferencia futura año 2027
```

---

### Opción B: Ejecución Manual Paso a Paso (Modular en `src/`)

Si deseas inspeccionar o correr cada fase individualmente desde su módulo en `src/`:

#### Paso 1: Auditoría Inicial de Datos
```bash
python src/01_ingesta/analisis_inicial.py
```

#### Paso 2: Análisis de Calidad y Estructura (SISMED)
```bash
python src/01_ingesta/obtener_sismed_filtrado.py
```

#### Paso 3: Preparación e Integración de Datos (ETL)
```bash
python src/02_preparacion/preparacion_datos_mejorado.py
```
*Esto creará el archivo unificado en `datos_procesados/dataset_final_crisp_dm_mejorado.csv` con cerca de 60,000 registros.*

#### Paso 4: Análisis Exploratorio de Datos (EDA - Sesión 5)
```bash
python src/03_eda/eda_proyecto.py
```
*Generará las figuras de alta resolución y los resúmenes estadísticos en `datos_procesados/`.*

#### Paso 5: Escalamiento y Transformación
```bash
python src/04_transformacion/escalamiento.py
```

#### Paso 6: Ejecución del Modelo de Predicción y Riesgo
```bash
python src/05_modelado/probar_modelo_desabastecimiento.py
```

#### Paso 7: Pronóstico de Escenarios Futuros (Ej: Año 2027)
```bash
python src/05_modelado/prediccion_futura_2027.py
```

---

## 🔬 Scripts de Experimentación y Futuras Integraciones (`scripts/`)
Prototipos y utilitarios auxiliares que amplían las capacidades del sistema analítico:
- `scripts/ejemplo_mapa.py`: Prototipo de georreferenciación interactiva con Mapbox y Plotly Express.
- `scripts/descarga_nasa.py`: Conector para la ingesta satelital climática vía NASA POWER API.
- `scripts/espiar_sismed.py`: Utilitario para auditoría de esquemas del SISMED.

