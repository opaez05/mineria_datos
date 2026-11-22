"""
Aplicación de Métodos Numéricos sobre una muestra real del proyecto:
Predicción de Brotes Epidemiológicos y Desabastecimiento de Medicamentos (Colombia).

Muestra seleccionada:
  - Departamento: TOLIMA
  - Evento epidemiológico: DENGUE (COD_EVE = 210)
  - Periodo: Primer semestre de 2019 (meses 1 a 6) + mes 7 como validación fuera de muestra.

Métodos aplicados:
  1. Regresión lineal por mínimos cuadrados:
       x = Casos_Reportados, y = Medicamentos_Vendidos (n = 6, meses 1..6)
       Validación de extrapolación en mes 7 (x = 1667, y_real = 29729).
  2. Interpolación polinomial de Lagrange (grado 2):
       Nodos temporales (mes, Casos_Reportados): (1, 512), (3, 821), (6, 1121)
       Validación de interpolación en mes 5 (x = 5, y_real = 1099).

Uso:
  python matematicas/aplicacion_metodos_numericos.py
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MAT_DIR = Path(__file__).resolve().parent
DATASET_PATH = ROOT / "datos_procesados" / "dataset_final_crisp_dm_mejorado.csv"
SAMPLE_CSV_PATH = MAT_DIR / "muestra_tolima_dengue_2019.csv"
RESULTS_JSON_PATH = MAT_DIR / "resultados_metodos_numericos.json"


def cargar_muestra_tolima_2019() -> list[dict]:
    """Extrae los meses 1..7 de TOLIMA · DENGUE · 2019 desde el dataset procesado."""
    fuente = DATASET_PATH if DATASET_PATH.exists() else SAMPLE_CSV_PATH
    filas: list[dict] = []
    with fuente.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (
                row.get("Departamento", "").strip().upper() == "TOLIMA"
                and row.get("Nombre_evento", "").strip().upper() == "DENGUE"
                and int(row["ANO"]) == 2019
                and 1 <= int(row["mes"]) <= 7
            ):
                filas.append(
                    {
                        "Departamento": row["Departamento"].strip(),
                        "ANO": int(row["ANO"]),
                        "mes": int(row["mes"]),
                        "COD_EVE": int(row["COD_EVE"]),
                        "Nombre_evento": row["Nombre_evento"].strip(),
                        "Casos_Reportados": float(row["Casos_Reportados"]),
                        "Temperatura_Promedio": float(row["Temperatura_Promedio"]),
                        "Lluvias_Acumuladas": float(row["Lluvias_Acumuladas"]),
                        "Humedad_Ambiente": float(row["Humedad_Ambiente"]),
                        "Medicamentos_Vendidos": float(row["Medicamentos_Vendidos"]),
                    }
                )
    filas.sort(key=lambda r: r["mes"])
    return filas


def exportar_muestra_csv(filas: list[dict]) -> None:
    """Guarda la muestra exacta utilizada en matematicas/muestra_tolima_dengue_2019.csv."""
    roles = {
        1: "Regresion + Nodo L0",
        2: "Regresion",
        3: "Regresion + Nodo L1",
        4: "Regresion",
        5: "Regresion + Validacion Lagrange",
        6: "Regresion + Nodo L2",
        7: "Validacion Extrapolacion Regresion",
    }
    campos = [
        "Departamento",
        "ANO",
        "mes",
        "COD_EVE",
        "Nombre_evento",
        "Casos_Reportados",
        "Temperatura_Promedio",
        "Lluvias_Acumuladas",
        "Humedad_Ambiente",
        "Medicamentos_Vendidos",
        "Rol_Muestra",
    ]
    with SAMPLE_CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for r in filas:
            out = dict(r)
            out["Casos_Reportados"] = int(r["Casos_Reportados"])
            out["Medicamentos_Vendidos"] = int(r["Medicamentos_Vendidos"])
            out["Rol_Muestra"] = roles.get(r["mes"], "")
            writer.writerow(out)


def regresion_lineal(xs: list[float], ys: list[float]) -> dict:
    """Implementación desde cero de regresión lineal por mínimos cuadrados."""
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    xm = sx / n
    ym = sy / n

    num = n * sxy - sx * sy
    den = n * sxx - sx * sx
    a1 = num / den
    a0 = ym - a1 * xm

    tabla = []
    st = 0.0
    sr = 0.0
    for i, (x, y) in enumerate(zip(xs, ys), start=1):
        yh = a0 + a1 * x
        e = y - yh
        e2 = e * e
        dy2 = (y - ym) ** 2
        sr += e2
        st += dy2
        tabla.append(
            {
                "i": i,
                "x": x,
                "y": y,
                "x2": x * x,
                "xy": x * y,
                "y_hat": yh,
                "e": e,
                "e2": e2,
                "dy2": dy2,
            }
        )

    r2 = (st - sr) / st
    r = math.sqrt(r2) if a1 >= 0 else -math.sqrt(r2)
    syx = math.sqrt(sr / (n - 2))

    return {
        "n": n,
        "sx": sx,
        "sy": sy,
        "sxx": sxx,
        "sxy": sxy,
        "xm": xm,
        "ym": ym,
        "numerador_a1": num,
        "denominador_a1": den,
        "a0": a0,
        "a1": a1,
        "St": st,
        "Sr": sr,
        "R2": r2,
        "r": r,
        "Syx": syx,
        "tabla": tabla,
    }


def lagrange_base(xs: list[float], i: int, x: float) -> float:
    """Evalúa el polinomio base de Lagrange L_i(x)."""
    val = 1.0
    for j, xj in enumerate(xs):
        if j != i:
            val *= (x - xj) / (xs[i] - xj)
    return val


def lagrange_eval(xs: list[float], ys: list[float], x: float) -> float:
    """Evalúa el polinomio interpolante de Lagrange P_n(x)."""
    return sum(ys[i] * lagrange_base(xs, i, x) for i in range(len(xs)))


def lagrange_cuadratico_expandido(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """Retorna coeficientes (c2, c1, c0) de P2(x) = c2*x^2 + c1*x + c0 para 3 nodos."""
    c2 = c1 = c0 = 0.0
    for i in range(3):
        j1, j2 = (i + 1) % 3, (i + 2) % 3
        den = (xs[i] - xs[j1]) * (xs[i] - xs[j2])
        c2 += ys[i] / den
        c1 += ys[i] * (-(xs[j1] + xs[j2])) / den
        c0 += ys[i] * (xs[j1] * xs[j2]) / den
    return c2, c1, c0


def main() -> None:
    filas = cargar_muestra_tolima_2019()
    exportar_muestra_csv(filas)

    # 1. Regresión lineal: meses 1..6 (x = Casos_Reportados, y = Medicamentos_Vendidos)
    sem1 = [r for r in filas if r["mes"] <= 6]
    mes7 = next(r for r in filas if r["mes"] == 7)

    xs_reg = [r["Casos_Reportados"] for r in sem1]
    ys_reg = [r["Medicamentos_Vendidos"] for r in sem1]
    reg = regresion_lineal(xs_reg, ys_reg)

    pred_1000 = reg["a0"] + reg["a1"] * 1000.0
    pred_mes7 = reg["a0"] + reg["a1"] * mes7["Casos_Reportados"]
    err_abs_m7 = abs(mes7["Medicamentos_Vendidos"] - pred_mes7)
    err_rel_m7 = err_abs_m7 / mes7["Medicamentos_Vendidos"] * 100.0

    # 2. Interpolación de Lagrange: nodos meses 1, 3, 6 -> validar en mes 5
    por_mes = {r["mes"]: r for r in sem1}
    xs_lag = [1.0, 3.0, 6.0]
    ys_lag = [por_mes[1]["Casos_Reportados"], por_mes[3]["Casos_Reportados"], por_mes[6]["Casos_Reportados"]]
    x_eval = 5.0
    y_real_m5 = por_mes[5]["Casos_Reportados"]

    pesos_m5 = [lagrange_base(xs_lag, i, x_eval) for i in range(3)]
    p2_m5 = lagrange_eval(xs_lag, ys_lag, x_eval)
    c2, c1, c0 = lagrange_cuadratico_expandido(xs_lag, ys_lag)
    err_abs_m5 = abs(y_real_m5 - p2_m5)
    err_rel_m5 = err_abs_m5 / y_real_m5 * 100.0

    # Verificación opcional con NumPy / SciPy si están disponibles
    verificacion_libs: dict[str, object] = {}
    try:
        import numpy as np  # type: ignore

        a1_np, a0_np = np.polyfit(xs_reg, ys_reg, 1)
        verificacion_libs["numpy_polyfit"] = {
            "a1": float(a1_np),
            "a0": float(a0_np),
            "diff_a1": abs(float(a1_np) - reg["a1"]),
            "diff_a0": abs(float(a0_np) - reg["a0"]),
        }
    except ImportError:
        verificacion_libs["numpy_polyfit"] = "No instalado (cálculo verificado en Python puro)"

    try:
        from scipy.interpolate import lagrange as scipy_lagrange  # type: ignore

        poly = scipy_lagrange(xs_lag, ys_lag)
        verificacion_libs["scipy_lagrange"] = {
            "P2_en_5": float(poly(x_eval)),
            "diff_P2_en_5": abs(float(poly(x_eval)) - p2_m5),
        }
    except ImportError:
        verificacion_libs["scipy_lagrange"] = "No instalado (cálculo verificado en Python puro)"

    resultados = {
        "muestra": "TOLIMA · DENGUE · 2019 (Meses 1 a 6 + Mes 7 validación)",
        "regresion_lineal": {
            **reg,
            "prediccion_1000_casos": pred_1000,
            "extrapolacion_mes7": {
                "x_casos_julio": mes7["Casos_Reportados"],
                "y_real_julio": mes7["Medicamentos_Vendidos"],
                "y_hat_julio": pred_mes7,
                "error_absoluto": err_abs_m7,
                "error_relativo_pct": err_rel_m7,
            },
        },
        "interpolacion_lagrange": {
            "nodos_x_mes": xs_lag,
            "nodos_y_casos": ys_lag,
            "denominadores": [10, -6, 15],
            "polinomio_expandido": {"c2": c2, "c1": c1, "c0": c0},
            "evaluacion_mes5": {
                "x": x_eval,
                "L0": pesos_m5[0],
                "L1": pesos_m5[1],
                "L2": pesos_m5[2],
                "suma_L": sum(pesos_m5),
                "P2_5": p2_m5,
                "real_mes5": y_real_m5,
                "error_absoluto": err_abs_m5,
                "error_relativo_pct": err_rel_m5,
            },
        },
        "verificacion_librerias": verificacion_libs,
    }

    RESULTS_JSON_PATH.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")

    # Reporte en consola
    print("=" * 72)
    print("APLICACIÓN DE MÉTODOS NUMÉRICOS · PROYECTO DENGUE TOLIMA 2019")
    print("=" * 72)
    print("\n[1] REGRESIÓN LINEAL POR MÍNIMOS CUADRADOS (Meses 1..6)")
    print(f"  n = {reg['n']} | Σx = {reg['sx']:.0f} | Σy = {reg['sy']:.0f}")
    print(f"  Σx² = {reg['sxx']:.0f} | Σxy = {reg['sxy']:.0f}")
    print(f"  x̄ = {reg['xm']:.4f} | ȳ = {reg['ym']:.4f}")
    print(f"  a1 = {reg['a1']:.6f} medicamentos/caso | a0 = {reg['a0']:.4f} medicamentos")
    print(f"  Modelo: ŷ = {reg['a0']:.2f} + {reg['a1']:.4f}·x")
    print(f"  St = {reg['St']:.2f} | Sr = {reg['Sr']:.2f}")
    print(f"  R² = {reg['R2']:.4f} ({reg['R2']*100:.2f}%) | r = {reg['r']:.4f} | Sy/x = {reg['Syx']:.2f}")
    print(f"  Interpolación (x=1000 casos): ŷ(1000) = {pred_1000:.2f} unidades")
    print(
        f"  Extrapolación mes 7 (x=1667): ŷ(1667) = {pred_mes7:.2f} vs Real = {mes7['Medicamentos_Vendidos']:.0f} "
        f"(Error = {err_rel_m7:.2f}%)"
    )

    print("\n[2] INTERPOLACIÓN POLINOMIAL DE LAGRANGE (Nodos: meses 1, 3, 6)")
    print(f"  Nodos: (1, {ys_lag[0]:.0f}), (3, {ys_lag[1]:.0f}), (6, {ys_lag[2]:.0f})")
    print(f"  Polinomio expandido: P2(x) = {c2:.4f}x² + {c1:.4f}x + {c0:.4f}")
    print(
        f"  Pesos en x=5: L0(5)={pesos_m5[0]:.4f}, L1(5)={pesos_m5[1]:.4f}, "
        f"L2(5)={pesos_m5[2]:.4f} (ΣL = {sum(pesos_m5):.4f})"
    )
    print(
        f"  P2(5) = {p2_m5:.2f} casos vs Real mayo = {y_real_m5:.0f} casos "
        f"(Error abs = {err_abs_m5:.2f}, Error rel = {err_rel_m5:.2f}%)"
    )
    print(f"\nArchivos exportados:\n  - {SAMPLE_CSV_PATH}\n  - {RESULTS_JSON_PATH}")


if __name__ == "__main__":
    main()
