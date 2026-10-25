"""
=============================================================================
  ORQUESTADOR MAESTRO DE PIPELINE ANALÍTICO (CRISP-DM)
  Proyecto: Predicción de Brotes Epidemiológicos y Prevención de
            Desabastecimiento de Medicamentos en Colombia
=============================================================================
Este orquestador unifica todas las fases del ciclo de vida del proyecto
garantizando la trazabilidad estricta del paso a paso, la reproducibilidad y
la ejecución controlada por fases o end-to-end.

Uso:
  python main.py --help
  python main.py --all                      # Ejecuta el pipeline completo de principio a fin
  python main.py --fase ingesta             # Fase 1: Auditoría y calidad de datos crudos
  python main.py --fase etl                 # Fase 2: Limpieza, integración y simulación climática
  python main.py --fase eda                 # Fase 3: Análisis Exploratorio de Datos (Sesión 5)
  python main.py --fase escalamiento        # Fase 4: Escalamiento (StandardScaler + RobustScaler)
  python main.py --fase modelado            # Fase 5: Entrenamiento RandomForest y alertas de riesgo
  python main.py --fase prediccion          # Fase 6: Inferencia de escenarios futuros (2027)
=============================================================================
"""

import sys
import os
import argparse
import time
import subprocess
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent

# Catálogo oficial de fases del pipeline (Organizadas modularmente en src/)
FASES = {
    "ingesta": {
        "numero": "Fase 1",
        "nombre": "Comprensión Inicial & Auditoría de Fuentes Crudas",
        "scripts": ["src/01_ingesta/analisis_inicial.py", "src/01_ingesta/obtener_sismed_filtrado.py"],
        "descripcion": "Inspección de volúmenes, formatos y nulos en SIVIGILA, IDEAM y SISMED."
    },
    "etl": {
        "numero": "Fase 2",
        "nombre": "Preparación e Integración de Datos (ETL)",
        "scripts": ["src/02_preparacion/preparacion_datos_mejorado.py"],
        "descripcion": "Limpieza, normalización temporal ISO y simulación climática por departamento."
    },
    "eda": {
        "numero": "Fase 3",
        "nombre": "Análisis Exploratorio de Datos (EDA - Sesión 5)",
        "scripts": ["src/03_eda/eda_proyecto.py"],
        "descripcion": "Cálculo de 3 familias de medidas, regla IQR de outliers y 7 figuras analíticas."
    },
    "escalamiento": {
        "numero": "Fase 4",
        "nombre": "Transformación & Escalamiento de Características",
        "scripts": ["src/04_transformacion/escalamiento.py"],
        "descripcion": "Estandarización y escalado robusto para variables asimétricas (Standard + Robust)."
    },
    "modelado": {
        "numero": "Fase 5",
        "nombre": "Modelado Predictivo & Evaluación de Riesgo Hospitalario",
        "scripts": ["src/05_modelado/probar_modelo_desabastecimiento.py"],
        "descripcion": "Entrenamiento de RandomForest y estimación de presión sobre el inventario."
    },
    "prediccion": {
        "numero": "Fase 6",
        "nombre": "Inferencia de Escenarios Futuros (2027)",
        "scripts": ["src/05_modelado/prediccion_futura_2027.py"],
        "descripcion": "Simulación estacional y pronóstico de desabastecimiento para el año 2027."
    },
    "mapa": {
        "numero": "Fase 7",
        "nombre": "Visualización Geoespacial Interactiva (Mapa de Riesgo)",
        "scripts": ["src/06_visualizacion/mapa_riesgo_interactivo.py"],
        "descripcion": "Georreferenciación de los 32 departamentos y mapa interactivo OpenStreetMap."
    }
}

ORDEN_FASES = ["ingesta", "etl", "eda", "escalamiento", "modelado", "prediccion", "mapa"]

def imprimir_banner():
    print("""
=============================================================================
       SISTEMA INTELIGENTE DE PREDICCIÓN EPIDEMIOLÓGICA Y DESABASTECIMIENTO
               ORQUESTADOR MAESTRO DEL PIPELINE (CRISP-DM)
=============================================================================
""")

def ejecutar_script(script_nombre: str) -> bool:
    ruta_script = BASE_DIR / script_nombre
    if not ruta_script.exists():
        print(f"  [ERROR] No se encuentra el script: {script_nombre}")
        return False

    print(f"\n  >>> Ejecutando módulo: {script_nombre} ...")
    inicio = time.time()
    
    # Ejecuta en el mismo intérprete de python activo
    resultado = subprocess.run([sys.executable, str(ruta_script)], cwd=str(BASE_DIR))
    duracion = time.time() - inicio

    if resultado.returncode == 0:
        print(f"  [OK] {script_nombre} completado en {duracion:.2f}s")
        return True
    else:
        print(f"  [FALLO] Fallo {script_nombre} (Codigo de salida: {resultado.returncode})")
        return False

def ejecutar_fase(clave_fase: str) -> bool:
    info = FASES.get(clave_fase)
    if not info:
        print(f"[ERROR] Fase desconocida: '{clave_fase}'. Opciones válidas: {list(FASES.keys())}")
        return False

    print("\n" + "=" * 75)
    print(f"  {info['numero']}: {info['nombre'].upper()}")
    print(f"  Propósito: {info['descripcion']}")
    print("=" * 75)

    for script in info["scripts"]:
        exito = ejecutar_script(script)
        if not exito:
            print(f"\n[INTERRUPCIÓN] El pipeline se detuvo por error en: {script}")
            return False
    return True

def ejecutar_pipeline_completo():
    imprimir_banner()
    print("Iniciando ejecución End-to-End del pipeline analítico...\n")
    inicio_total = time.time()
    fases_exitosas = 0

    for clave in ORDEN_FASES:
        exito = ejecutar_fase(clave)
        if not exito:
            print(f"\n[PIPELINE ABORTADO] Falló la ejecución en la fase: {clave}")
            sys.exit(1)
        fases_exitosas += 1

    duracion_total = time.time() - inicio_total
    print("\n" + "=" * 75)
    print("             PIPELINE ANALÍTICO COMPLETADO EXITOSAMENTE")
    print("=" * 75)
    print(f"Total fases ejecutadas : {fases_exitosas} de {len(ORDEN_FASES)}")
    print(f"Tiempo total ejecución : {duracion_total:.2f} segundos")
    print(f"Artefactos generados   : Carpeta 'datos_procesados/'")
    print(f"Documentación y Guías  : Carpeta 'docs/' y 'Reporte_EDA_Sesion5.md'")
    print("=" * 75)

def main():
    parser = argparse.ArgumentParser(
        description="Orquestador Maestro del Pipeline de Minería de Datos (CRISP-DM)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ejecuta todas las fases del pipeline en orden secuencial (End-to-End)"
    )
    parser.add_argument(
        "--fase",
        choices=ORDEN_FASES,
        help="""Ejecuta una fase específica del pipeline:
  ingesta      : Auditoría inicial de fuentes crudas
  etl          : Preparación, limpieza e integración (SIVIGILA + IDEAM + SISMED)
  eda          : Análisis Exploratorio de Datos (Sesión 5)
  escalamiento : Normalización StandardScaler y RobustScaler
  modelado     : Modelo RandomForest y alertas de desabastecimiento
  prediccion   : Inferencia predictiva de escenarios futuros (2027)
  mapa         : Visualización Geoespacial Interactiva (OpenStreetMap)"""
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Muestra el estado actual del linaje de datos y artefactos generados"
    )

    args = parser.parse_args()

    if args.status:
        imprimir_banner()
        print("ESTADO ACTUAL DE ARTEFACTOS Y LINEAJE DE DATOS:\n")
        dp = BASE_DIR / "datos_procesados"
        archivos_clave = [
            ("Dataset Consolidado (Silver)", dp / "dataset_final_crisp_dm_mejorado.csv"),
            ("Dataset Escalado (Gold)", dp / "dataset_escalado_standard_robust.csv"),
            ("Figuras EDA (Sesión 5)", dp / "fig5_heatmap_correlaciones.png"),
            ("Gráfica Modelo Riesgo", dp / "grafica_riesgo_desabastecimiento.png"),
            ("Pronóstico Futuro 2027", dp / "pronostico_demanda_2027.png"),
            ("Mapa Interactivo Colombia", dp / "mapa_desabastecimiento_colombia.html"),
        ]
        for nombre, ruta in archivos_clave:
            estado = "[OK]" if ruta.exists() else "[PENDIENTE]"
            tamano = f"({ruta.stat().st_size / 1024:.1f} KB)" if ruta.exists() else ""
            print(f"  {nombre:32} : {estado} {tamano}")
        print("\nPara ejecutar una fase: python main.py --fase <nombre_fase>")
        print("Para ejecutar todo    : python main.py --all")
        return

    if args.all:
        ejecutar_pipeline_completo()
    elif args.fase:
        imprimir_banner()
        exito = ejecutar_fase(args.fase)
        if exito:
            print(f"\n[OK FASE COMPLETADA] La fase '{args.fase}' finalizo con exito.")
        else:
            sys.exit(1)
    else:
        imprimir_banner()
        parser.print_help()

if __name__ == "__main__":
    main()
