import pandas as pd
import plotly.express as px

# 1. Datos de ejemplo
datos = {
    'Ciudad_Departamento': ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Ibagué'],
    'Latitud': [4.7110, 6.2442, 3.4516, 10.9685, 4.4389],
    'Longitud': [-74.0721, -75.5812, -76.5320, -74.7813, -75.2322],
    'Nivel_Desabastecimiento': [85, 40, 65, 30, 90], 
    'Epidemia_Principal': ['Dengue', 'IRA', 'Dengue', 'Zika', 'Dengue']
}

df = pd.DataFrame(datos)

# 2. Crear el mapa interactivo (Corregido para Plotly 6+)
fig = px.scatter_map(
    df,
    lat="Latitud",
    lon="Longitud",
    color="Epidemia_Principal",       
    size="Nivel_Desabastecimiento",   
    hover_name="Ciudad_Departamento", 
    hover_data=["Nivel_Desabastecimiento"], 
    zoom=4.5,                         
    center={"lat": 4.5709, "lon": -74.2973}, 
    map_style="carto-positron",       # ¡Aquí también cambia a map_style!
    title="Zonas de Desabastecimiento de Medicamentos en Colombia",
    size_max=30                       
)

fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig.show()