"""Preparación compartida para clasificación supervisada.
    Audita calidad del dataset
    Filtra el caso de estudio DENGUE y construye el target
    
    Ejecutar verificación:
    python src/07_modelos/supervisado/00_preparacion_supervisado.py
"""

from pathlib import Path
import time
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parents[3]
RUTA_DATASET = BASE_DIR / "datos_procesados" / "dataset_final_crisp_dm_mejorado.csv"
DIR_FIGURAS = BASE_DIR / "img" / "modelos" / "supervisado"

RANDOM_STATE = 42
TEST_SIZE = 0.25
CLASES_ORDEN = ["Riesgo Bajo", "Riesgo Medio", "Riesgo Alto"]

COLUMNAS_NUMERICAS = [
    "ANO",
    "mes",
    "Temperatura_Promedio",
    "Lluvias_Acumuladas",
    "Humedad_Ambiente",
    "Casos_Reportados",
]
COLUMNAS_CATEGORICAS = ["Departamento"]

# Capacidad instalada departamental de referencia  con eda_proyecto.py
INVENTARIO_DEPTO = {
    "ANTIOQUIA": 80000,
    "VALLE DEL CAUCA": 70000,
    "BOGOTA": 90000,
    "SANTANDER": 40000,
    "CESAR": 35000,
    "HUILA": 25000,
    "TOLIMA": 30000,
    "ATLANTICO": 50000,
    "BOLIVAR": 45000,
    "CORDOBA": 30000,
    "NARINO": 25000,
    "CHOCO": 15000,
    "NORTE SANTANDER": 35000,
}


def asegurar_directorio_figuras() -> Path:
    #Se crea la carpeta de salida para las gráficas del módulo supervisado.
    DIR_FIGURAS.mkdir(parents=True, exist_ok=True)
    return DIR_FIGURAS


def cargar_datos_dengue(verbose: bool = True) -> pd.DataFrame:
    # Cargamos el dataset.
    if not RUTA_DATASET.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset en {RUTA_DATASET}. "
            "Ejecuta primero src/02_preparacion/preparacion_datos_mejorado.py"
        )

    df = pd.read_csv(RUTA_DATASET)
    df_dengue = df[df["Nombre_evento"] == "DENGUE"].copy().reset_index(drop=True)

    nulos = int(df_dengue.isna().sum().sum())
    duplicados = int(df_dengue.duplicated().sum())
    assert nulos == 0, f"Se detectaron {nulos} valores nulos en DENGUE."
    assert duplicados == 0, f"Se detectaron {duplicados} filas duplicadas en DENGUE."

    # Construcción del target Nivel_Riesgo según la regla oficial de eda_proyecto.py
    df_dengue["inventario_referencia"] = (
        df_dengue["Departamento"].map(INVENTARIO_DEPTO).fillna(20000)
    )
    df_dengue["indice_presion"] = (
        df_dengue["Medicamentos_Vendidos"] / df_dengue["inventario_referencia"]
    )
    df_dengue["Nivel_Riesgo"] = np.where(
        df_dengue["indice_presion"] >= 0.60,
        "Riesgo Alto",
        np.where(df_dengue["indice_presion"] >= 0.35, "Riesgo Medio", "Riesgo Bajo"),
    )

    if verbose:
        print("=== AUDITORÍA DE DATOS (DENGUE) ===")
        print(f"Dataset completo : {df.shape[0]:,} filas x {df.shape[1]} columnas")
        print(f"Subconjunto DENGUE: {df_dengue.shape[0]:,} filas x {df_dengue.shape[1]} columnas")
        print(f"Nulos totales    : {nulos}")
        print(f"Duplicados       : {duplicados}")
        print("\nDistribución de clases (Nivel_Riesgo):")
        conteo = df_dengue["Nivel_Riesgo"].value_counts().reindex(CLASES_ORDEN)
        pct = (conteo / len(df_dengue) * 100).round(1)
        for clase in CLASES_ORDEN:
            print(f"  {clase:<14}: {int(conteo[clase]):>4} ({pct[clase]:>5.1f}%)")

    return df_dengue


def preparar_matriz_x_y(
    df_dengue: pd.DataFrame, verbose: bool = True
) -> tuple[pd.DataFrame, pd.Series]:
    
    columnas_entrada = COLUMNAS_NUMERICAS + COLUMNAS_CATEGORICAS
    X = pd.get_dummies(
        df_dengue[columnas_entrada],
        columns=COLUMNAS_CATEGORICAS,
        dtype=int,
    )
    y = df_dengue["Nivel_Riesgo"]

    # Guardia estricta contra fuga de datos: la fuente directa del target no entra a X
    for col_prohibida in ("Medicamentos_Vendidos", "indice_presion", "inventario_referencia"):
        assert col_prohibida not in X.columns, f"Fuga de datos detectada: {col_prohibida} en X"

    if verbose:
        print(f"\nMatriz X: {X.shape[0]:,} filas x {X.shape[1]} columnas "
              f"({len(COLUMNAS_NUMERICAS)} numéricas + {X.shape[1] - len(COLUMNAS_NUMERICAS)} dummies)")

    return X, y


def obtener_particion_compartida(
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.DataFrame]:
    #Retorna la partición única estratificada train/test compartida.
    df_dengue = cargar_datos_dengue(verbose=verbose)
    X, y = preparar_matriz_x_y(df_dengue, verbose=verbose)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    if verbose:
        print(
            f"Partición única (random_state={RANDOM_STATE}, stratify=y): "
            f"Train={len(X_train):,} ({1 - TEST_SIZE:.0%}) | "
            f"Test={len(X_test):,} ({TEST_SIZE:.0%})"
        )

    return X_train, X_test, y_train, y_test, df_dengue


def evaluar_clasificador(
    nombre: str,
    modelo: Any,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> dict[str, Any]:
    # Entrena un clasificador, mide tiempos de fit/predict y calcula métricas clave.
    t0 = time.perf_counter()
    modelo.fit(X_train, y_train)
    t_fit = time.perf_counter() - t0

    y_pred_train = modelo.predict(X_train)

    t1 = time.perf_counter()
    y_pred_test = modelo.predict(X_test)
    t_predict = time.perf_counter() - t1

    acc_train = accuracy_score(y_train, y_pred_train)
    acc_test = accuracy_score(y_test, y_pred_test)
    precision_macro = precision_score(y_test, y_pred_test, average="macro", zero_division=0)
    recall_macro = recall_score(y_test, y_pred_test, average="macro", zero_division=0)
    f1_macro = f1_score(y_test, y_pred_test, average="macro", zero_division=0)

    recalls_por_clase = recall_score(
        y_test, y_pred_test, labels=CLASES_ORDEN, average=None, zero_division=0
    )
    recall_alto = float(recalls_por_clase[CLASES_ORDEN.index("Riesgo Alto")])

    matriz_conf = confusion_matrix(y_test, y_pred_test, labels=CLASES_ORDEN)
    reporte_texto = classification_report(
        y_test, y_pred_test, labels=CLASES_ORDEN, digits=3, zero_division=0
    )

    return {
        "modelo": nombre,
        "objeto": modelo,
        "acc_train": float(acc_train),
        "acc_test": float(acc_test),
        "brecha": float(acc_train - acc_test),
        "precision_macro": float(precision_macro),
        "recall_macro": float(recall_macro),
        "f1_macro": float(f1_macro),
        "recall_alto": recall_alto,
        "t_fit": float(t_fit),
        "t_predict": float(t_predict),
        "y_pred_test": y_pred_test,
        "matriz_confusion": matriz_conf,
        "reporte_texto": reporte_texto,
    }


def main() -> None:
    print("=" * 72)
    print("  MÓDULO 00 · VERIFICACIÓN DE DATOS Y PARTICIÓN COMPARTIDA")
    print("=" * 72)
    X_train, X_test, y_train, y_test, _ = obtener_particion_compartida(verbose=True)

    print("\nDistribución en Train vs Test (%):")
    dist_train = (y_train.value_counts(normalize=True).reindex(CLASES_ORDEN) * 100).round(2)
    dist_test = (y_test.value_counts(normalize=True).reindex(CLASES_ORDEN) * 100).round(2)
    tabla_split = pd.DataFrame({"Train_%": dist_train, "Test_%": dist_test})
    print(tabla_split.to_string())


if __name__ == "__main__":
    main()

