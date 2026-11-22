"""
=============================================================================
  PROCESADOR Y EXTRACTOR DE DATOS 3D (2017 - 2027)
  Proyecto: Minería de Datos - Riesgo Epidemiológico y Logístico
  Genera el archivo JSON optimizado para Deck.gl / MapLibre GL
=============================================================================
"""

import csv
import json
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "datos_procesados" / "dataset_final_crisp_dm_mejorado.csv"
OUTPUT_JSON = BASE_DIR / "mapa_3d_interactivo" / "data" / "timeline_colombia_3d.json"
OUTPUT_JS = BASE_DIR / "mapa_3d_interactivo" / "data" / "timeline_colombia_3d.js"

def pearson_corr(xs, ys):
    """Calcula correlación de Pearson r entre dos listas numéricas."""
    n = len(xs)
    if n < 3:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = sum((x - mx) ** 2 for x in xs)
    den_y = sum((y - my) ** 2 for y in ys)
    den = math.sqrt(den_x * den_y)
    return round(num / den, 3) if den > 0 else 0.0

# Coordenadas precisas de capitales / centroides departamentales
COORDENADAS_COLOMBIA = {
    'AMAZONAS': {'lat': -1.4429, 'lon': -71.5724, 'capital': 'Leticia'},
    'ANTIOQUIA': {'lat': 6.2442, 'lon': -75.5812, 'capital': 'Medellín'},
    'ARAUCA': {'lat': 7.0847, 'lon': -70.7591, 'capital': 'Arauca'},
    'ATLANTICO': {'lat': 10.9685, 'lon': -74.7813, 'capital': 'Barranquilla'},
    'BOGOTA': {'lat': 4.7110, 'lon': -74.0721, 'capital': 'Bogotá D.C.'},
    'BOLIVAR': {'lat': 10.3997, 'lon': -75.5144, 'capital': 'Cartagena'},
    'BOYACA': {'lat': 5.5353, 'lon': -73.3678, 'capital': 'Tunja'},
    'CALDAS': {'lat': 5.0689, 'lon': -75.5174, 'capital': 'Manizales'},
    'CAQUETA': {'lat': 1.6144, 'lon': -75.6062, 'capital': 'Florencia'},
    'CASANARE': {'lat': 5.3377, 'lon': -72.3959, 'capital': 'Yopal'},
    'CAUCA': {'lat': 2.4448, 'lon': -76.6147, 'capital': 'Popayán'},
    'CESAR': {'lat': 10.4631, 'lon': -73.2532, 'capital': 'Valledupar'},
    'CHOCO': {'lat': 5.6923, 'lon': -76.6582, 'capital': 'Quibdó'},
    'CORDOBA': {'lat': 8.7479, 'lon': -75.8814, 'capital': 'Montería'},
    'CUNDINAMARCA': {'lat': 4.8624, 'lon': -74.0595, 'capital': 'Soacha/Chía'},
    'GUAINIA': {'lat': 3.8653, 'lon': -67.9239, 'capital': 'Inírida'},
    'GUAJIRA': {'lat': 11.5444, 'lon': -72.9072, 'capital': 'Riohacha'},
    'GUAVIARE': {'lat': 2.5729, 'lon': -72.6459, 'capital': 'San José del Guaviare'},
    'HUILA': {'lat': 2.9273, 'lon': -75.2819, 'capital': 'Neiva'},
    'MAGDALENA': {'lat': 11.2408, 'lon': -74.1990, 'capital': 'Santa Marta'},
    'META': {'lat': 4.1420, 'lon': -73.6266, 'capital': 'Villavicencio'},
    'NARINO': {'lat': 1.2136, 'lon': -77.2811, 'capital': 'Pasto'},
    'NORTE SANTANDER': {'lat': 7.8939, 'lon': -72.5078, 'capital': 'Cúcuta'},
    'PUTUMAYO': {'lat': 1.1492, 'lon': -76.6467, 'capital': 'Mocoa'},
    'QUINDIO': {'lat': 4.5339, 'lon': -75.6811, 'capital': 'Armenia'},
    'RISARALDA': {'lat': 4.8133, 'lon': -75.6961, 'capital': 'Pereira'},
    'SAN ANDRES': {'lat': 12.5847, 'lon': -81.7006, 'capital': 'San Andrés'},
    'SANTANDER': {'lat': 7.1254, 'lon': -73.1198, 'capital': 'Bucaramanga'},
    'SUCRE': {'lat': 9.3047, 'lon': -75.3978, 'capital': 'Sincelejo'},
    'TOLIMA': {'lat': 4.4389, 'lon': -75.2322, 'capital': 'Ibagué'},
    'VALLE DEL CAUCA': {'lat': 3.4516, 'lon': -76.5320, 'capital': 'Cali'},
    'VAUPES': {'lat': 1.2514, 'lon': -70.2337, 'capital': 'Mitú'},
    'VICHADA': {'lat': 6.1884, 'lon': -67.4859, 'capital': 'Puerto Carreño'}
}

# Centros logísticos de distribución nacional farmacéutica
CENTROS_DISTRIBUCION = {
    'BOGOTA': {'lat': 4.7110, 'lon': -74.0721, 'nombre': 'Centro de Distribución Central (Bogotá)'},
    'ANTIOQUIA': {'lat': 6.2442, 'lon': -75.5812, 'nombre': 'Hub Logístico Occidente (Medellín)'},
    'VALLE DEL CAUCA': {'lat': 3.4516, 'lon': -76.5320, 'nombre': 'Hub Logístico Suroccidente (Cali)'},
    'ATLANTICO': {'lat': 10.9685, 'lon': -74.7813, 'nombre': 'Hub Logístico Costa Caribe (Barranquilla)'}
}

def procesar():
    print(f"Leyendo CSV desde: {CSV_PATH}")
    if not CSV_PATH.exists():
        print("ERROR: Archivo no encontrado.")
        return

    # Estructura de almacenamiento por: enfermedad -> anio-mes -> depto -> datos
    # También por evento "TODOS"
    datos_agrupados = {}
    raw_series = {}
    eventos_set = set()
    anios_set = set()

    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            depto = row['Departamento'].strip().upper()
            if depto not in COORDENADAS_COLOMBIA:
                continue

            try:
                ano = int(row['ANO'])
                mes = int(row['mes'])
                evento = row['Nombre_evento'].strip().upper()
                casos = float(row['Casos_Reportados']) if row['Casos_Reportados'] else 0.0
                temp = float(row['Temperatura_Promedio']) if row['Temperatura_Promedio'] else 24.0
                lluvia = float(row['Lluvias_Acumuladas']) if row['Lluvias_Acumuladas'] else 100.0
                humedad = float(row['Humedad_Ambiente']) if row['Humedad_Ambiente'] else 75.0
                meds = float(row['Medicamentos_Vendidos']) if row['Medicamentos_Vendidos'] else 5000.0
            except (ValueError, KeyError):
                continue

            eventos_set.add(evento)
            anios_set.add(ano)
            periodo = f"{ano}-{mes:02d}"

            for ev in [evento, "CONSOLIDADO_GENERAL"]:
                if ev not in raw_series:
                    raw_series[ev] = {'t': [], 'l': [], 'h': [], 'c': []}
                raw_series[ev]['t'].append(temp)
                raw_series[ev]['l'].append(lluvia)
                raw_series[ev]['h'].append(humedad)
                raw_series[ev]['c'].append(casos)

                if ev not in datos_agrupados:
                    datos_agrupados[ev] = {}
                if periodo not in datos_agrupados[ev]:
                    datos_agrupados[ev][periodo] = {}
                if depto not in datos_agrupados[ev][periodo]:
                    datos_agrupados[ev][periodo][depto] = {
                        'casos': 0.0,
                        'meds': 0.0,
                        'temp_sum': 0.0,
                        'lluvia_sum': 0.0,
                        'hum_sum': 0.0,
                        'count': 0
                    }
                
                d = datos_agrupados[ev][periodo][depto]
                d['casos'] += casos
                d['meds'] += meds
                d['temp_sum'] += temp
                d['lluvia_sum'] += lluvia
                d['hum_sum'] += humedad
                d['count'] += 1

    print(f"Años históricos detectados: {sorted(list(anios_set))}")
    print(f"Total eventos encontrados: {len(eventos_set)}")

    # Proyecciones predictivas 2025 - 2027 (Basadas en estacionalidad climática + crecimiento epidemiológico del modelo)
    # Generamos los meses 2025-01 hasta 2027-12
    max_ano = max(anios_set)
    anios_proyeccion = [2025, 2026, 2027]
    eventos_top = [
        "DENGUE",
        "DENGUE GRAVE",
        "MALARIA",
        "MALARIA ASOCIADA (FORMAS MIXTAS)",
        "MALARIA COMPLICADA",
        "INFECCION RESPIRATORIA AGUDA GRAVE IRAG INUSITADA",
        "MORTALIDAD POR EDA 0-4 AÑOS",
        "CHIKUNGUNYA",
        "ZIKA",
        "ACCIDENTE OFIDICO",
        "CONSOLIDADO_GENERAL"
    ]
    # Agregar el resto de eventos presentes ordenados alfabéticamente
    for ev in sorted(eventos_set):
        if ev not in eventos_top:
            eventos_top.append(ev)

    for ev in eventos_top:
        if ev not in datos_agrupados:
            continue
        
        # Calcular estacionalidad base por mes para cada departamento
        patrones_mes = {} # depto -> mes -> {casos_avg, meds_avg, temp_avg, lluvia_avg, hum_avg}
        for depto in COORDENADAS_COLOMBIA:
            patrones_mes[depto] = {}
            for m in range(1, 13):
                casos_lista = []
                meds_lista = []
                temp_lista = []
                lluvia_lista = []
                hum_lista = []
                for ano in anios_set:
                    per = f"{ano}-{m:02d}"
                    if per in datos_agrupados[ev] and depto in datos_agrupados[ev][per]:
                        rec = datos_agrupados[ev][per][depto]
                        casos_lista.append(rec['casos'])
                        meds_lista.append(rec['meds'])
                        cnt = max(1, rec['count'])
                        temp_lista.append(rec['temp_sum'] / cnt)
                        lluvia_lista.append(rec['lluvia_sum'] / cnt)
                        hum_lista.append(rec['hum_sum'] / cnt)
                
                c_avg = sum(casos_lista) / len(casos_lista) if casos_lista else 10.0
                m_avg = sum(meds_lista) / len(meds_lista) if meds_lista else 2000.0
                t_avg = sum(temp_lista) / len(temp_lista) if temp_lista else 25.0
                l_avg = sum(lluvia_lista) / len(lluvia_lista) if lluvia_lista else 120.0
                h_avg = sum(hum_lista) / len(hum_lista) if hum_lista else 78.0

                patrones_mes[depto][m] = {
                    'casos': c_avg, 'meds': m_avg, 'temp': t_avg, 'lluvia': l_avg, 'hum': h_avg
                }

        # Generar años proyectados con incremento de variabilidad y tendencia de cambio climático
        for p_ano in anios_proyeccion:
            factor_ano = 1.0 + (p_ano - max_ano) * 0.052 # Crecimiento según modelo
            for m in range(1, 13):
                per = f"{p_ano}-{m:02d}"
                datos_agrupados[ev][per] = {}
                # Factor estacional fenómeno del niño/niña oscilatorio
                factor_clima = 1.0 + 0.18 * math.sin((p_ano * 12 + m) * 0.5)
                for depto in COORDENADAS_COLOMBIA:
                    base = patrones_mes[depto][m]
                    casos_proj = base['casos'] * factor_ano * factor_clima
                    meds_proj = base['meds'] * (1.0 + (p_ano - max_ano) * 0.03) # Oferta farmacéutica crece más lento que la demanda
                    t_proj = base['temp'] + (p_ano - max_ano) * 0.15 # Calentamiento progresivo
                    l_proj = base['lluvia'] * (1.0 + 0.1 * math.sin(m))
                    h_proj = min(98.0, base['hum'] + 1.2)

                    datos_agrupados[ev][per][depto] = {
                        'casos': round(casos_proj, 1),
                        'meds': round(meds_proj, 0),
                        'temp_sum': t_proj,
                        'lluvia_sum': l_proj,
                        'hum_sum': h_proj,
                        'count': 1,
                        'es_proyeccion': True
                    }

    # Ahora convertimos a la estructura final para el Frontend
    timeline_records = []
    # Obtener todos los periodos cronológicos ordenados
    todos_periodos = sorted(list(datos_agrupados["CONSOLIDADO_GENERAL"].keys()))

    print(f"Total periodos temporales (Mes a Mes): {len(todos_periodos)} ({todos_periodos[0]} a {todos_periodos[-1]})")

    # Calcular correlaciones reales de Pearson (Temperatura, Lluvias, Humedad -> Casos)
    eventos_seleccionados = []
    for ev in eventos_top:
        if ev in datos_agrupados and ev not in eventos_seleccionados:
            eventos_seleccionados.append(ev)
        if len(eventos_seleccionados) >= 15:
            break

    correlaciones_clima = {}
    for ev in eventos_seleccionados:
        ser = raw_series.get(ev, {'t': [], 'l': [], 'h': [], 'c': []})
        correlaciones_clima[ev] = {
            'r_temp': pearson_corr(ser['t'], ser['c']),
            'r_lluvia': pearson_corr(ser['l'], ser['c']),
            'r_hum': pearson_corr(ser['h'], ser['c']),
            'n': len(ser['c'])
        }
        print(f"  [CORR] {ev}: Temp={correlaciones_clima[ev]['r_temp']:+.3f}, Lluvia={correlaciones_clima[ev]['r_lluvia']:+.3f}, Hum={correlaciones_clima[ev]['r_hum']:+.3f}")

    # Lista final filtrable
    salida_estructurada = {
        'metadata': {
            'periodos': todos_periodos,
            'inicio_proyeccion': f"{anios_proyeccion[0]}-01",
            'coordenadas': COORDENADAS_COLOMBIA,
            'centros_distribucion': CENTROS_DISTRIBUCION,
            'eventos_disponibles': sorted(eventos_seleccionados),
            'correlaciones_clima': correlaciones_clima
        },
        'timeline': {}
    }

    for ev in salida_estructurada['metadata']['eventos_disponibles']:
        if ev not in datos_agrupados:
            continue
        salida_estructurada['timeline'][ev] = {}

        for per in todos_periodos:
            if per not in datos_agrupados[ev]:
                continue
            
            deptos_list = []
            arcos_list = []

            for depto, coord in COORDENADAS_COLOMBIA.items():
                rec = datos_agrupados[ev][per].get(depto, None)
                if not rec:
                    casos = 0
                    meds = 1000
                    temp = 25.0
                    lluvia = 100.0
                    hum = 75.0
                    es_proj = per >= f"{anios_proyeccion[0]}-01"
                else:
                    cnt = max(1, rec['count'])
                    casos = rec['casos']
                    meds = rec['meds']
                    temp = round(rec['temp_sum'] / cnt, 1)
                    lluvia = round(rec['lluvia_sum'] / cnt, 1)
                    hum = round(rec['hum_sum'] / cnt, 1)
                    es_proj = rec.get('es_proyeccion', per >= f"{anios_proyeccion[0]}-01")

                # Ratio de presión sobre el inventario y riesgo de desabastecimiento
                # Relación demanda estimada por caso vs medicamentos disponibles
                demanda_estimada = casos * 4.5
                ratio_presion = demanda_estimada / max(1.0, meds)
                
                # Clasificación de criticidad
                if ratio_presion >= 1.2 or (casos > 350 and ratio_presion >= 0.8):
                    alerta = "CRÍTICO"
                    color = [239, 68, 68, 220]     # Rojo neon
                    altura_factor = 2.5
                elif ratio_presion >= 0.6 or casos > 150:
                    alerta = "ALERTA"
                    color = [245, 158, 11, 200]    # Naranja advertencia
                    altura_factor = 1.6
                else:
                    alerta = "ESTABLE"
                    color = [16, 185, 129, 180]    # Verde esmeralda
                    altura_factor = 0.8

                # Altura extruida 3D (en metros para el motor de Deck.gl)
                elevacion_3d = min(120000.0, max(1500.0, casos * 350.0 * altura_factor))

                item_depto = {
                    'depto': depto,
                    'capital': coord['capital'],
                    'lat': coord['lat'],
                    'lon': coord['lon'],
                    'casos': int(round(casos)),
                    'meds': int(round(meds)),
                    'demanda_est': int(round(demanda_estimada)),
                    'ratio_presion': round(ratio_presion * 100, 1),
                    'temp': temp,
                    'lluvia': lluvia,
                    'hum': hum,
                    'alerta': alerta,
                    'color': color,
                    'elevacion': elevacion_3d,
                    'es_proyeccion': es_proj
                }
                deptos_list.append(item_depto)

                # Si está en alerta o crítico, generar un arco 3D de despacho de emergencia desde el centro más cercano
                if alerta in ["CRÍTICO", "ALERTA"]:
                    # Buscar el centro de distribución con menor distancia euclídea
                    mejor_centro = 'BOGOTA'
                    min_dist = 999.0
                    for c_key, c_val in CENTROS_DISTRIBUCION.items():
                        dist = math.hypot(coord['lat'] - c_val['lat'], coord['lon'] - c_val['lon'])
                        if dist < min_dist:
                            min_dist = dist
                            mejor_centro = c_key

                    c_source = CENTROS_DISTRIBUCION[mejor_centro]
                    arcos_list.append({
                        'origen': mejor_centro,
                        'origen_nombre': c_source['nombre'],
                        'origen_coords': [c_source['lon'], c_source['lat']],
                        'destino': depto,
                        'destino_coords': [coord['lon'], coord['lat']],
                        'criticidad': alerta,
                        'volumen_despacho': int(demanda_estimada * 0.75),
                        'color_arco': [255, 75, 75, 230] if alerta == "CRÍTICO" else [255, 180, 0, 180]
                    })

            salida_estructurada['timeline'][ev][per] = {
                'deptos': deptos_list,
                'arcos': arcos_list,
                'totales': {
                    'casos': sum(d['casos'] for d in deptos_list),
                    'meds': sum(d['meds'] for d in deptos_list),
                    'criticos': sum(1 for d in deptos_list if d['alerta'] == 'CRÍTICO'),
                    'alertas': sum(1 for d in deptos_list if d['alerta'] == 'ALERTA'),
                    'estables': sum(1 for d in deptos_list if d['alerta'] == 'ESTABLE')
                }
            }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    json_str = json.dumps(salida_estructurada, ensure_ascii=False)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as out_f:
        out_f.write(json_str)

    with open(OUTPUT_JS, 'w', encoding='utf-8') as out_js:
        out_js.write("window.DATASET_3D_COLOMBIA = " + json_str + ";")

    size_mb = OUTPUT_JSON.stat().st_size / (1024 * 1024)
    print(f"¡EXITO! Dataset 3D exportado a: {OUTPUT_JSON} ({size_mb:.2f} MB) y {OUTPUT_JS.name}")

if __name__ == '__main__':
    procesar()

