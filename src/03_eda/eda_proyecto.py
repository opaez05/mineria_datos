"""
=============================================================================
  SESIÓN 5 – MINERÍA DE DATOS (UNIMINUTO)
  ANÁLISIS EXPLORATORIO DE DATOS (EDA) APLICADO AL PROYECTO:
  "Predicción de Brotes Epidemiológicos y Prevención de Desabastecimiento
   de Medicamentos en Colombia"
=============================================================================
Metodología: CRISP-DM – Fase 2: Entendimiento de los Datos (Cierre Avance 1)

Este script aplica rigurosamente todos los estándares, métricas estadísticas
y la galería visual de la Sesión 5 al dataset integrado del proyecto:
  1. Primer vistazo descriptivo (dimensiones, tipos, nulos).
  2. Tres familias de medidas: Tendencia central, Dispersión y Forma (Skew, Kurtosis).
  3. Cuantificación formal de outliers mediante la regla del Rango Intercuartílico (IQR).
  4. Galería gráfica profesional (matplotlib):
     - Fig 1: Histograma con líneas verticales para Media (rojo) y Mediana (verde).
     - Fig 2: Boxplot horizontal con anatomía de 5 números y outliers explícitos.
     - Fig 3: Gráficos de barras ordenados por frecuencia (Departamentos y Eventos).
     - Fig 4: Dispersión + recta de tendencia lineal (y = mx + b) con Pearson r.
     - Fig 5: Mapa de calor de correlaciones de Pearson (anotado, colormap RdBu_r).
     - Fig 6: Matriz de dispersión multivariada (scatter matrix con diagonal hist).
     - Fig 7: Análisis bivariado de contingencia: Tasa de riesgo de desabastecimiento
              por departamento mediante pd.crosstab(normalize="index").
=============================================================================
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Generación sin interfaz gráfica para entornos headless
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import scatter_matrix

# ---------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE RUTAS Y CONSTANTES
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
RUTA_DATASET = BASE_DIR / "datos_procesados" / "dataset_final_crisp_dm_mejorado.csv"
CARPETA_FIGURAS = BASE_DIR / "datos_procesados"
CARPETA_FIGURAS.mkdir(parents=True, exist_ok=True)

def ruta_figura(nombre: str) -> Path:
    return CARPETA_FIGURAS / nombre

print("=" * 75)
print("   SESIÓN 5: ANÁLISIS EXPLORATORIO DE DATOS (EDA) – PROYECTO CRISP-DM")
print("=" * 75)

if not RUTA_DATASET.exists():
    print(f"\n[ERROR] No se encontró el dataset: {RUTA_DATASET}")
    print("  -> Ejecute primero: python preparacion_datos_mejorado.py")
    exit(1)

df = pd.read_csv(RUTA_DATASET)
print("\n[A] PRIMER VISTAZO AL DATASET DEL PROYECTO")
print(f"Dimensiones del dataset general: {df.shape[0]:,} filas x {df.shape[1]} columnas")
print("\nNulos por columna:")
nulos = df.isna().sum()
if (nulos > 0).any():
    print(nulos[nulos > 0].to_string())
else:
    print("  -> 0 nulos detectados. Dataset 100% limpio e imputado.")

# Columnas numéricas del proyecto
COLS_NUM = [
    "Casos_Reportados",
    "Temperatura_Promedio",
    "Lluvias_Acumuladas",
    "Humedad_Ambiente",
    "Medicamentos_Vendidos"
]

print("\nEstadística descriptiva global:")
print(df[COLS_NUM].describe().round(2).to_string())

# ---------------------------------------------------------------------------
# 2. SUBSET DEL CASO DE ESTUDIO PRIORITARIO: DENGUE
#    (El foco del modelo predictivo de brotes y desabastecimiento)
# ---------------------------------------------------------------------------
df_dengue = df[df["Nombre_evento"] == "DENGUE"].copy()
print(f"\n-> Muestra específica para DENGUE: {len(df_dengue):,} registros histórico-regionales")

print("\n" + "-" * 75)
print("TRES FAMILIAS DE MEDIDAS: TENDENCIA CENTRAL, DISPERSIÓN Y FORMA (DENGUE)")
print("-" * 75)

stats_forma = []
for col in COLS_NUM:
    media = df_dengue[col].mean()
    mediana = df_dengue[col].median()
    std = df_dengue[col].std()
    asimetria = df_dengue[col].skew()
    curtosis = df_dengue[col].kurtosis()
    stats_forma.append({
        "Variable": col,
        "Media": round(media, 2),
        "Mediana": round(mediana, 2),
        "Desv_Est": round(std, 2),
        "Asimetría (Skew)": round(asimetria, 2),
        "Curtosis": round(curtosis, 2)
    })

df_stats_forma = pd.DataFrame(stats_forma)
print(df_stats_forma.to_string(index=False))

print("\n[LECCIÓN SESIÓN 5 APLICADA AL PROYECTO]:")
print(f" * Casos_Reportados: Media = {df_dengue['Casos_Reportados'].mean():.1f} vs Mediana = {df_dengue['Casos_Reportados'].median():.1f}")
print(f"   Asimetría = +{df_dengue['Casos_Reportados'].skew():.2f} (cola derecha extrema) | Curtosis = {df_dengue['Casos_Reportados'].kurtosis():.2f}")
print("   -> Conclusión: La media está inflada por brotes epidémicos atípicos. La MEDIANA es la medida honesta del centro.")

# ---------------------------------------------------------------------------
# FIGURA 1: HISTOGRAMA DE CASOS REPORTADOS DE DENGUE
# ---------------------------------------------------------------------------
plt.figure(figsize=(8.5, 4.8))
datos_casos = df_dengue["Casos_Reportados"].dropna()
media_c = datos_casos.mean()
mediana_c = datos_casos.median()

plt.hist(datos_casos, bins=35, color="#0e7490", edgecolor="white", alpha=0.9)
plt.axvline(media_c, color="#dc2626", ls="--", lw=2.2,
            label=f"Media: {media_c:.1f} casos")
plt.axvline(mediana_c, color="#059669", ls="-", lw=2.2,
            label=f"Mediana: {mediana_c:.1f} casos")

plt.xlabel("Casos Reportados Mensuales de Dengue por Departamento", fontsize=11)
plt.ylabel("Frecuencia (Meses-Departamento)", fontsize=11)
plt.title("Distribución de Casos de Dengue: Asimetría Positiva Marcada (Cola Derecha)", fontsize=12, fontweight="bold")
plt.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1")
plt.grid(axis="y", linestyle=":", alpha=0.6)
plt.tight_layout()
fig1_path = ruta_figura("fig1_hist_casos_dengue.png")
plt.savefig(fig1_path, dpi=120)
plt.close()
print(f"\n[1] Histograma guardado en: {fig1_path.name}")

# ---------------------------------------------------------------------------
# FIGURA 2: BOXPLOT Y CUANTIFICACIÓN FORMAL DE OUTLIERS (REGLA IQR)
# ---------------------------------------------------------------------------
plt.figure(figsize=(8.5, 3.2))
plt.boxplot(datos_casos, vert=False, widths=0.55, patch_artist=True,
            boxprops=dict(facecolor="#bae6fd", color="#0369a1"),
            medianprops=dict(color="#dc2626", lw=2),
            flierprops=dict(marker='o', markerfacecolor='#e11d48', markersize=5, alpha=0.6, markeredgecolor='none'))
plt.xlabel("Casos Reportados de Dengue (Mensual)", fontsize=11)
plt.title("Boxplot de Casos de Dengue: Identificación de Brotes Epidemiológicos (Outliers)", fontsize=12, fontweight="bold")
plt.grid(axis="x", linestyle=":", alpha=0.6)
plt.tight_layout()
fig2_path = ruta_figura("fig2_box_casos_outliers.png")
plt.savefig(fig2_path, dpi=120)
plt.close()

# Regla del IQR aplicada rigurosamente
q1, q3 = datos_casos.quantile([0.25, 0.75])
iqr = q3 - q1
limite_sup = q3 + 1.5 * iqr
limite_inf = max(0, q1 - 1.5 * iqr)
outliers_casos = df_dengue[df_dengue["Casos_Reportados"] > limite_sup]
pct_outliers = (len(outliers_casos) / len(df_dengue)) * 100

print(f"\n[2] Regla IQR formal para Casos de Dengue:")
print(f"    Q1 = {q1:.1f} | Q3 = {q3:.1f} | IQR = {iqr:.1f}")
print(f"    Límite Superior (Q3 + 1.5*IQR) = {limite_sup:.1f} casos")
print(f"    Outliers detectados: {len(outliers_casos)} de {len(df_dengue)} registros ({pct_outliers:.1f}%)")
print("    Top 5 Departamentos con mayor cantidad de meses en condición de brote atípico (Outlier):")
top_outliers = (outliers_casos.groupby("Departamento")["Casos_Reportados"]
                .agg(Meses_Brote="count", Max_Casos="max", Mediana_Casos="median")
                .sort_values(by="Meses_Brote", ascending=False)
                .head(5))
print(top_outliers.to_string())

# ---------------------------------------------------------------------------
# FIGURA 3: GRÁFICOS DE BARRAS (CATEGÓRICAS ORDENADAS POR FRECUENCIA)
# ---------------------------------------------------------------------------
fig, ejes = plt.subplots(1, 2, figsize=(13, 5.2))

# Subplot 1: Top 10 departamentos con mayor total de casos de dengue acumulados
top_deptos = (df_dengue.groupby("Departamento")["Casos_Reportados"]
              .sum()
              .sort_values(ascending=True)
              .tail(10))
top_deptos.plot.barh(ax=ejes[0], color="#0e7490", edgecolor="white")
ejes[0].set_title("Top 10 Departamentos por Carga Total de Dengue", fontsize=11, fontweight="bold")
ejes[0].set_xlabel("Total Casos Acumulados Históricos", fontsize=10)
ejes[0].grid(axis="x", linestyle=":", alpha=0.6)

# Subplot 2: Top 8 eventos epidemiológicos más reportados en todo el país
top_eventos = (df.groupby("Nombre_evento")["Casos_Reportados"]
               .sum()
               .sort_values(ascending=True)
               .tail(8))
top_eventos.plot.barh(ax=ejes[1], color="#d97706", edgecolor="white")
ejes[1].set_title("Top 8 Patologías más Frecuentes en Colombia (SIVIGILA)", fontsize=11, fontweight="bold")
ejes[1].set_xlabel("Total Casos Acumulados", fontsize=10)
ejes[1].grid(axis="x", linestyle=":", alpha=0.6)

plt.tight_layout()
fig3_path = ruta_figura("fig3_barras_departamentos_eventos.png")
plt.savefig(fig3_path, dpi=120)
plt.close()
print(f"\n[3] Gráficos de barras ordenadas guardados en: {fig3_path.name}")

# Tabla bivariada por departamento (ordenada por mediana)
resumen_depto = (df_dengue.groupby("Departamento")["Casos_Reportados"]
                 .agg(Registros="count", Media="mean", Mediana="median")
                 .round(1)
                 .sort_values("Mediana", ascending=False)
                 .head(10))
print("\nTop 10 Departamentos en Dengue (Mediana ordena honestamente):")
print(resumen_depto.to_string())

# ---------------------------------------------------------------------------
# FIGURA 4: DISPERSIÓN + RECTA DE TENDENCIA (CASOS VS MEDICAMENTOS VENDIDOS)
# ---------------------------------------------------------------------------
plt.figure(figsize=(8.2, 5.2))
sub_reg = df_dengue.dropna(subset=["Casos_Reportados", "Medicamentos_Vendidos"])

plt.scatter(sub_reg["Casos_Reportados"], sub_reg["Medicamentos_Vendidos"] / 1000,
            s=22, alpha=0.55, color="#0e7490", edgecolors="none")

# Ajuste por mínimos cuadrados: y = mx + b
m, b = np.polyfit(sub_reg["Casos_Reportados"], sub_reg["Medicamentos_Vendidos"] / 1000, 1)
x_vals = np.linspace(sub_reg["Casos_Reportados"].min(), sub_reg["Casos_Reportados"].max(), 100)
plt.plot(x_vals, m * x_vals + b, color="#dc2626", lw=2.5,
         label=f"Ajuste lineal: y = {m:.2f}x + {b:.1f} mil")

r_pearson = sub_reg["Casos_Reportados"].corr(sub_reg["Medicamentos_Vendidos"])

plt.xlabel("Casos Reportados Mensuales de Dengue", fontsize=11)
plt.ylabel("Medicamentos Vendidos (Miles de unidades)", fontsize=11)
plt.title(f"Casos de Dengue vs Demanda de Medicamentos (r = {r_pearson:.3f})",
          fontsize=12, fontweight="bold")
plt.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1")
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
fig4_path = ruta_figura("fig4_scatter_casos_medicamentos.png")
plt.savefig(fig4_path, dpi=120)
plt.close()

print(f"\n[4] Regresión y dispersión guardada en: {fig4_path.name}")
print(f"    Correlación de Pearson (Casos vs Medicamentos): r = {r_pearson:.3f} (Muy fuerte y positiva)")
print(f"    Ecuación estimada: Demanda_Medicamentos = {m*1000:.2f} * Casos + {b*1000:.0f}")
print(f"    Interpretación de negocio: Cada caso reportado adicional de dengue genera una demanda")
print(f"    inducida promedio de aprox. {m*1000:.1f} unidades de medicamentos asociados.")

# ---------------------------------------------------------------------------
# FIGURA 5: MAPA DE CALOR DE CORRELACIONES (HEATMAP ANOTADO)
# ---------------------------------------------------------------------------
corr_matrix = df_dengue[COLS_NUM].corr()

plt.figure(figsize=(7.5, 6))
im = plt.imshow(corr_matrix, cmap="RdBu_r", vmin=-1, vmax=1)
plt.colorbar(im, label="Coeficiente de Correlación de Pearson (r)")

n_vars = len(COLS_NUM)
etiquetas_cortas = ["Casos", "Temp (°C)", "Lluvias (mm)", "Humedad (%)", "Medicamentos"]
plt.xticks(range(n_vars), etiquetas_cortas, rotation=35, ha="right", fontsize=10)
plt.yticks(range(n_vars), etiquetas_cortas, fontsize=10)

for i in range(n_vars):
    for j in range(n_vars):
        val = corr_matrix.iloc[i, j]
        color_texto = "white" if abs(val) > 0.55 else "black"
        plt.text(j, i, f"{val:.2f}", ha="center", va="center",
                 fontsize=10, fontweight="bold", color=color_texto)

plt.title("Mapa de Calor de Correlaciones Numéricas (Dengue)", fontsize=12, fontweight="bold")
plt.tight_layout()
fig5_path = ruta_figura("fig5_heatmap_correlaciones.png")
plt.savefig(fig5_path, dpi=120)
plt.close()

print(f"\n[5] Heatmap de correlaciones guardado en: {fig5_path.name}")
print("Matriz de correlaciones numéricas:")
print(corr_matrix.round(3).to_string())

# ---------------------------------------------------------------------------
# FIGURA 6: MATRIZ DE DISPERSIÓN MULTIVARIADA (SCATTER MATRIX)
# ---------------------------------------------------------------------------
vars_pairplot = ["Temperatura_Promedio", "Lluvias_Acumuladas", "Casos_Reportados", "Medicamentos_Vendidos"]
sub_pair = df_dengue[vars_pairplot].dropna()

fig, ax = plt.subplots(figsize=(9, 9))
ejes_sm = scatter_matrix(sub_pair,
                         figsize=(9, 9),
                         diagonal="hist",
                         alpha=0.45,
                         color="#0e7490",
                         hist_kwds={"bins": 25, "color": "#0e7490", "edgecolor": "white"})
plt.suptitle("Matriz de Dispersión Multivariada (Variables Críticas del Proyecto)", y=0.92, fontsize=12, fontweight="bold")
fig6_path = ruta_figura("fig6_matriz_dispersion.png")
plt.savefig(fig6_path, dpi=120)
plt.close()
print(f"\n[6] Matriz de dispersión guardada en: {fig6_path.name}")

# ---------------------------------------------------------------------------
# FIGURA 7: CRUCE BIVARIADO DE NEGOCIO: TASA DE RIESGO DE DESABASTECIMIENTO
#           (Equivalente oficial al cruce pd.crosstab(normalize="index") de la Sesión 5)
# ---------------------------------------------------------------------------
# Capacidad instalada de inventario (regla de negocio del proyecto sin modificar)
INVENTARIO_DEPTO = {
    'ANTIOQUIA': 80000, 'VALLE DEL CAUCA': 70000, 'BOGOTA': 90000,
    'SANTANDER': 40000, 'CESAR': 35000, 'HUILA': 25000,
    'TOLIMA': 30000, 'ATLANTICO': 50000, 'BOLIVAR': 45000,
    'CORDOBA': 30000, 'NARINO': 25000, 'CHOCO': 15000,
    'NORTE SANTANDER': 35000
}

df_dengue["inventario_referencia"] = df_dengue["Departamento"].map(INVENTARIO_DEPTO).fillna(20000)
df_dengue["indice_presion"] = df_dengue["Medicamentos_Vendidos"] / df_dengue["inventario_referencia"]
df_dengue["Nivel_Riesgo"] = np.where(df_dengue["indice_presion"] >= 0.60, "Riesgo Alto",
                            np.where(df_dengue["indice_presion"] >= 0.35, "Riesgo Medio", "Riesgo Bajo"))

# Tabla de contingencia normalizada por filas (departamentos)
tabla_riesgo = pd.crosstab(df_dengue["Departamento"], df_dengue["Nivel_Riesgo"], normalize="index").round(3)
tabla_riesgo_ordenada = tabla_riesgo.sort_values(by="Riesgo Alto", ascending=False)

print("\n" + "=" * 75)
print("[B] CRUCE BIVARIADO CATEGÓRICO: TASA DE RIESGO DE DESABASTECIMIENTO")
print("=" * 75)
print("Top 12 Departamentos con mayor proporción de periodos en RIESGO ALTO:")
print((tabla_riesgo_ordenada[["Riesgo Alto", "Riesgo Medio", "Riesgo Bajo"]].head(12) * 100).round(1).to_string())

# Gráfico de barras apiladas de la tasa de riesgo por departamento
plt.figure(figsize=(10, 5.5))
colores_riesgo = {"Riesgo Alto": "#ef4444", "Riesgo Medio": "#f59e0b", "Riesgo Bajo": "#10b981"}
top_riesgo_plot = tabla_riesgo_ordenada.head(10)[["Riesgo Bajo", "Riesgo Medio", "Riesgo Alto"]]
ax_bar = top_riesgo_plot.plot(kind="barh", stacked=True, color=[colores_riesgo[c] for c in top_riesgo_plot.columns],
                              figsize=(10, 5.5), edgecolor="white")
plt.title("Proporción de Periodos por Nivel de Riesgo de Desabastecimiento (Top 10 Deptos)",
          fontsize=12, fontweight="bold")
plt.xlabel("Proporción Acumulada (1.0 = 100% de los meses analizados)", fontsize=10)
plt.ylabel("Departamento", fontsize=10)
plt.legend(title="Nivel de Riesgo", loc="lower right", frameon=True, facecolor="white")
plt.tight_layout()
fig7_path = ruta_figura("fig7_tasa_riesgo_desabastecimiento.png")
plt.savefig(fig7_path, dpi=120)
plt.close()
print(f"\n[7] Gráfica de tasa de riesgo guardada en: {fig7_path.name}")

print("\n" + "=" * 75)
print("EJECUCIÓN DEL EDA DE LA SESIÓN 5 FINALIZADA CON ÉXITO")
print(f"Todas las figuras generadas se encuentran en: {CARPETA_FIGURAS}")
print("=" * 75)
