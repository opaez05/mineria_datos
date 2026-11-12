"""Módulo 04 · Comparacion de todos los Modelos Supervisados

  1. Evalúa los 3 clasificadores oficiales (Árbol de Decisión, Naive Bayes y KNN)
     bajo exactamente la misma partición de ``00_preparacion_supervisado.py``.
  2. Genera gráficas comparativas y matrices de confusión lado a lado.

Ejecutar:
    python src/07_modelos/supervisado/04_torneo_comparacion.py
"""

import importlib
from pathlib import Path
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.tree import DecisionTreeClassifier

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

prep = importlib.import_module("00_preparacion_supervisado")


def ejecutar_ronda(
    modelos: dict,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> tuple[pd.DataFrame, list[dict]]:
    # Entrena y evalúa un diccionario de modelos retornando tabla y resultados completos.
    resultados = []
    filas = []
    for nombre, modelo in modelos.items():
        res = prep.evaluar_clasificador(nombre, modelo, X_train, X_test, y_train, y_test)
        resultados.append(res)
        filas.append({
            "modelo": nombre,
            "acc_train": res["acc_train"],
            "acc_test": res["acc_test"],
            "brecha": res["brecha"],
            "precision_macro": res["precision_macro"],
            "recall_macro": res["recall_macro"],
            "f1_macro": res["f1_macro"],
            "recall_alto": res["recall_alto"],
            "t_fit_s": res["t_fit"],
            "t_pred_s": res["t_predict"],
        })
    df_tabla = pd.DataFrame(filas)
    return df_tabla, resultados


def graficar_comparacion_metricas(df_ronda_a: pd.DataFrame, df_ronda_b: pd.DataFrame, ruta_salida: Path) -> None:
    # Se genera gráfico comparativo de barras para Ronda Estándar y Ronda Optimizada.
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)

    for ax, df_tab, titulo in [
        (axes[0], df_ronda_a, "Ronda A: Estándar de Sesión 8 (Baseline)"),
        (axes[1], df_ronda_b, "Ronda B: Mejores Configuraciones Validadas"),
    ]:
        x = np.arange(len(df_tab))
        ancho = 0.25

        b1 = ax.bar(x - ancho, df_tab["acc_train"], width=ancho, label="Acc Train", color="#38bdf8")
        b2 = ax.bar(x, df_tab["acc_test"], width=ancho, label="Acc Test", color="#10b981")
        b3 = ax.bar(x + ancho, df_tab["f1_macro"], width=ancho, label="F1 Macro (Test)", color="#8b5cf6")

        for barras in (b1, b2, b3):
            for bar in barras:
                h = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    h + 0.015,
                    f"{h:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        ax.set_xticks(x)
        ax.set_xticklabels(df_tab["modelo"], rotation=15, ha="right", fontsize=9)
        ax.set_ylim(0, 1.05)
        ax.set_title(titulo, fontsize=11, fontweight="bold")
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        ax.legend(frameon=True, facecolor="white", fontsize=8.5)

    axes[0].set_ylabel("Puntuación (0 - 1)", fontsize=10.5)
    plt.suptitle(
        "Torneo de Clasificación Supervisada · Predicción de Nivel_Riesgo (Dengue)",
        fontsize=13,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close()


def graficar_matrices_confusion(resultados: list[dict], titulo_general: str, ruta_salida: Path) -> None:
    # Dibuja las matrices de confusión lado a lado para los competidores del torneo.
    n = len(resultados)
    fig, axes = plt.subplots(1, n, figsize=(5.2 * n, 4.8))
    if n == 1:
        axes = [axes]

    cmaps = ["Greens", "Blues", "Purples", "Oranges"]
    for idx, (ax, res) in enumerate(zip(axes, resultados)):
        disp = ConfusionMatrixDisplay(
            confusion_matrix=res["matriz_confusion"],
            display_labels=["Bajo", "Medio", "Alto"],
        )
        disp.plot(ax=ax, cmap=cmaps[idx % len(cmaps)], colorbar=False)
        ax.set_title(f"{res['modelo']}\nAcc Test: {res['acc_test']:.3f} | Rec Alto: {res['recall_alto']:.3f}",
                     fontsize=10, fontweight="bold")
        ax.set_xlabel("Predicho")
        ax.set_ylabel("Real" if idx == 0 else "")

    plt.suptitle(titulo_general, fontsize=12.5, fontweight="bold")
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close()


def main() -> None:
    print("=" * 80)
    print("  MÓDULO 04 · TORNEO COMPARATIVO DE CLASIFICACIÓN SUPERVISADA (SESIÓN 8)")
    print("=" * 80)

    dir_fig = prep.asegurar_directorio_figuras()
    X_train, X_test, y_train, y_test, _ = prep.obtener_particion_compartida(verbose=True)

    # Ronda A: configuraciones base exactamente equivalentes a comparacion_modelos.py
    modelos_ronda_a = {
        "Arbol (prof=4)": DecisionTreeClassifier(max_depth=4, random_state=prep.RANDOM_STATE),
        "Naive Bayes": GaussianNB(),
        "KNN Std (k=5)": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
        "KNN Rob (k=5)": make_pipeline(RobustScaler(), KNeighborsClassifier(n_neighbors=5)),
    }

    print("\n--- RONDA A · CONFIGURACIONES ESTÁNDAR DE SESIÓN 8 ---")
    df_a, res_a = ejecutar_ronda(modelos_ronda_a, X_train, X_test, y_train, y_test)
    print(df_a.round(4).to_string(index=False))

    # Ronda B: mejores configuraciones validadas en 01, 02 y 03
    modelos_ronda_b = {
        "Arbol (prof=8)": DecisionTreeClassifier(max_depth=8, random_state=prep.RANDOM_STATE),
        "Arbol Bal (prof=4)": DecisionTreeClassifier(
            max_depth=4, class_weight="balanced", random_state=prep.RANDOM_STATE
        ),
        "NB (smooth=1e-3)": GaussianNB(var_smoothing=1e-3),
        "KNN Std (k=11)": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=11)),
        "KNN Rob Manh (k=7)": make_pipeline(
            RobustScaler(), KNeighborsClassifier(n_neighbors=7, weights="distance", metric="manhattan")
        ),
    }

    print("\n--- RONDA B · MEJORES VARIANTES POR FAMILIA (EXPLORACIÓN DE HIPERPARÁMETROS) ---")
    df_b, res_b = ejecutar_ronda(modelos_ronda_b, X_train, X_test, y_train, y_test)
    print(df_b.round(4).to_string(index=False))

    # Matrices de confusión de los 3 ganadores representativos por familia
    ganadores_familia = [res_b[0], res_a[1], res_b[3]]  # Arbol prof=8, Naive Bayes base, KNN Std k=11

    ruta_metricas = dir_fig / "torneo_comparacion_metricas.png"
    graficar_comparacion_metricas(df_a, df_b, ruta_metricas)
    print(f"\n[OK] Gráfica comparativa guardada en: {ruta_metricas}")

    ruta_cm_a = dir_fig / "torneo_matrices_confusion.png"
    graficar_matrices_confusion(
        ganadores_familia,
        "Matrices de Confusión Comparadas (Mejor Representante por Familia)",
        ruta_cm_a,
    )
    print(f"[OK] Matrices de confusión comparadas guardadas en: {ruta_cm_a}")

    # Resumen objetivo para toma de decisión
    ganador_acc = df_b.sort_values(by=["acc_test", "f1_macro"], ascending=False).iloc[0]
    ganador_std = df_a.sort_values(by=["acc_test", "f1_macro"], ascending=False).iloc[0]
    print("\n--- VEREDICTO CUANTITATIVO DEL TORNEO ---")
    print(
        f"Ganador Ronda Estándar (Sesión 8): {ganador_std['modelo']} | "
        f"Acc Test={ganador_std['acc_test']:.4f} | Brecha={ganador_std['brecha']:.4f}"
    )
    print(
        f"Ganador Ronda Optimizada         : {ganador_acc['modelo']} | "
        f"Acc Test={ganador_acc['acc_test']:.4f} | F1 Macro={ganador_acc['f1_macro']:.4f}"
    )


if __name__ == "__main__":
    main()

