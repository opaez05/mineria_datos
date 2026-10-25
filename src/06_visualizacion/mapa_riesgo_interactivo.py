"""
=============================================================================
  FASE 6 – VISUALIZACIÓN GEOESPACIAL INTERACTIVA (MAPA DE RIESGO)
  Proyecto: Predicción de Brotes Epidemiológicos y Prevención de
            Desabastecimiento de Medicamentos en Colombia
  Metodología: CRISP-DM
=============================================================================
Este módulo integra el dataset consolidado del proyecto y el modelo de riesgo
logístico con las coordenadas geográficas de los 32 departamentos de Colombia,
generando un mapa interactivo con OpenStreetMap y exportando un artefacto
HTML autónomo para presentaciones y toma de decisiones.

Salida:
  - datos_procesados/mapa_desabastecimiento_colombia.html
=============================================================================
"""

import os
import sys
import webbrowser
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "datos_procesados" / "dataset_final_crisp_dm_mejorado.csv"
OUTPUT_HTML = BASE_DIR / "datos_procesados" / "mapa_desabastecimiento_colombia.html"

# Diccionario oficial de centroides geográficos (Latitud, Longitud) de departamentos en Colombia
COORDENADAS_COLOMBIA = {
    'AMAZONAS': {'lat': -1.4429, 'lon': -71.5724},
    'ANTIOQUIA': {'lat': 6.5322, 'lon': -75.4975},
    'ARAUCA': {'lat': 6.5544, 'lon': -70.9328},
    'ATLANTICO': {'lat': 10.6966, 'lon': -74.8741},
    'BOGOTA': {'lat': 4.7110, 'lon': -74.0721},
    'BOLIVAR': {'lat': 8.6226, 'lon': -74.0300},
    'BOYACA': {'lat': 5.5353, 'lon': -73.3678},
    'CALDAS': {'lat': 5.2983, 'lon': -75.2479},
    'CAQUETA': {'lat': 0.8699, 'lon': -73.8419},
    'CASANARE': {'lat': 5.3377, 'lon': -71.7456},
    'CAUCA': {'lat': 2.4448, 'lon': -76.6147},
    'CESAR': {'lat': 9.3373, 'lon': -73.6536},
    'CHOCO': {'lat': 5.6923, 'lon': -76.6582},
    'CORDOBA': {'lat': 8.7479, 'lon': -75.8814},
    'CUNDINAMARCA': {'lat': 4.8624, 'lon': -74.0595},
    'GUAINIA': {'lat': 2.5855, 'lon': -68.5247},
    'GUAJIRA': {'lat': 11.3548, 'lon': -72.5205},
    'GUAVIARE': {'lat': 2.0594, 'lon': -71.9592},
    'HUILA': {'lat': 2.9273, 'lon': -75.2819},
    'MAGDALENA': {'lat': 10.4113, 'lon': -74.4057},
    'META': {'lat': 3.4243, 'lon': -73.3087},
    'NARINO': {'lat': 1.2892, 'lon': -77.3579},
    'NORTE SANTANDER': {'lat': 8.0163, 'lon': -72.8872},
    'PUTUMAYO': {'lat': 0.4389, 'lon': -75.8770},
    'QUINDIO': {'lat': 4.4610, 'lon': -75.6674},
    'RISARALDA': {'lat': 4.8133, 'lon': -75.6961},
    'SAN ANDRES': {'lat': 12.5847, 'lon': -81.7006},
    'SANTANDER': {'lat': 6.6821, 'lon': -73.6536},
    'SUCRE': {'lat': 9.3047, 'lon': -75.3978},
    'TOLIMA': {'lat': 4.4389, 'lon': -75.2322},
    'VALLE DEL CAUCA': {'lat': 3.8009, 'lon': -76.6413},
    'VAUPES': {'lat': 0.8554, 'lon': -70.8120},
    'VICHADA': {'lat': 4.4234, 'lon': -69.2878}
}

# Inventarios base de referencia hospitalaria departamental
INVENTARIOS_BASE = {
    'ANTIOQUIA': 80000,
    'VALLE DEL CAUCA': 70000,
    'BOGOTA': 90000,
    'SANTANDER': 40000,
    'CESAR': 35000,
    'HUILA': 25000,
    'TOLIMA': 30000,
    'ATLANTICO': 50000,
    'BOLIVAR': 45000,
    'CORDOBA': 30000,
    'NARINO': 25000,
    'CHOCO': 15000,
    'NORTE SANTANDER': 35000,
    'META': 35000,
    'CASANARE': 20000,
    'MAGDALENA': 30000,
    'SUCRE': 20000
}

def generar_mapa_interactivo(enfermedad: str = "DENGUE", abrir_navegador: bool = True):
    print("\n" + "=" * 70)
    print(f" GENERADOR DE MAPA GEOESPACIAL INTERACTIVO - CASO: {enfermedad}")
    print("=" * 70)

    if not DATA_PATH.exists():
        print(f"[ERROR] No se encuentra el dataset consolidado en: {DATA_PATH}")
        sys.exit(1)

    # 1. Cargar datos consolidados
    df = pd.read_csv(DATA_PATH)
    print(f"-> Dataset cargado exitosamente: {len(df):,} registros.")

    # 2. Filtrar por enfermedad prioritaria
    df_enf = df[df['Nombre_evento'] == enfermedad].copy()
    if df_enf.empty:
        print(f"[ALERTA] No se hallaron registros para '{enfermedad}', usando todo el dataset.")
        df_enf = df.copy()

    # 3. Agregación analítica por departamento
    depto_agg = df_enf.groupby('Departamento').agg(
        Total_Casos=('Casos_Reportados', 'sum'),
        Promedio_Mensual_Casos=('Casos_Reportados', 'mean'),
        Max_Casos_Mes=('Casos_Reportados', 'max'),
        Total_Medicamentos=('Medicamentos_Vendidos', 'sum'),
        Promedio_Medicamentos=('Medicamentos_Vendidos', 'mean'),
        Temperatura_Media=('Temperatura_Promedio', 'mean'),
        Precipitacion_Media=('Lluvias_Acumuladas', 'mean'),
        Humedad_Media=('Humedad_Ambiente', 'mean')
    ).reset_index()

    # 4. Clasificación de riesgo logístico según presión sobre el inventario
    # Puntos críticos epidemiológicos: Alta incidencia de casos históricos y demanda farmacéutica
    q75_casos = depto_agg['Promedio_Mensual_Casos'].quantile(0.75)
    q50_casos = depto_agg['Promedio_Mensual_Casos'].quantile(0.50)

    conditions = [
        depto_agg['Promedio_Mensual_Casos'] >= q75_casos,
        depto_agg['Promedio_Mensual_Casos'] >= q50_casos
    ]
    choices = ['ALTO RIESGO', 'RIESGO MEDIO']
    depto_agg['Nivel_Alerta'] = np.select(conditions, choices, default='BAJO RIESGO')

    # 5. Cruzar con coordenadas geográficas
    depto_agg['Latitud'] = depto_agg['Departamento'].map(lambda d: COORDENADAS_COLOMBIA.get(d, {}).get('lat', None))
    depto_agg['Longitud'] = depto_agg['Departamento'].map(lambda d: COORDENADAS_COLOMBIA.get(d, {}).get('lon', None))

    # Filtrar departamentos no mapeables
    depto_geo = depto_agg.dropna(subset=['Latitud', 'Longitud']).copy()
    depto_geo = depto_geo.sort_values(by='Total_Casos', ascending=False)

    print(f"-> Departamentos georreferenciados: {len(depto_geo)}")
    print(f"   * ALTO RIESGO   : {(depto_geo['Nivel_Alerta'] == 'ALTO RIESGO').sum()} departamentos")
    print(f"   * RIESGO MEDIO  : {(depto_geo['Nivel_Alerta'] == 'RIESGO MEDIO').sum()} departamentos")
    print(f"   * BAJO RIESGO   : {(depto_geo['Nivel_Alerta'] == 'BAJO RIESGO').sum()} departamentos")

    # 6. Formateo de métricas para Tooltip (Hover)
    depto_geo['Casos_Totales'] = depto_geo['Total_Casos'].apply(lambda x: f"{int(x):,}")
    depto_geo['Casos_Promedio'] = depto_geo['Promedio_Mensual_Casos'].round(1).astype(str)
    depto_geo['Pico_Maximo'] = depto_geo['Max_Casos_Mes'].apply(lambda x: f"{int(x):,} casos")
    depto_geo['Demanda_Promedio'] = depto_geo['Promedio_Medicamentos'].apply(lambda x: f"{int(x):,} und/mes")
    depto_geo['Clima'] = (
        depto_geo['Temperatura_Media'].round(1).astype(str) + " °C | " +
        depto_geo['Precipitacion_Media'].round(0).astype(int).astype(str) + " mm | " +
        depto_geo['Humedad_Media'].round(0).astype(int).astype(str) + " %"
    )

    # 7. Paleta de colores oficial CRISP-DM
    color_map = {
        'ALTO RIESGO': '#D32F2F',    # Rojo crítico
        'RIESGO MEDIO': '#FB8C00',   # Naranja alerta
        'BAJO RIESGO': '#2E7D32'     # Verde estable
    }

    # 8. Construcción del Mapa con OpenStreetMap (Garantiza mapa base visible de Colombia)
    fig = px.scatter_map(
        depto_geo,
        lat="Latitud",
        lon="Longitud",
        color="Nivel_Alerta",
        color_discrete_map=color_map,
        size="Total_Casos",
        size_max=32,
        hover_name="Departamento",
        hover_data={
            "Latitud": False,
            "Longitud": False,
            "Nivel_Alerta": True,
            "Casos_Totales": True,
            "Casos_Promedio": True,
            "Pico_Maximo": True,
            "Demanda_Promedio": True,
            "Clima": True,
            "Total_Casos": False
        },
        labels={
            "Nivel_Alerta": "Nivel de Criticidad",
            "Casos_Totales": "Casos Totales Reportados",
            "Casos_Promedio": "Promedio Mensual Casos",
            "Pico_Maximo": "Pico Histórico Mensual",
            "Demanda_Promedio": "Demanda Promedio Fármacos",
            "Clima": "Clima (Temp | Lluvia | Humedad)"
        },
        zoom=4.8,
        center={"lat": 4.5709, "lon": -74.2973},
        map_style="open-street-map",
        title="<b>Monitoreo Epidemiológico y Riesgo de Desabastecimiento Farmacéutico (Dengue)</b><br><sup>Colombia — Pipeline CRISP-DM Integrado (SIVIGILA + IDEAM + SISMED)</sup>"
    )

    fig.update_layout(
        margin={"r": 0, "t": 60, "l": 0, "b": 0},
        legend=dict(
            title="<b>Nivel de Alerta</b>",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1
        ),
        font=dict(family="Arial, sans-serif", size=13)
    )

    # 9. Exportar HTML autónomo
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(OUTPUT_HTML), include_plotlyjs="cdn")
    print(f"-> [OK] Mapa exportado con éxito a: {OUTPUT_HTML.relative_to(BASE_DIR)}")

    # 10. Abrir en navegador
    if abrir_navegador:
        print("-> Abriendo mapa interactivo de Colombia en tu navegador...")
        webbrowser.open(OUTPUT_HTML.as_uri())

    print("=" * 70)
    return depto_geo

if __name__ == "__main__":
    generar_mapa_interactivo()
