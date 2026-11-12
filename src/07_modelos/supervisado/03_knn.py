"""Modelo 03 · K-Vecinos Más Cercanos

Ejecutar:
    python src/07_modelos/supervisado/03_knn.py
"""

import importlib
from pathlib import Path
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

prep = importlib.import_module("00_preparacion_supervisado")


def graficar_curva_k(df_k: pd.DataFrame, ruta_salida: Path) -> None:
    """Genera curva de accuracy Train vs Test y Recall Riesgo Alto según el valor de k."""
    x_pos = range(len(df_k))
    etiquetas_k = [str(k) for k in df_k["k"]]

    plt.figure(figsize=(9, 5))
    plt.plot(x_pos, df_k["acc_train"], marker="o", linewidth=2.2, label="Accuracy Train", color="#0284c7")
    plt.plot(x_pos, df_k["acc_test"], marker="s", linewidth=2.2, label="Accuracy Test", color="#7c3aed")
    plt.plot(x_pos, df_k["recall_alto"], marker="^", linestyle="--", linewidth=1.8,
             label="Recall Riesgo Alto (Test)", color="#dc2626")

    plt.xticks(list(x_pos), etiquetas_k)
    plt.ylim(0.2, 1.05)
    plt.xlabel("Número de vecinos (k)", fontsize=11)
    plt.ylabel("Puntuación (0 - 1)", fontsize=11)
    plt.title("KNN (Pipeline + RobustScaler): Efecto del Parámetro k en Generalización",
              fontsize=12, fontweight="bold")
    plt.legend(frameon=True, facecolor="white")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close()


def main() -> None:
    print("=" * 76)
    print("  MODELO 03 · K-VECINOS MÁS CERCANOS (KNeighborsClassifier)")
    print("=" * 76)

    dir_fig = prep.asegurar_directorio_figuras()
    X_train, X_test, y_train, y_test, _ = prep.obtener_particion_compartida(verbose=True)

    # 1. Comparación con y sin escalado (Regla: distancia manda a escalar)
    print("\n--- 1. IMPACTO DEL ESCALAMIENTO (k=5, SIN FUGA DE DATOS) ---")
    escaladores = {
        "KNN SIN escalar (crudo)": KNeighborsClassifier(n_neighbors=5),
        "Pipeline(StandardScaler, KNN k=5)": make_pipeline(
            StandardScaler(), KNeighborsClassifier(n_neighbors=5)
        ),
        "Pipeline(RobustScaler, KNN k=5)": make_pipeline(
            RobustScaler(), KNeighborsClassifier(n_neighbors=5)
        ),
        "Pipeline(MinMaxScaler, KNN k=5)": make_pipeline(
            MinMaxScaler(), KNeighborsClassifier(n_neighbors=5)
        ),
    }

    filas_esc = []
    for nombre_esc, modelo_esc in escaladores.items():
        res_esc = prep.evaluar_clasificador(
            nombre_esc, modelo_esc, X_train, X_test, y_train, y_test
        )
        filas_esc.append({
            "configuracion": nombre_esc,
            "acc_train": res_esc["acc_train"],
            "acc_test": res_esc["acc_test"],
            "f1_macro": res_esc["f1_macro"],
            "recall_alto": res_esc["recall_alto"],
            "t_fit_s": res_esc["t_fit"],
            "t_pred_s": res_esc["t_predict"],
        })

    df_esc = pd.DataFrame(filas_esc)
    print(df_esc.round(4).to_string(index=False))

    # 2. Barrido del parámetro k (con RobustScaler y StandardScaler para comparar)
    print("\n--- 2. BARRIDO DEL PARÁMETRO k (Pipeline + RobustScaler) ---")
    valores_k = [1, 3, 5, 7, 11, 15, 21, 31, 51, 101]
    filas_k_rob = []
    for k in valores_k:
        pipe = make_pipeline(RobustScaler(), KNeighborsClassifier(n_neighbors=k))
        res_k = prep.evaluar_clasificador(
            f"KNN_Robust_k={k}", pipe, X_train, X_test, y_train, y_test
        )
        filas_k_rob.append({
            "k": k,
            "acc_train": res_k["acc_train"],
            "acc_test": res_k["acc_test"],
            "brecha": res_k["brecha"],
            "f1_macro": res_k["f1_macro"],
            "recall_alto": res_k["recall_alto"],
            "t_fit_s": res_k["t_fit"],
            "t_pred_s": res_k["t_predict"],
        })

    df_k_rob = pd.DataFrame(filas_k_rob)
    print(df_k_rob.round(4).to_string(index=False))

    ruta_curva_k = dir_fig / "knn_curva_k_escalado.png"
    graficar_curva_k(df_k_rob, ruta_curva_k)
    print(f"\n[OK] Curva de k guardada en: {ruta_curva_k}")

    print("\n--- 2B. BARRIDO DEL PARÁMETRO k (Pipeline + StandardScaler) ---")
    filas_k_std = []
    for k in valores_k:
        pipe = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
        res_k = prep.evaluar_clasificador(
            f"KNN_Std_k={k}", pipe, X_train, X_test, y_train, y_test
        )
        filas_k_std.append({
            "k": k,
            "acc_train": res_k["acc_train"],
            "acc_test": res_k["acc_test"],
            "f1_macro": res_k["f1_macro"],
            "recall_alto": res_k["recall_alto"],
        })
    df_k_std = pd.DataFrame(filas_k_std)
    print(df_k_std.round(4).to_string(index=False))

    # 3. Experimentos adicionales de Sesión 8: weights="distance" y métrica Manhattan
    mejor_fila_rob = df_k_rob.sort_values(by=["acc_test", "f1_macro"], ascending=False).iloc[0]
    k_optimo = int(mejor_fila_rob["k"])

    print(f"\n--- 3. VARIANTES DE PESO Y DISTANCIA (k={k_optimo}) ---")
    variantes_knn = {
        f"RobustScaler + Euclidean + uniform (k={k_optimo})": make_pipeline(
            RobustScaler(), KNeighborsClassifier(n_neighbors=k_optimo, weights="uniform", metric="euclidean")
        ),
        f"RobustScaler + Euclidean + distance (k={k_optimo})": make_pipeline(
            RobustScaler(), KNeighborsClassifier(n_neighbors=k_optimo, weights="distance", metric="euclidean")
        ),
        f"RobustScaler + Manhattan + distance (k={k_optimo})": make_pipeline(
            RobustScaler(), KNeighborsClassifier(n_neighbors=k_optimo, weights="distance", metric="manhattan")
        ),
        f"StandardScaler + Euclidean + distance (k={k_optimo})": make_pipeline(
            StandardScaler(), KNeighborsClassifier(n_neighbors=k_optimo, weights="distance", metric="euclidean")
        ),
        "RobustScaler + k=5 + distance (solo 6 numéricas)": None,
    }

    filas_var = []
    for nombre_var, modelo_var in variantes_knn.items():
        if modelo_var is None:
            res_var = prep.evaluar_clasificador(
                nombre_var,
                make_pipeline(RobustScaler(), KNeighborsClassifier(n_neighbors=5, weights="distance")),
                X_train[prep.COLUMNAS_NUMERICAS],
                X_test[prep.COLUMNAS_NUMERICAS],
                y_train,
                y_test,
            )
        else:
            res_var = prep.evaluar_clasificador(
                nombre_var, modelo_var, X_train, X_test, y_train, y_test
            )
        filas_var.append({
            "variante": nombre_var,
            "acc_train": res_var["acc_train"],
            "acc_test": res_var["acc_test"],
            "f1_macro": res_var["f1_macro"],
            "recall_alto": res_var["recall_alto"],
            "t_pred_s": res_var["t_predict"],
        })

    df_var = pd.DataFrame(filas_var)
    print(df_var.round(4).to_string(index=False))

    # 4. Reporte detallado del mejor KNN estándar del curso (RobustScaler, k_optimo, weights="uniform")
    print(f"\n--- 4. DETALLE MODELO KNN SELECCIONADO (RobustScaler, k={k_optimo}) ---")
    knn_final = make_pipeline(RobustScaler(), KNeighborsClassifier(n_neighbors=k_optimo))
    res_final = prep.evaluar_clasificador(
        f"KNN (RobustScaler, k={k_optimo})", knn_final, X_train, X_test, y_train, y_test
    )
    print("\nReporte de clasificación (Test):")
    print(res_final["reporte_texto"])

    print("Matriz de confusión (filas=Real, columnas=Predicho):")
    df_cm = pd.DataFrame(
        res_final["matriz_confusion"],
        index=[f"Real: {c}" for c in prep.CLASES_ORDEN],
        columns=[f"Pred: {c}" for c in prep.CLASES_ORDEN],
    )
    print(df_cm.to_string())

    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=res_final["matriz_confusion"],
        display_labels=prep.CLASES_ORDEN,
    )
    disp.plot(ax=ax, cmap="Purples", colorbar=False)
    ax.set_title(f"Matriz de Confusión - KNN (RobustScaler, k={k_optimo})")
    plt.tight_layout()
    ruta_cm = dir_fig / "knn_confusion.png"
    plt.savefig(ruta_cm, dpi=150)
    plt.close()
    print(f"\n[OK] Matriz de confusión guardada en: {ruta_cm}")


if __name__ == "__main__":
    main()

