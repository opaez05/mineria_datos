"""
=============================================================================
  FASE 3 – PREPARACIÓN DE DATOS: ESCALAMIENTO DE CARACTERÍSTICAS
  Proyecto: Predicción de Brotes Epidemiológicos y Prevención de
            Desabastecimiento de Medicamentos en Colombia
  Metodología: CRISP-DM
=============================================================================

¿POR QUÉ ESCALAR?
-----------------
El dataset generado por `preparacion_datos_mejorado.py` contiene variables
numéricas que viven en escalas completamente distintas:

  - Temperatura_Promedio  -> valores entre ~12 y ~32 (°C)
  - Lluvias_Acumuladas    -> valores entre ~10 y ~850 (mm)
  - Humedad_Ambiente      -> valores entre ~35 y ~96 (%)
  - Medicamentos_Vendidos -> valores entre ~5 000 y ~400 000 (unidades)

Cuando estas variables se usan directamente en algoritmos sensibles a la
magnitud (distancias euclideas, regresión lineal, SVM, KNN, redes
neuronales, PCA, etc.), la variable con mayor rango domina injustamente
el cálculo.  El escalamiento pone todas las variables en un "lenguaje
común" para que el modelo las pondere de forma equitativa.

¿QUÉ SCALER SE USA Y POR QUÉ?
-------------------------------
Este proyecto emplea TRES escaladores de manera justificada:

  1. StandardScaler  (media=0, desviación estándar=1)
     -> Apropiado para variables con distribución aproximadamente normal.
     -> Se usa sobre Temperatura_Promedio y Humedad_Ambiente, que tienden
       a distribuirse de forma simétrica por departamento.

  2. RobustScaler   (mediana=0, escala basada en IQR)
     -> Apropiado cuando hay valores atípicos (outliers) pronunciados.
     -> Se usa sobre Lluvias_Acumuladas (Chocó tiene >500 mm vs regiones
       áridas con <30 mm) y sobre Medicamentos_Vendidos, que tiene una
       cola derecha muy larga por departamentos de alta densidad poblacional.
     -> Al basarse en la mediana y el rango intercuartílico (IQR) en lugar
       de la media y varianza, el RobustScaler no se "distorsiona" por
       esos extremos.

  3. MinMaxScaler   ([0, 1])
     -> Se aplica DESPUÉS del escalamiento anterior como comparación
       opcional y para columnas que alimentan algoritmos que requieren
       valores en [0, 1] (e.g., redes neuronales con activación sigmoide).

NOTA: Casos_Reportados NO se escala porque es la variable objetivo (y)
      del modelo predictivo.  Escalarla generaría incongruencias al
      interpretar los resultados del modelo.

ARCHIVO DE ENTRADA:
  datos_procesados/dataset_final_crisp_dm_mejorado.csv
  (Generado por preparacion_datos_mejorado.py)

ARCHIVOS DE SALIDA:
  datos_procesados/dataset_escalado_standard_robust.csv
      Dataset listo para modelado con StandardScaler + RobustScaler.
  datos_procesados/resumen_escalamiento.txt
      Reporte textual con estadísticas antes/después del escalamiento.
=============================================================================
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# ---------------------------------------------------------------------------
DATA_PATH   = os.path.join("datos_procesados", "dataset_final_crisp_dm_mejorado.csv")
OUTPUT_CSV  = os.path.join("datos_procesados", "dataset_escalado_standard_robust.csv")
OUTPUT_TXT  = os.path.join("datos_procesados", "resumen_escalamiento.txt")

print("=" * 70)
print("   FASE 3 – ESCALAMIENTO DE CARACTERÍSTICAS (CRISP-DM)              ")
print("=" * 70)

# ---------------------------------------------------------------------------
# 1. CARGA DEL DATASET
#    Se lee el CSV generado por preparacion_datos_mejorado.py.
#    Ese archivo ya tiene los datos limpios, integrados y simulados.
# ---------------------------------------------------------------------------
if not os.path.exists(DATA_PATH):
    print(f"\n[ERROR] No se encontró el archivo: {DATA_PATH}")
    print("  -> Ejecuta primero: python preparacion_datos_mejorado.py")
    exit(1)

df = pd.read_csv(DATA_PATH)
print(f"\n[1] Dataset cargado correctamente.")
print(f"    Registros: {len(df):,}  |  Columnas: {df.shape[1]}")
print(f"    Columnas: {list(df.columns)}")

# ---------------------------------------------------------------------------
# 2. SEPARACIÓN DE VARIABLES
#    - y            : variable objetivo -> NO se escala
#    - VARS_STD     : variables con distribución relativamente normal
#                     -> StandardScaler
#    - VARS_ROBUST  : variables con outliers pronunciados
#                     -> RobustScaler
#    - cols_id      : columnas identificadoras/categóricas -> se conservan tal cual
# ---------------------------------------------------------------------------
y = df["Casos_Reportados"]   # Variable objetivo – se conserva sin modificar

# Variables aptas para StandardScaler (simétricas, sin outliers extremos)
VARS_STD = [
    "Temperatura_Promedio",  # Rango ~12–32 °C, distribución aproximada normal
    "Humedad_Ambiente",      # Rango ~35–96 %, distribución relativamente centrada
]

# Variables con outliers – se prefiere RobustScaler
VARS_ROBUST = [
    "Lluvias_Acumuladas",    # Chocó >500 mm vs Guajira <30 mm -> outlier severo
    "Medicamentos_Vendidos", # Cola derecha larga por grandes departamentos
]

# Columnas que se arrastran sin escalar (identificadores y categorías)
COLS_ID = ["Departamento", "ANO", "mes", "COD_EVE", "Nombre_evento", "Casos_Reportados"]

print("\n[2] Separación de variables definida:")
print(f"    StandardScaler  -> {VARS_STD}")
print(f"    RobustScaler    -> {VARS_ROBUST}")
print(f"    Sin escalar     -> {COLS_ID}")

# ---------------------------------------------------------------------------
# 3. ESTADÍSTICAS ORIGINALES (ANTES DEL ESCALAMIENTO)
#    Se registran para demostrar la disparidad de escalas y justificar
#    la necesidad del escalamiento.
# ---------------------------------------------------------------------------
print("\n[3] Estadísticas ANTES del escalamiento:")
todas_numericas = VARS_STD + VARS_ROBUST
estadisticas_antes = df[todas_numericas].describe().round(3)
print(estadisticas_antes.to_string())

# ---------------------------------------------------------------------------
# 4. APLICAR StandardScaler A LAS VARIABLES SIMÉTRICAS
#    Transforma cada variable x a: z = (x - media) / desv_estándar
#    Resultado: media = 0, desv_estándar = 1 para cada variable.
# ---------------------------------------------------------------------------
print("\n[4] Aplicando StandardScaler a:", VARS_STD)

std_scaler = StandardScaler()
X_std_array = std_scaler.fit_transform(df[VARS_STD])
X_std = pd.DataFrame(X_std_array, columns=VARS_STD, index=df.index)

print("    Medias originales usadas por el scaler:")
for col, mean in zip(VARS_STD, std_scaler.mean_):
    print(f"      {col}: {mean:.4f}")
print("    Desviaciones estándar usadas por el scaler:")
for col, scale in zip(VARS_STD, std_scaler.scale_):
    print(f"      {col}: {scale:.4f}")

print("    Verificación post-StandardScaler (deben ser ~0 y ~1):")
print(X_std.describe().loc[["mean", "std"]].round(4).to_string())

# ---------------------------------------------------------------------------
# 5. APLICAR RobustScaler A LAS VARIABLES CON OUTLIERS
#    Transforma cada variable x a: z = (x - mediana) / IQR
#    IQR = percentil 75 - percentil 25
#    Resultado: robusto frente a datos extremos (Chocó, grandes ciudades).
# ---------------------------------------------------------------------------
print("\n[5] Aplicando RobustScaler a:", VARS_ROBUST)

rob_scaler = RobustScaler()
X_rob_array = rob_scaler.fit_transform(df[VARS_ROBUST])
X_rob = pd.DataFrame(X_rob_array, columns=VARS_ROBUST, index=df.index)

print("    Medianas usadas por el scaler:")
for col, center in zip(VARS_ROBUST, rob_scaler.center_):
    print(f"      {col}: {center:.4f}")
print("    IQR (escala) usados por el scaler:")
for col, scale in zip(VARS_ROBUST, rob_scaler.scale_):
    print(f"      {col}: {scale:.4f}")

print("    Verificación post-RobustScaler (medianas deben ser ~0):")
print(X_rob.describe().loc[["50%"]].round(4).to_string())

# ---------------------------------------------------------------------------
# 6. ESCALAMIENTO ALTERNATIVO CON MinMaxScaler (COMPARACIÓN / OPCIONAL)
#    Normaliza cada variable al rango [0, 1].
#    Útil para algoritmos como redes neuronales.
# ---------------------------------------------------------------------------
print("\n[6] Aplicando MinMaxScaler (alternativo, rango [0,1]) a:", todas_numericas)

mm_scaler = MinMaxScaler()
X_mm_array = mm_scaler.fit_transform(df[todas_numericas])
X_mm = pd.DataFrame(X_mm_array, columns=todas_numericas, index=df.index)

print("    Verificación post-MinMaxScaler (min=0, max=1):")
print(X_mm.describe().loc[["min", "max"]].round(4).to_string())

# ---------------------------------------------------------------------------
# 7. CONSTRUCCIÓN DEL DATASET FINAL ESCALADO
#    Se unen:
#      - Columnas identificadoras/categóricas (sin modificar)
#      - Variables escaladas con StandardScaler
#      - Variables escaladas con RobustScaler
# ---------------------------------------------------------------------------
print("\n[7] Ensamblando dataset final escalado...")

df_escalado = pd.concat(
    [
        df[COLS_ID].reset_index(drop=True),
        X_std.reset_index(drop=True),
        X_rob.reset_index(drop=True),
    ],
    axis=1
)

print(f"    Forma del dataset escalado: {df_escalado.shape}")
print(f"    Columnas finales: {list(df_escalado.columns)}")
print("\n    Primeras 5 filas del dataset escalado:")
print(df_escalado.head().to_string())

# ---------------------------------------------------------------------------
# 8. GUARDAR EL DATASET ESCALADO
# ---------------------------------------------------------------------------
os.makedirs("datos_procesados", exist_ok=True)
df_escalado.to_csv(OUTPUT_CSV, index=False)
print(f"\n[8] Dataset escalado guardado en: '{OUTPUT_CSV}'")

# ---------------------------------------------------------------------------
# 9. GENERAR REPORTE TEXTUAL DE ESCALAMIENTO
# ---------------------------------------------------------------------------
lineas_reporte = []
lineas_reporte.append("=" * 70)
lineas_reporte.append("   REPORTE DE ESCALAMIENTO DE CARACTERÍSTICAS")
lineas_reporte.append("   Proyecto: Predicción de Brotes Epidemiológicos – Colombia")
lineas_reporte.append("=" * 70)

lineas_reporte.append("\n--- ESTADÍSTICAS ANTES DEL ESCALAMIENTO ---")
lineas_reporte.append(estadisticas_antes.to_string())

lineas_reporte.append("\n\n--- ESTADÍSTICAS DESPUÉS – StandardScaler ---")
lineas_reporte.append(f"Variables: {VARS_STD}")
lineas_reporte.append(X_std.describe().round(4).to_string())

lineas_reporte.append("\n\n--- ESTADÍSTICAS DESPUÉS – RobustScaler ---")
lineas_reporte.append(f"Variables: {VARS_ROBUST}")
lineas_reporte.append(X_rob.describe().round(4).to_string())

lineas_reporte.append("\n\n--- ESTADÍSTICAS DESPUÉS – MinMaxScaler (alternativo) ---")
lineas_reporte.append(f"Variables: {todas_numericas}")
lineas_reporte.append(X_mm.describe().round(4).to_string())

lineas_reporte.append("\n\n--- DECISIÓN FINAL ---")
lineas_reporte.append("Dataset exportado usa: StandardScaler + RobustScaler")
lineas_reporte.append(f"Archivo de salida: {OUTPUT_CSV}")
lineas_reporte.append(f"Registros: {len(df_escalado):,}  |  Columnas: {df_escalado.shape[1]}")

with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
    f.write("\n".join(lineas_reporte))

print(f"[9] Reporte guardado en: '{OUTPUT_TXT}'")

# ---------------------------------------------------------------------------
# RESUMEN FINAL
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("   ESCALAMIENTO COMPLETADO EXITOSAMENTE")
print("=" * 70)
print(f"""
RESUMEN:
  Registros procesados       : {len(df_escalado):,}
  Variables originales       : {len(todas_numericas)} numéricas
  StandardScaler aplicado a  : {VARS_STD}
  RobustScaler aplicado a    : {VARS_ROBUST}
  Variable objetivo (y)      : Casos_Reportados (no escalada)
  Dataset escalado           : {OUTPUT_CSV}
  Reporte de auditoría       : {OUTPUT_TXT}

SIGUIENTE PASO:
  Usa el archivo escalado como entrada alternativa en:
    -> probar_modelo_desabastecimiento.py
    -> prediccion_futura_2027.py
  Cambiando DATA_PATH por:
    datos_procesados/dataset_escalado_standard_robust.csv
""")

