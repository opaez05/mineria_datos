"""Árbol de Decisión

  1. Utiliza la partición compartida y auditada de ``00_preparacion_supervisado.py``.
  2. Evalúa el impacto de ``max_depth`` en [2, 3, 4, 5, 8, None] para detectar sobreajuste.
  3. Entrena el árbol podado final, genera gráfica legible (plot_tree) y curva de poda.
  4. Extrae reglas interpretables con ``export_text`` y ranking ``feature_importances_``.
  5. Evalúa alternativa con ``class_weight="balanced"`` para proteger Recall en Riesgo Alto.

Ejecutar:
    python src/07_modelos/supervisado/01_arbol_decision.py
"""

import importlib
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

prep = importlib.import_module("00_preparacion_supervisado")

PROFUNDIDAD_FINAL = 4


def graficar_curva_profundidad(df_prof: pd.DataFrame, ruta_salida: Path) -> None:
    etiquetas_x = [str(p) for p in df_prof["profundidad"]]
    x_pos = range(len(etiquetas_x))

    plt.figure(figsize=(8.5, 5))
    plt.plot(x_pos, df_prof["acc_train"], marker="o", linewidth=2.2, label="Accuracy Train", color="#0284c7")
    plt.plot(x_pos, df_prof["acc_test"], marker="s", linewidth=2.2, label="Accuracy Test", color="#059669")
    plt.plot(x_pos, df_prof["recall_alto"], marker="^", linestyle="--", linewidth=1.8,
             label="Recall Riesgo Alto (Test)", color="#dc2626")

    plt.xticks(list(x_pos), etiquetas_x)
    plt.ylim(-0.04, 1.05)
    plt.xlabel("Profundidad máxima (max_depth)", fontsize=11)
    plt.ylabel("Puntuación (0 - 1)", fontsize=11)
    plt.title("Árbol de Decisión: Diagnóstico de Sobreajuste por Profundidad", fontsize=12, fontweight="bold")
    plt.legend(frameon=True, facecolor="white")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close()


def graficar_arbol(arbol: DecisionTreeClassifier, columnas: list[str], ruta_salida: Path) -> None:
    # Dibujamos el árbol podado con etiquetas exactas según arbol.classes_
    plt.figure(figsize=(24, 11))
    plot_tree(
        arbol,
        feature_names=columnas,
        class_names=[str(c) for c in arbol.classes_],
        filled=True,
        rounded=True,
        fontsize=8,
    )
    plt.title(
        f"Árbol de Decisión Podado (max_depth={arbol.max_depth}) - Nivel de Riesgo de Desabastecimiento",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close()


def main() -> None:
    print("=" * 76)
    print("  MODELO 01 · ÁRBOL DE DECISIÓN")
    print("=" * 76)

    dir_fig = prep.asegurar_directorio_figuras()
    X_train, X_test, y_train, y_test, _ = prep.obtener_particion_compartida(verbose=True)

    # 1. Barrido de profundidades (estilo arbol_fuga.py)
    print("\n--- 1. EXPERIMENTO DE PROFUNDIDAD (DETECCIÓN DE SOBREAJUSTE) ---")
    registros_prof = []
    for prof in [2, 3, 4, 5, 8, None]:
        clf = DecisionTreeClassifier(max_depth=prof, random_state=prep.RANDOM_STATE)
        res = prep.evaluar_clasificador(
            f"Arbol (prof={prof})", clf, X_train, X_test, y_train, y_test
        )
        registros_prof.append({
            "profundidad": str(prof) if prof is not None else "sin limite",
            "acc_train": res["acc_train"],
            "acc_test": res["acc_test"],
            "brecha": res["brecha"],
            "f1_macro": res["f1_macro"],
            "recall_alto": res["recall_alto"],
            "t_fit": res["t_fit"],
        })

    df_prof = pd.DataFrame(registros_prof)
    print(df_prof.round(4).to_string(index=False))

    ruta_curva = dir_fig / "arbol_decision_profundidades.png"
    graficar_curva_profundidad(df_prof, ruta_curva)
    print(f"\n[OK] Curva de profundidades guardada en: {ruta_curva}")

    # 2. Modelo final legible (poda controlada)
    print(f"\n--- 2. ÁRBOL FINAL LEGIBLE (max_depth={PROFUNDIDAD_FINAL}) ---")
    arbol_final = DecisionTreeClassifier(
        max_depth=PROFUNDIDAD_FINAL, random_state=prep.RANDOM_STATE
    )
    res_final = prep.evaluar_clasificador(
        f"Arbol (prof={PROFUNDIDAD_FINAL})", arbol_final, X_train, X_test, y_train, y_test
    )
    print(
        f"Accuracy Train: {res_final['acc_train']:.4f} | "
        f"Accuracy Test: {res_final['acc_test']:.4f} | "
        f"Brecha: {res_final['brecha']:.4f}"
    )
    print(
        f"Precision Macro: {res_final['precision_macro']:.4f} | "
        f"Recall Macro: {res_final['recall_macro']:.4f} | "
        f"F1 Macro: {res_final['f1_macro']:.4f} | "
        f"Recall Riesgo Alto: {res_final['recall_alto']:.4f}"
    )
    print(
        f"Tiempo fit: {res_final['t_fit']:.4f}s | "
        f"Tiempo predict: {res_final['t_predict']:.4f}s"
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

    # 3. Extracción de reglas e importancia de variables
    print("\n--- 3. REGLAS DEL ÁRBOL (export_text) ---")
    print(export_text(arbol_final, feature_names=list(X_train.columns)))

    importancias = pd.Series(
        arbol_final.feature_importances_, index=X_train.columns
    ).sort_values(ascending=False)
    print("--- 4. IMPORTANCIA DE VARIABLES (TOP 10) ---")
    for nombre_var, valor in importancias.head(10).items():
        if valor > 0:
            print(f"  {nombre_var:<32} {valor:.4f}")

    ruta_arbol = dir_fig / "arbol_decision_dengue.png"
    graficar_arbol(arbol_final, list(X_train.columns), ruta_arbol)
    print(f"\n[OK] Diagrama del árbol guardado en: {ruta_arbol}")

    # 4. Experimento complementario: balanceo de clases
    print("\n--- 5. VERIFICACIÓN CON class_weight='balanced' (SENSIBILIDAD RIESGO ALTO) ---")
    arbol_bal = DecisionTreeClassifier(
        max_depth=PROFUNDIDAD_FINAL,
        class_weight="balanced",
        random_state=prep.RANDOM_STATE,
    )
    res_bal = prep.evaluar_clasificador(
        f"Arbol balanceado (prof={PROFUNDIDAD_FINAL})", arbol_bal, X_train, X_test, y_train, y_test
    )
    print(
        f"Accuracy Test: {res_bal['acc_test']:.4f} | "
        f"F1 Macro: {res_bal['f1_macro']:.4f} | "
        f"Recall Riesgo Alto: {res_bal['recall_alto']:.4f}"
    )

    # Guardar matriz de confusión individual
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=res_final["matriz_confusion"],
        display_labels=prep.CLASES_ORDEN,
    )
    disp.plot(ax=ax, cmap="Greens", colorbar=False)
    ax.set_title(f"Matriz de Confusión - Árbol de Decisión (prof={PROFUNDIDAD_FINAL})")
    plt.tight_layout()
    ruta_cm = dir_fig / "arbol_decision_confusion.png"
    plt.savefig(ruta_cm, dpi=150)
    plt.close()
    print(f"[OK] Matriz de confusión guardada en: {ruta_cm}")


if __name__ == "__main__":
    main()
