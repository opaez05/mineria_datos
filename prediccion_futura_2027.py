import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

# Estilo visual de los graficos
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [12, 6]
plt.rcParams['font.sans-serif'] = 'Arial'

DATA_PATH = os.path.join("datos_procesados", "dataset_final_crisp_dm_mejorado.csv")

print("==================================================================")
print("     PRONOSTICO DE RIESGO DE DESABASTECIMIENTO PARA EL AÑO 2027   ")
print("==================================================================")

if not os.path.exists(DATA_PATH):
    print(f"Error: No se encuentra el archivo {DATA_PATH}. Ejecuta preparacion_datos_mejorado.py primero.")
    exit(1)

# 1. Cargar datos historicos y entrenar el modelo
df = pd.read_csv(DATA_PATH)

col_temp = "Temperatura_Promedio"
col_prec = "Lluvias_Acumuladas"
col_hum = "Humedad_Ambiente"
col_casos = "Casos_Reportados"

# Filtrar para Dengue como caso de estudio
df_target = df[df['Nombre_evento'] == "DENGUE"].copy()

if len(df_target) == 0:
    print("Error: No se encontraron registros de DENGUE en el dataset.")
    exit(1)

features = ['ANO', 'mes', col_temp, col_prec, col_hum]
X = df_target[features].fillna(df_target[features].mean())
y = df_target[col_casos]

print(f"-> Entrenando modelo predictor con {len(df_target)} registros historicos...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)
print("-> Modelo entrenado correctamente.")

# 2. Generar el escenario futuro para el año 2027
# Perfiles climaticos por departamento (iguales a la fase de preparacion)
CLIMA_PERFILES = {
    'BOGOTA': {'temp': 13.5, 'prec': 70, 'hum': 80},
    'ANTIOQUIA': {'temp': 21.0, 'prec': 200, 'hum': 75},
    'VALLE DEL CAUCA': {'temp': 24.0, 'prec': 130, 'hum': 72},
    'ATLANTICO': {'temp': 28.0, 'prec': 80, 'hum': 77},
    'BOLIVAR': {'temp': 28.0, 'prec': 95, 'hum': 77},
    'CESAR': {'temp': 29.0, 'prec': 100, 'hum': 67},
    'CHOCO': {'temp': 26.5, 'prec': 500, 'hum': 90},
    'GUAJIRA': {'temp': 30.0, 'prec': 30, 'hum': 62},
    'HUILA': {'temp': 25.0, 'prec': 90, 'hum': 65},
    'SANTANDER': {'temp': 22.0, 'prec': 140, 'hum': 75},
    'NORTE SANTANDER': {'temp': 23.5, 'prec': 110, 'hum': 72},
    'NARINO': {'temp': 14.0, 'prec': 120, 'hum': 82},
    'BOYACA': {'temp': 13.5, 'prec': 80, 'hum': 78},
    'META': {'temp': 26.0, 'prec': 280, 'hum': 76},
    'TOLIMA': {'temp': 25.0, 'prec': 120, 'hum': 68},
    'CALDAS': {'temp': 19.5, 'prec': 180, 'hum': 80},
    'RISARALDA': {'temp': 20.0, 'prec': 190, 'hum': 80},
    'QUINDIO': {'temp': 19.0, 'prec': 180, 'hum': 80},
    'CORDOBA': {'temp': 27.5, 'prec': 150, 'hum': 79},
    'SUCRE': {'temp': 27.5, 'prec': 130, 'hum': 78},
    'MAGDALENA': {'temp': 28.0, 'prec': 110, 'hum': 77},
    'CAUCA': {'temp': 18.5, 'prec': 160, 'hum': 78},
    'PUTUMAYO': {'temp': 24.5, 'prec': 300, 'hum': 84},
    'AMAZONAS': {'temp': 26.0, 'prec': 270, 'hum': 86},
    'CAQUETA': {'temp': 25.5, 'prec': 280, 'hum': 83},
    'GUAVIARE': {'temp': 26.0, 'prec': 240, 'hum': 81},
    'GUAINIA': {'temp': 26.0, 'prec': 290, 'hum': 83},
    'VAUPES': {'temp': 25.5, 'prec': 270, 'hum': 84},
    'VICHADA': {'temp': 27.0, 'prec': 210, 'hum': 78},
    'CASANARE': {'temp': 26.5, 'prec': 220, 'hum': 74},
    'ARAUCA': {'temp': 27.0, 'prec': 190, 'hum': 73},
    'SAN ANDRES': {'temp': 27.5, 'prec': 140, 'hum': 79}
}

# Crear una lista de registros para predecir (Todos los departamentos, los 12 meses de 2027)
registros_futuros = []
for depto, perf in CLIMA_PERFILES.items():
    for mes in range(1, 13):
        # Aplicamos el mismo patron de estacionalidad
        if mes in [4, 5, 10, 11]:
            f_temp = -1.2
            f_prec = 1.7
            f_hum = 6.0
        elif mes in [1, 2, 7, 8]:
            f_temp = 1.5
            f_prec = 0.55
            f_hum = -5.0
        else:
            f_temp = 0.0
            f_prec = 1.0
            f_hum = 0.0
            
        # Asumimos que 2027 sera un año climaticamente neutral
        temp_est = perf['temp'] + f_temp
        prec_est = max(0.0, perf['prec'] * f_prec)
        hum_est = max(30.0, min(perf['hum'] + f_hum, 100.0))
        
        registros_futuros.append({
            'Departamento': depto,
            'ANO': 2027,
            'mes': mes,
            col_temp: round(temp_est, 2),
            col_prec: round(prec_est, 2),
            col_hum: round(hum_est, 2)
        })

df_futuro = pd.DataFrame(registros_futuros)

# 3. Hacer las predicciones para 2027
df_futuro['casos_predichos'] = model.predict(df_futuro[features])
df_futuro['demanda_medicamentos_predicha'] = (df_futuro['casos_predichos'] * 15).astype(int)

# Capacidad de inventario estimada
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

df_futuro['inventario_disponible'] = df_futuro['Departamento'].map(inventario_depto).fillna(20000)
df_futuro['indice_riesgo'] = df_futuro['demanda_medicamentos_predicha'] / df_futuro['inventario_disponible']
df_futuro['Riesgo_Desabastecimiento'] = np.where(df_futuro['indice_riesgo'] >= 0.85, 'ALTO', 
                                                 np.where(df_futuro['indice_riesgo'] >= 0.50, 'MEDIO', 'BAJO'))

# 4. Mostrar alertas pronosticadas para el año 2027
print("\n--- PRONOSTICOS CON RIESGO DE DESABASTECIMIENTO EN 2027 ---")
alertas_2027 = df_futuro[df_futuro['Riesgo_Desabastecimiento'] != 'BAJO'].sort_values(by='indice_riesgo', ascending=False)

if len(alertas_2027) > 0:
    print(alertas_2027[['Departamento', 'ANO', 'mes', 'casos_predichos', 'demanda_medicamentos_predicha', 'Riesgo_Desabastecimiento']].head(10).to_string(index=False))
else:
    print("No se pronostican riesgos de desabastecimiento altos o medios para 2027 en base a los climas normales.")

# 5. Generar grafica del pronostico mensual general
plt.figure(figsize=(12, 6))

# Agrupar la demanda de medicamentos mensual a nivel nacional para ver la tendencia estacional de 2027
demanda_mensual = df_futuro.groupby('mes')['demanda_medicamentos_predicha'].sum().reset_index()

sns.lineplot(
    data=demanda_mensual,
    x='mes',
    y='demanda_medicamentos_predicha',
    marker='o',
    color='blue',
    linewidth=2.5,
    label='Demanda Estimada'
)

plt.title('Tendencia de la Demanda de Medicamentos Pronosticada para Colombia en el Año 2027')
plt.xlabel('Mes del Año (2027)')
plt.ylabel('Demanda Total Unificada (Unidades)')
plt.xticks(range(1, 13))
plt.grid(True)

grafica_path = os.path.join("datos_procesados", "pronostico_demanda_2027.png")
plt.savefig(grafica_path, dpi=300, bbox_inches='tight')
print(f"\n[Grafica de tendencia de demanda para 2027 guardada en: '{grafica_path}']")
print("==================================================================")
