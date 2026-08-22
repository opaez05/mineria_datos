import os
import pandas as pd

DATA_DIR = "datos"
print("""
==================================================================
     FASE 02 CRISP-DM: AUDITORIA DE VOLUMEN Y TAMAÑO DE DATOS    
==================================================================
""")

if not os.path.exists(DATA_DIR):
    print(f"Error: La carpeta '{DATA_DIR}' no existe.")
    exit(1)

# Listar todos los archivos en la carpeta de datos
archivos = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

if not archivos:
    print(f"No se encontraron archivos CSV en la carpeta '{DATA_DIR}'.")
    exit(0)

print(f"Se detectaron {len(archivos)} archivos de datos para el proyecto.\n")
print(f"{'Archivo CSV':<45} | {'Tamaño (MB)':<12} | {'Filas':<10} | {'Columnas':<10}")
print("-" * 88)

for archivo in archivos:
    ruta = os.path.join(DATA_DIR, archivo)
    # Tamaño en MB
    tamano_mb = os.path.getsize(ruta) / (1024 * 1024)
    
    # Intentar leer filas y columnas sin cargar todo el archivo en memoria
    try:
        # Para saber el número de filas de forma rápida
        with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
            filas = sum(1 for line in f) - 1 # Restar la cabecera
            
        # Leer solo la cabecera para saber el número de columnas
        df_head = pd.read_csv(ruta, nrows=0)
        columnas = len(df_head.columns)
    except Exception as e:
        filas = "N/A"
        columnas = "N/A"

    print(f"{archivo:<45} | {tamano_mb:<12.2f} | {filas:<10} | {columnas:<10}")

print("==================================================================")
