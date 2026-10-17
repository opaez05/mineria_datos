# Predicción de Brotes Epidemiológicos y Prevención de Desabastecimiento de Medicamentos

Este proyecto de minería de datos tiene como objetivo analizar la correlación entre factores climáticos (temperatura, precipitación y humedad) y la ocurrencia de eventos epidemiológicos (como el Dengue y la Malaria) en los diferentes departamentos de Colombia. Con esta información, el sistema estima la demanda de medicamentos asociados para alertar de forma temprana sobre posibles riesgos de desabastecimiento.

El desarrollo sigue la metodología **CRISP-DM** (actualmente implementado hasta la Fase 3: Preparación de Datos, con un piloto demostrativo para las Fases 4 y 5).

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
├── src/                                  # CÓDIGO FUENTE MODULARIZADO POR FASES
│   ├── 01_ingesta/                       # Fase 1: Auditoría y calidad de datos crudos
│   │   ├── analisis_inicial.py
│   │   └── obtener_sismed_filtrado.py
│   ├── 02_preparacion/                   # Fase 2: Integración y limpieza SIVIGILA + IDEAM + SISMED
│   │   └── preparacion_datos_mejorado.py
│   ├── 03_eda/                           # Fase 3: Análisis Exploratorio de Datos (Sesión 5)
│   │   └── eda_proyecto.py
│   ├── 04_transformacion/                # Fase 4: Escalamiento StandardScaler + RobustScaler
│   │   ├── escalamiento.py
│   │   └── transformacion.py
│   └── 05_modelado/                      # Fase 5 & 6: ML RandomForest y Pronósticos 2027
│       ├── probar_modelo_desabastecimiento.py
│       └── prediccion_futura_2027.py
│
├── docs/                                 # DOCUMENTACIÓN TÉCNICA Y ACADÉMICA
│   ├── index.md                          # Índice general de documentación
│   ├── eda_sesion5.md                    # Guía técnica de la Sesión 5 (EDA)
│   ├── Reporte_EDA_Sesion5.md            # Informe formal de laboratorio (Rúbrica PEA)
│   └── Reporte_CRISP_DM.md               # Informe de auditoría CRISP-DM Fases 1 a 3
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

### Opción B: Ejecución Manual Paso a Paso (Trazabilidad Detallada)

### Paso 1: Auditoría Inicial de Datos
Ejecuta este script para conocer el tamaño físico, número de filas y columnas de los archivos crudos en `datos/`:
```bash
python analisis_inicial.py
```

### Paso 2: Análisis de Calidad y Estructura
Ejecuta este script para inspeccionar las columnas de los archivos clave e identificar el porcentaje de valores nulos:
```bash
python obtener_sismed_filtrado.py
```

### Paso 3: Preparación e Integración de Datos (ETL)
Ejecuta el script principal que limpia la información, simula el clima histórico regional de Colombia por departamento y genera el dataset consolidado final:
```bash
python preparacion_datos_mejorado.py
```
*Esto creará el archivo unificado en `datos_procesados/dataset_final_crisp_dm_mejorado.csv` con cerca de 60,000 registros.*

### Paso 3.1: Análisis Exploratorio de Datos (EDA - Sesión 5)
Ejecuta el análisis estadístico formal (tres familias de medidas, regla IQR, correlaciones y galería de 7 figuras):
```bash
python eda_proyecto.py
```
*Generará las figuras de alta resolución y los resúmenes estadísticos en `datos_procesados/`.*

### Paso 4: Ejecución del Modelo de Predicción y Riesgo
Corre el modelo predictivo piloto para Dengue y evalúa si existen alertas de escasez de medicamentos:
```bash
python probar_modelo_desabastecimiento.py
```
*Este paso entrenará un modelo RandomForest y exportará un gráfico de alertas en `datos_procesados/grafica_riesgo_desabastecimiento.png`.*

### Paso 5: Pronóstico de Escenarios Futuros (Ej: Año 2027)
Ejecuta el script de predicciones para proyectar casos y riesgos de desabastecimiento de medicamentos en el año siguiente (2027) bajo condiciones meteorológicas estimadas:
```bash
python prediccion_futura_2027.py
```
*Este paso generará y exportará el gráfico de tendencia estacional para el año 2027 en `datos_procesados/pronostico_demanda_2027.png`.*
