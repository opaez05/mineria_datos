import os
import pandas as pd

DATA_DIR = "datos"
print("""==================================================================")
        FASE 02 CRISP-DM: ESTRUCTURA, COLUMNAS Y CALIDAD DE DATOS
==================================================================""")

# Archivos clave para auditar en detalle
archivos_clave = [
    "SIVIGILA_2021.csv",
    "IDEAM_Datos_de_Estaciones.csv",
    "SISMED_LABORATORIOS.csv"
]

for archivo in archivos_clave:
    ruta = os.path.join(DATA_DIR, archivo)
    if not os.path.exists(ruta):
        continue
        
    print(f"\n>>> AUDITANDO ESTRUCTURA DE: {archivo}")
    try:
        # Cargar solo una muestra para no saturar memoria
        df = pd.read_csv(ruta, nrows=1000, low_memory=False)
        
        print(f"-> Columnas detectadas ({len(df.columns)}):")
        print(list(df.columns))
        
        # Calcular porcentaje de nulos por columna (aproximado con la muestra)
        nulos = df.isnull().mean() * 100
        print("\n-> Calidad de datos (Porcentaje aproximado de valores nulos):")
        for col, pct in nulos.items():
            if pct > 0:
                print(f"   * {col}: {pct:.1f}% nulos")
        if nulos.sum() == 0:
            print("   * ¡No se encontraron valores nulos en la muestra!")
            
    except Exception as e:
        print(f"Error al analizar el archivo: {e}")
    print("-" * 66)

print("==================================================================")
