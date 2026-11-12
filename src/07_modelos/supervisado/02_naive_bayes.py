"""Modelo 02 · Naive Bayes
Ejecutar:
    python src/07_modelos/supervisado/02_naive_bayes.py
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
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PowerTransformer, RobustScaler, StandardScaler

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

prep = importlib.import_module("00_preparacion_supervisado")


def graficar_confianza_probabilidades(
    y_test: pd.Series,
    y_pred: np.ndarray,
    probs: np.ndarray,
    ruta_salida: Path,
) -> None:
    # Grafica la distribución de probabilidad máxima predicha en aciertos vs errores.
    max_probs = probs.max(axis=1)
    aciertos = y_pred == y_test.to_numpy()

    plt.figure(figsize=(8.5, 4.8))
    plt.hist(
        max_probs[aciertos],
        bins=15,
        alpha=0.7,
        label=f"Aciertos (n={aciertos.sum()})",
        color="#059669",
        edgecolor="white",
    )
    plt.hist(
        max_probs[~aciertos],
        bins=15,
        alpha=0.7,
        label=f"Errores (n={(~aciertos).sum()})",
        color="#dc2626",
        edgecolor="white",
    )
    plt.xlabel("Probabilidad máxima reportada por GaussianNB", fontsize=11)
    plt.ylabel("Cantidad de registros (Test)", fontsize=11)
    plt.title(
        "Auditoría de Calibración en Naive Bayes: Confianza en Aciertos vs Errores",
        fontsize=12,
        fontweight="bold",
    )
    plt.legend(frameon=True, facecolor="white")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close()


def main() -> None:
    print("=" * 76)
    print("  MODELO 02 · NAIVE BAYES (GaussianNB)")
    print("=" * 76)

    dir_fig = prep.asegurar_directorio_figuras()
    X_train, X_test, y_train, y_test, _ = prep.obtener_particion_compartida(verbose=True)

    # 1. Modelo base estilo Sesión 8 (GaussianNB sin escalar)
    print("\n--- 1. MODELO BASE: GaussianNB (SIN ESCALAR) ---")
    nb_base = GaussianNB()
    res_base = prep.evaluar_clasificador(
        "Naive Bayes (base)", nb_base, X_train, X_test, y_train, y_test
    )
    print(
        f"Accuracy Train: {res_base['acc_train']:.4f} | "
        f"Accuracy Test: {res_base['acc_test']:.4f} | "
        f"Brecha: {res_base['brecha']:.4f}"
    )
    print(
        f"Precision Macro: {res_base['precision_macro']:.4f} | "
        f"Recall Macro: {res_base['recall_macro']:.4f} | "
        f"F1 Macro: {res_base['f1_macro']:.4f} | "
        f"Recall Riesgo Alto: {res_base['recall_alto']:.4f}"
    )
    print(
        f"Tiempo fit: {res_base['t_fit']:.4f}s | "
        f"Tiempo predict: {res_base['t_predict']:.4f}s"
    )

    print("\nReporte de clasificación (Test):")
    print(res_base["reporte_texto"])

    print("Matriz de confusión (filas=Real, columnas=Predicho):")
    df_cm = pd.DataFrame(
        res_base["matriz_confusion"],
        index=[f"Real: {c}" for c in prep.CLASES_ORDEN],
        columns=[f"Pred: {c}" for c in prep.CLASES_ORDEN],
    )
    print(df_cm.to_string())

    # 2. Auditoría de calibración de probabilidades (Error 1 de Sesión 8)
    probs_test = nb_base.predict_proba(X_test)
    max_probs = probs_test.max(axis=1)
    aciertos = res_base["y_pred_test"] == y_test.to_numpy()
    errores_alta_conf = int(((~aciertos) & (max_probs >= 0.90)).sum())
    print("\n--- 2. AUDITORÍA DE PROBABILIDADES (predict_proba) ---")
    print(f"Confianza promedio en aciertos : {max_probs[aciertos].mean():.4f}")
    print(f"Confianza promedio en errores  : {max_probs[~aciertos].mean():.4f}")
    print(f"Errores con confianza >= 90%   : {errores_alta_conf} de {(~aciertos).sum()} errores")

    ruta_probs = dir_fig / "naive_bayes_probabilidades.png"
    graficar_confianza_probabilidades(y_test, res_base["y_pred_test"], probs_test, ruta_probs)
    print(f"[OK] Gráfica de probabilidades guardada en: {ruta_probs}")

    # 3. Verificación de invariancia al escalamiento y experimentos de mejora
    print("\n--- 3. EXPERIMENTOS DE PREPROCESAMIENTO Y var_smoothing ---")
    variantes = {
        "GaussianNB crudo (default)": GaussianNB(),
        "Pipeline(StandardScaler, GNB)": make_pipeline(StandardScaler(), GaussianNB()),
        "Pipeline(RobustScaler, GNB)": make_pipeline(RobustScaler(), GaussianNB()),
        "Pipeline(PowerTransformer, GNB)": make_pipeline(PowerTransformer(), GaussianNB()),
        "GaussianNB (var_smoothing=1e-3)": GaussianNB(var_smoothing=1e-3),
        "GaussianNB (var_smoothing=1e-1)": GaussianNB(var_smoothing=1e-1),
        "GaussianNB (solo 6 numéricas)": None,
    }

    filas_exp = []
    for nombre_var, modelo_var in variantes.items():
        if nombre_var == "GaussianNB (solo 6 numéricas)":
            X_tr_sub = X_train[prep.COLUMNAS_NUMERICAS]
            X_te_sub = X_test[prep.COLUMNAS_NUMERICAS]
            res_var = prep.evaluar_clasificador(
                nombre_var, GaussianNB(), X_tr_sub, X_te_sub, y_train, y_test
            )
        else:
            res_var = prep.evaluar_clasificador(
                nombre_var, modelo_var, X_train, X_test, y_train, y_test
            )
        filas_exp.append({
            "variante": nombre_var,
            "acc_train": res_var["acc_train"],
            "acc_test": res_var["acc_test"],
            "f1_macro": res_var["f1_macro"],
            "recall_alto": res_var["recall_alto"],
        })

    df_exp = pd.DataFrame(filas_exp)
    print(df_exp.round(4).to_string(index=False))

    # 4. Guardar matriz de confusión individual
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=res_base["matriz_confusion"],
        display_labels=prep.CLASES_ORDEN,
    )
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Matriz de Confusión - Naive Bayes (GaussianNB)")
    plt.tight_layout()
    ruta_cm = dir_fig / "naive_bayes_confusion.png"
    plt.savefig(ruta_cm, dpi=150)
    plt.close()
    print(f"\n[OK] Matriz de confusión guardada en: {ruta_cm}")


if __name__ == "__main__":
    main()

