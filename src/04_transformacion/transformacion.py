import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler, KBinsDiscretizer
from sklearn.decomposition import PCA

# 1. Rutas relativas o absolutas
RUTA = Path(r"PROYECTO\datos_procesados\dataset_final_crisp_dm_mejorado.csv")
df = pd.read_csv(RUTA)
print(f"Dimensiones iniciales: {df.shape}")



y = df["Casos_Reportados"]  # Target (no se escala junto a X)

# Definir columnas numéricas que entrarán a la matriz de distancias
NUMERICAS = [
    "Temperatura_Promedio",
    "Lluvias_Acumuladas",
    "Humedad_Ambiente",
    "Medicamentos_Vendidos"
]
X_num = df[NUMERICAS].copy()


# Puedes usar StandardScaler (media 0, varianza 1) o RobustScaler si hay outliers climáticos
scaler = StandardScaler()
X_scaled = pd.DataFrame(
    scaler.fit_transform(X_num),
    columns=NUMERICAS,
    index=df.index
)


# Codificación One-Hot de nominales
categoricas_nominales = ["Departamento", "Nombre_evento"]

# Generamos dummies con enteros 0 y 1 (dtype=int)
X_cat = pd.get_dummies(df[categoricas_nominales], prefix=categoricas_nominales, dtype=int)
print(f"Nuevas columnas generadas por One-Hot: {X_cat.shape[1]}")


# Ejemplo con Lluvias_Acumuladas en 4 cuantiles
discretizador = KBinsDiscretizer(n_bins=4, encode="ordinal", strategy="quantile")
lluvias_bins = discretizador.fit_transform(df[["Lluvias_Acumuladas"]]).ravel()
print("Bordes de los rangos de lluvia:", discretizador.bin_edges_[0].round(1))



# 5. Reducción de Dimensionalidad con PCA (Opción A: 3 componentes explican el 93.3% de la varianza)
pca = PCA(n_components=3)
X_pca_array = pca.fit_transform(X_scaled)
columnas_pca = [f"PC_{i+1}" for i in range(3)]
X_pca = pd.DataFrame(X_pca_array, columns=columnas_pca, index=df.index)

acumulada = pca.explained_variance_ratio_.cumsum().round(3)
print("Varianza acumulada de los 3 componentes numéricos:", acumulada)


# Incluimos identificador (COD_EVE) y variables temporales (ANO, mes)
X_id_tiempo = df[["COD_EVE", "ANO", "mes"]]

# Concatenar horizontalmente usando X_pca en lugar de X_scaled
X_final = pd.concat([X_pca, X_id_tiempo, X_cat], axis=1)

print("\n--- Matriz Final de Entrenamiento con PCA ---")
print("Forma final de X:", X_final.shape)
print("Target y:", y.shape)
print(f"Variables sintéticas PCA generadas: {columnas_pca}")

