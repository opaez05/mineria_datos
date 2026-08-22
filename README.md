# Predicción de Brotes Epidemiológicos y Prevención de Desabastecimiento de Medicamentos

Este proyecto de minería de datos tiene como objetivo analizar la correlación entre factores climáticos (temperatura, precipitación y humedad) y la ocurrencia de eventos epidemiológicos (como el Dengue y la Malaria) en los diferentes departamentos de Colombia. Con esta información, el sistema estima la demanda de medicamentos asociados para alertar de forma temprana sobre posibles riesgos de desabastecimiento.

El desarrollo sigue la metodología **CRISP-DM** (actualmente implementado hasta la Fase 3: Preparación de Datos, con un piloto demostrativo para las Fases 4 y 5).

---

## 📋 Estructura del Proyecto

*   **`datos/`**: Carpeta que contiene los archivos originales en crudo (SIVIGILA históricos de 2017, 2018, 2019 y 2021; y catálogos/estaciones de IDEAM y SISMED).
*   **`datos_procesados/`**: Carpeta donde se guarda el dataset integrado resultante y los gráficos del modelo. (Esta carpeta está excluida del control de versiones).
*   **`analisis_inicial.py`**: Script de auditoría de volumen de datos inicial.
*   **`obtener_sismed_filtrado.py`**: Script de análisis de calidad, estructura y nulos de los archivos de origen.
*   **`preparacion_datos_mejorado.py`**: Proceso principal de ETL que unifica, limpia, simula el clima regional histórico de Colombia e integra las variables de salud y medicamentos.
*   **`probar_modelo_desabastecimiento.py`**: Modelo predictivo piloto (`RandomForest`) que estima casos y evalúa el riesgo de inventario.

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

El proyecto cuenta con un flujo estructurado que puedes ejecutar paso a paso:

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
