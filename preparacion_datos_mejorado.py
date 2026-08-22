import pandas as pd
import numpy as np
import os
import glob
import unicodedata

DATA_DIR = "datos"
print("--- PROCESAMIENTO E INTEGRACION DE DATOS HISTORICOS (SIVIGILA - CLIMA) ---")

def clean_text(text):
    if pd.isna(text):
        return text
    # Limpieza basica de texto: mayusculas, sin acentos ni espacios
    text = str(text).upper().strip()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    
    # Estandarizacion de nombres de departamentos
    if 'BOGOTA' in text: return 'BOGOTA'
    if 'NORTE' in text: return 'NORTE SANTANDER'
    if 'VALLE' in text: return 'VALLE DEL CAUCA'
    if 'SAN ANDRES' in text: return 'SAN ANDRES'
    if 'LA GUAJIRA' in text or 'GUAJIRA' in text: return 'GUAJIRA'
    return text

# Mapeo de codigos DIVIPOLA a nombres de departamentos
DIVIPOLA = {
    5: 'ANTIOQUIA',
    8: 'ATLANTICO',
    11: 'BOGOTA',
    13: 'BOLIVAR',
    15: 'BOYACA',
    17: 'CALDAS',
    18: 'CAQUETA',
    19: 'CAUCA',
    20: 'CESAR',
    23: 'CORDOBA',
    25: 'CUNDINAMARCA',
    27: 'CHOCO',
    41: 'HUILA',
    44: 'GUAJIRA',
    47: 'MAGDALENA',
    50: 'META',
    52: 'NARINO',
    54: 'NORTE SANTANDER',
    63: 'QUINDIO',
    66: 'RISARALDA',
    68: 'SANTANDER',
    70: 'SUCRE',
    73: 'TOLIMA',
    76: 'VALLE DEL CAUCA',
    81: 'ARAUCA',
    85: 'CASANARE',
    86: 'PUTUMAYO',
    88: 'SAN ANDRES',
    91: 'AMAZONAS',
    94: 'GUAINIA',
    95: 'GUAVIARE',
    97: 'VAUPES',
    99: 'VICHADA'
}

# Perfiles de referencia climatica por departamento (Temp °C, Lluvia mm, Humedad %)
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

CLIMA_DEFAULT = {'temp': 22.0, 'prec': 150, 'hum': 75}

def generar_clima_historico(row):
    depto = row['Departamento']
    mes = row['mes']
    ano = row['ANO']
    
    perf = CLIMA_PERFILES.get(depto, CLIMA_DEFAULT)
    
    # Factores estacionales aproximados
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
        
    # Variacion de El Nino y La Nina
    if ano == 2019:
        f_nino_temp = 1.1
        f_nino_prec = 0.75
    elif ano == 2021:
        f_nino_temp = -0.8
        f_nino_prec = 1.25
    else:
        f_nino_temp = 0.0
        f_nino_prec = 1.0
        
    # Simulacion estocastica del clima
    np.random.seed(hash(f"{depto}-{mes}-{ano}") % (2**32))
    
    temperatura = perf['temp'] + f_temp + f_nino_temp + np.random.normal(0, 0.4)
    lluvias = (perf['prec'] * f_prec * f_nino_prec) + np.random.normal(0, 15)
    humedad = perf['hum'] + f_hum + np.random.normal(0, 2)
    
    lluvias = max(0.0, lluvias)
    humedad = max(30.0, min(humedad, 100.0))
    
    return pd.Series({
        'Temperatura_Promedio': round(temperatura, 2),
        'Lluvias_Acumuladas': round(lluvias, 2),
        'Humedad_Ambiente': round(humedad, 2)
    })

# 1. Unificacion de archivos historicos SIVIGILA
print("\nCargando y unificando historicos de SIVIGILA...")
sivigila_files = glob.glob(os.path.join(DATA_DIR, "SIVIGILA_*.csv"))
df_sivigila_list = []

for file in sivigila_files:
    print(f"   -> Procesando {os.path.basename(file)}...")
    df = pd.read_csv(file, low_memory=False)
    df.columns = [c.upper() for c in df.columns]
    
    # Identificar columna del departamento
    dept_col = None
    is_code = False
    for col in ['DEPARTAMENTO_OCURRENCIA', 'COD_DPTO_O', 'COD_DPTO']:
        if col in df.columns:
            dept_col = col
            if 'COD' in col:
                is_code = True
            break
            
    # Identificar columna del nombre del evento
    event_col = None
    for col in ['NOMBRE_EVENTO', 'NOMBRE']:
        if col in df.columns:
            event_col = col
            break
            
    # Identificar columna de cantidad de casos
    count_col = None
    for col in ['CONTEO', 'CONTEO_CASOS']:
        if col in df.columns:
            count_col = col
            break
            
    if dept_col is None or event_col is None or 'SEMANA' not in df.columns or 'ANO' not in df.columns:
        print(f"      Saltando {file} por falta de columnas requeridas.")
        continue
        
    df_temp = pd.DataFrame()
    df_temp['SEMANA'] = df['SEMANA'].astype(int)
    df_temp['ANO'] = df['ANO'].astype(str).str.replace(',', '').str.replace('.', '').astype(float).astype(int)
    df_temp['COD_EVE'] = df['COD_EVE'].astype(int) if 'COD_EVE' in df.columns else 0
    df_temp['Nombre_evento'] = df[event_col].astype(str).str.upper().str.strip()
    
    if count_col:
        df_temp['conteo'] = pd.to_numeric(df[count_col], errors='coerce').fillna(1).astype(int)
    else:
        df_temp['conteo'] = 1
        
    if is_code:
        df['TEMP_CODE'] = pd.to_numeric(df[dept_col], errors='coerce').fillna(0).astype(int)
        df_temp['Departamento'] = df['TEMP_CODE'].map(DIVIPOLA).fillna('PROCEDENCIA DESCONOCIDA')
    else:
        df_temp['Departamento'] = df[dept_col].apply(clean_text)
        
    df_sivigila_list.append(df_temp)

df_sivigila = pd.concat(df_sivigila_list, ignore_index=True)
print(f"-> Registros cargados: {len(df_sivigila)}")

# Conversion de semana a mes
df_sivigila['SEMANA_str'] = df_sivigila['SEMANA'].astype(str).str.zfill(2)
df_sivigila['iso_date_str'] = df_sivigila['ANO'].astype(str) + '-W' + df_sivigila['SEMANA_str'] + '-1'
df_sivigila['Fecha_Aprox'] = pd.to_datetime(df_sivigila['iso_date_str'], format='%G-W%V-%u', errors='coerce')
df_sivigila['mes'] = df_sivigila['Fecha_Aprox'].dt.month
df_sivigila['mes'] = df_sivigila['mes'].fillna(((df_sivigila['SEMANA'] - 1) // 4) + 1).clip(1, 12).astype(int)
df_sivigila['Departamento'] = df_sivigila['Departamento'].apply(clean_text)

# Agrupacion temporal
df_salud = df_sivigila.groupby(['Departamento', 'ANO', 'mes', 'COD_EVE', 'Nombre_evento'], as_index=False)['conteo'].sum()
df_salud = df_salud.rename(columns={'conteo': 'Casos_Reportados'})
print(f"-> Datos de salud agrupados por mes/departamento: {len(df_salud)} registros.")

# 2. Generar datos climaticos asociados
print("\nImputando datos climaticos por region y fecha...")
clima_cols = df_salud.apply(generar_clima_historico, axis=1)
df_integrado = pd.concat([df_salud, clima_cols], axis=1)

# 3. Mapear proxy de ventas (SISMED)
print("\nGenerando simulacion de ventas de medicamentos asociadas...")
np.random.seed(123)
casos = df_integrado['Casos_Reportados']
base = np.random.randint(5000, 12000, size=len(df_integrado))
factor = np.random.uniform(8.0, 18.0, size=len(df_integrado))
ruido = np.random.normal(0, 300, size=len(df_integrado))

df_integrado['Medicamentos_Vendidos'] = (base + (casos * factor) + ruido).astype(int)
df_integrado['Medicamentos_Vendidos'] = df_integrado['Medicamentos_Vendidos'].clip(lower=0)

# Filtrado de columnas finales
cols_finales = [
    'Departamento', 'ANO', 'mes', 'COD_EVE', 'Nombre_evento', 
    'Casos_Reportados', 'Temperatura_Promedio', 'Lluvias_Acumuladas', 
    'Humedad_Ambiente', 'Medicamentos_Vendidos'
]
df_final = df_integrado[cols_finales]

# 4. Guardar archivo final
OUTPUT_DIR = "datos_procesados"
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_path = os.path.join(OUTPUT_DIR, "dataset_final_crisp_dm_mejorado.csv")
df_final.to_csv(output_path, index=False)

print(f"\nProceso finalizado. Archivo exportado en: '{output_path}'")
print(f"Dimensiones de la matriz final: {df_final.shape}")
