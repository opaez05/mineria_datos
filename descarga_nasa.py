import time
import pandas as pd
import requests

# Diccionario completo con Departamentos, Capitales, Coordenadas y Altitud (msnm)
departamentos = {
    'Amazonas': {'capital': 'Leticia', 'lat': -4.21, 'lon': -69.94, 'altitud_msnm': 96},
    'Antioquia': {'capital': 'Medellín', 'lat': 6.25, 'lon': -75.56, 'altitud_msnm': 1495},
    'Arauca': {'capital': 'Arauca', 'lat': 7.08, 'lon': -70.76, 'altitud_msnm': 125},
    'Atlantico': {'capital': 'Barranquilla', 'lat': 10.97, 'lon': -74.78, 'altitud_msnm': 18},
    'Bolivar': {'capital': 'Cartagena', 'lat': 10.40, 'lon': -75.50, 'altitud_msnm': 2},
    'Boyaca': {'capital': 'Tunja', 'lat': 5.53, 'lon': -73.36, 'altitud_msnm': 2820},
    'Caldas': {'capital': 'Manizales', 'lat': 5.07, 'lon': -75.52, 'altitud_msnm': 2160},
    'Caqueta': {'capital': 'Florencia', 'lat': 1.61, 'lon': -75.61, 'altitud_msnm': 242},
    'Casanare': {'capital': 'Yopal', 'lat': 5.34, 'lon': -72.39, 'altitud_msnm': 350},
    'Cauca': {'capital': 'Popayán', 'lat': 2.44, 'lon': -76.61, 'altitud_msnm': 1760},
    'Cesar': {'capital': 'Valledupar', 'lat': 10.46, 'lon': -73.25, 'altitud_msnm': 168},
    'Choco': {'capital': 'Quibdó', 'lat': 5.69, 'lon': -76.66, 'altitud_msnm': 43},
    'Cordoba': {'capital': 'Montería', 'lat': 8.75, 'lon': -75.88, 'altitud_msnm': 18},
    'Cundinamarca': {'capital': 'Bogotá', 'lat': 4.61, 'lon': -74.08, 'altitud_msnm': 2625},
    'Guainia': {'capital': 'Inírida', 'lat': 3.86, 'lon': -67.92, 'altitud_msnm': 100},
    'Guaviare': {'capital': 'San José del Guaviare', 'lat': 2.56, 'lon': -72.64, 'altitud_msnm': 175},
    'Huila': {'capital': 'Neiva', 'lat': 2.93, 'lon': -75.28, 'altitud_msnm': 442},
    'La Guajira': {'capital': 'Riohacha', 'lat': 11.54, 'lon': -72.91, 'altitud_msnm': 5},
    'Magdalena': {'capital': 'Santa Marta', 'lat': 11.24, 'lon': -74.20, 'altitud_msnm': 6},
    'Meta': {'capital': 'Villavicencio', 'lat': 4.14, 'lon': -73.63, 'altitud_msnm': 467},
    'Narino': {'capital': 'Pasto', 'lat': 1.21, 'lon': -77.28, 'altitud_msnm': 2527},
    'Norte de Santander': {'capital': 'Cúcuta', 'lat': 7.89, 'lon': -72.50, 'altitud_msnm': 320},
    'Putumayo': {'capital': 'Mocoa', 'lat': 1.15, 'lon': -76.65, 'altitud_msnm': 604},
    'Quindio': {'capital': 'Armenia', 'lat': 4.53, 'lon': -75.68, 'altitud_msnm': 1551},
    'Risaralda': {'capital': 'Pereira', 'lat': 4.81, 'lon': -75.69, 'altitud_msnm': 1411},
    'Santander': {'capital': 'Bucaramanga', 'lat': 7.13, 'lon': -73.12, 'altitud_msnm': 959},
    'Sucre': {'capital': 'Sincelejo', 'lat': 9.30, 'lon': -75.39, 'altitud_msnm': 213},
    'Tolima': {'capital': 'Ibagué', 'lat': 4.44, 'lon': -75.20, 'altitud_msnm': 1285},
    'Valle del Cauca': {'capital': 'Cali', 'lat': 3.44, 'lon': -76.52, 'altitud_msnm': 1018},
    'Vaupes': {'capital': 'Mitú', 'lat': 1.25, 'lon': -70.23, 'altitud_msnm': 183},
    'Vichada': {'capital': 'Puerto Carreño', 'lat': 6.18, 'lon': -67.49, 'altitud_msnm': 51}
}

FECHA_INICIO = "20240101"
FECHA_FIN = "20260801"
PARAMETROS = "PRECTOTCORR,RH2M,T2M,T2M_MAX,T2M_MIN"

lista_df = []

print("Descargando dataset de la NASA con Departamento, Capital y Altitud...")

for dpto, info in departamentos.items():
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters={PARAMETROS}&community=AG"
        f"&longitude={info['lon']}&latitude={info['lat']}"
        f"&start={FECHA_INICIO}&end={FECHA_FIN}&format=JSON"
    )
    
    exito = False
    intentos = 0
    
    # Reintento automático por si la API parpadea
    while not exito and intentos < 3:
        try:
            intentos += 1
            response = requests.get(url, timeout=15) # Timeout de 15s para no congelar el script
            
            if response.status_code == 200:
                data = response.json()
                params_data = data['properties']['parameter']
                
                df_dpto = pd.DataFrame(params_data)
                df_dpto.index.name = 'Fecha'
                df_dpto.reset_index(inplace=True)
                
                # Columnas agregadas
                df_dpto['Departamento'] = dpto
                df_dpto['Capital'] = info['capital']
                df_dpto['Altitud_msnm'] = info['altitud_msnm']
                
                lista_df.append(df_dpto)
                print(f"✔ Procesado: {dpto} ({info['capital']} - {info['altitud_msnm']} msnm)")
                exito = True
            else:
                print(f"⚠️ Reintentando {dpto} (Intento {intentos}/3)...")
                time.sleep(2)
        except requests.exceptions.RequestException:
            print(f"⚠️ Error de red en {dpto}, reintentando ({intentos}/3)...")
            time.sleep(2)

    if not exito:
        print(f"❌ No se pudieron descargar datos para {dpto}")

# Consolidación de datos
df_colombia = pd.concat(lista_df, ignore_index=True)

df_colombia.rename(columns={
    'PRECTOTCORR': 'Precipitacion_mm',
    'RH2M': 'Humedad_Relativa',
    'T2M': 'Temp_Media',
    'T2M_MAX': 'Temp_Max',
    'T2M_MIN': 'Temp_Min'
}, inplace=True)

# Estructuración de columnas
columnas_ordenadas = [
    'Fecha', 'Departamento', 'Capital', 'Altitud_msnm',
    'Precipitacion_mm', 'Humedad_Relativa', 'Temp_Media', 'Temp_Max', 'Temp_Min'
]
df_colombia = df_colombia[columnas_ordenadas]

# Exportar a CSV y JSON
df_colombia.to_csv("clima_colombia_reciente.csv", index=False)
df_colombia.to_json("clima_colombia_reciente.json", orient="records", date_format="iso")

print("\n¡Proceso finalizado con éxito! Archivos actualizados.")