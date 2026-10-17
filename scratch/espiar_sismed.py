import pandas as pd
import os

DATA_DIR = "datos"
# ⚠️ Ajusta el nombre exacto de tu archivo de SISMED si es diferente
archivo_sismed = "SISMED_LABORATORIOS.csv" 
sismed_path = os.path.join(DATA_DIR, archivo_sismed)

print("--- 🕵️‍♂️ Espiando las columnas del SISMED gigante ---")

try:
    # nrows=1 le dice a Python que solo lea los encabezados y la primera fila
    df_espia = pd.read_csv(sismed_path, nrows=1, low_memory=False)
    print("\n✅ ¡Columnas encontradas con éxito!")
    print("Copia y pegame esta lista de columnas:")
    print(list(df_espia.columns))
except FileNotFoundError:
    print(f"\n❌ No encontré el archivo en la ruta: {sismed_path}")
    print("Verifica si el archivo ya se descargó por completo y qué nombre exacto tiene.")
except Exception as e:
    print(f"\n❌ Ocurrió un error al leer el archivo: {e}")
