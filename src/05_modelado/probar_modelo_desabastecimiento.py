import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Estilo visual de los graficos
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['font.sans-serif'] = 'Arial'

DATA_PATH = os.path.join("datos_procesados", "dataset_final_crisp_dm_mejorado.csv")

print("""
==================================================================
        MODELO PREDICTIVO Y ANALISIS DE RIESGO DE INVENTARIO
==================================================================
""")

if not os.path.exists(DATA_PATH):
    print(f"Error: No se encuentra el archivo {DATA_PATH}. Ejecute preparacion_datos_mejorado.py primero.")
    exit(1)

# 1. Carga de datos
df = pd.read_csv(DATA_PATH)

col_temp = "Temperatura_Promedio"
col_prec = "Lluvias_Acumuladas"
col_hum = "Humedad_Ambiente"
col_casos = "Casos_Reportados"

print(f"-> Registros cargados: {len(df)}")
print("-> Variables analizadas:")
print(f"   * Temperatura: {col_temp}")
print(f"   * Lluvia: {col_prec}")
print(f"   * Humedad: {col_hum}")
print(f"   * Casos: {col_casos}")

# 2. Filtrado por enfermedad (Caso de estudio: DENGUE)
enfermedad_objetivo = "DENGUE"
df_target = df[df['Nombre_evento'] == enfermedad_objetivo].copy()

if len(df_target) < 10:
    print(f"Advertencia: Pocos datos para {enfermedad_objetivo}. Usando toda la muestra.")
    df_target = df.copy()
else:
    print(f"-> Muestra para {enfermedad_objetivo}: {len(df_target)} registros")

# 3. Modelado Predictivo (Estimacion de casos segun clima)
features = ['ANO', 'mes', col_temp, col_prec, col_hum]
X = df_target[features].fillna(df_target[features].mean())
y = df_target[col_casos]

# Division de muestras
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# RandomForest para regresion
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Metricas del modelo
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n--- METRICAS DE AJUSTE ---")
print(f"Error Absoluto Medio (MAE): {mae:.2f} casos")
print(f"Coeficiente de Determinacion (R2): {r2:.2f}")

# 4. Simulacion de logistica e inventarios
df_target['casos_predichos'] = model.predict(X)
df_target['demanda_medicamentos_predicha'] = (df_target['casos_predichos'] * 15).astype(int)

# Capacidad de inventario estimada por departamento
inventario_depto = {
    'ANTIOQUIA': 80000,
    'VALLE DEL CAUCA': 70000,
    'BOGOTA': 90000,
    'SANTANDER': 40000,
    'CESAR': 35000,
    'HUILA': 25000,
    'TOLIMA': 30000,
    'ATLANTICO': 50000,
    'BOLIVAR': 45000,
    'CORDOBA': 30000,
    'NARINO': 25000,
    'CHOCO': 15000,
    'NORTE SANTANDER': 35000
}

df_target['inventario_disponible'] = df_target['Departamento'].map(inventario_depto).fillna(20000)

# Calculo de riesgo logistico
df_target['indice_riesgo'] = df_target['demanda_medicamentos_predicha'] / df_target['inventario_disponible']
df_target['Riesgo_Desabastecimiento'] = np.where(df_target['indice_riesgo'] >= 0.85, 'ALTO', 
                                                 np.where(df_target['indice_riesgo'] >= 0.50, 'MEDIO', 'BAJO'))

# Reporte de alertas
print("\n--- REGISTROS CON ALERTA DE RIESGO ---")
alertas = df_target[df_target['Riesgo_Desabastecimiento'] != 'BAJO'].sort_values(by='indice_riesgo', ascending=False)
print(alertas[['Departamento', 'ANO', 'mes', col_casos, 'casos_predichos', 'demanda_medicamentos_predicha', 'Riesgo_Desabastecimiento']].head(15).to_string(index=False))

# 5. Generar grafica de validacion
plt.figure(figsize=(12, 6))

sns.scatterplot(
    data=df_target,
    x=col_casos,
    y='casos_predichos',
    hue='Riesgo_Desabastecimiento',
    palette={'BAJO': 'green', 'MEDIO': 'orange', 'ALTO': 'red'},
    style='Riesgo_Desabastecimiento',
    s=120,
    alpha=0.8
)

plt.plot([0, y.max()], [0, y.max()], 'r--', linewidth=2, label='Prediccion Ideal')
plt.title(f'Predicciones de {enfermedad_objetivo} vs Nivel de Riesgo de Desabastecimiento')
plt.xlabel('Casos Reales')
plt.ylabel('Casos Predichos')
plt.legend(title='Alerta de Inventario')

grafica_path = os.path.join("datos_procesados", "grafica_riesgo_desabastecimiento.png")
plt.savefig(grafica_path, dpi=300, bbox_inches='tight')
print(f"\n[Grafica de alertas guardada en: '{grafica_path}']")
print("==================================================================")
