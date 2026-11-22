# GEO-EPIDEMIA 3D: Plataforma de Visualización Geoespacial y Simulación Predictiva (2017 - 2027)

> **Proyecto:** Minería de Datos — Examen Final  
> **Tema:** Predicción de Brotes Epidemiológicos y Prevención de Desabastecimiento Farmacéutico en Colombia  
> **Metodología:** CRISP-DM + Machine Learning Supervisado / No Supervisado

---

## 🌟 Características de la Plataforma 3D

1. **Motor Gráfico de Alta Densidad (Deck.gl + MapLibre GL)**:
   - **Columnas Extruidas 3D (`ColumnLayer`)**: Representan el volumen de casos y el nivel de criticidad departamental.
   - **Arcos Parabólicos 3D (`ArcLayer`)**: Rutas dinámicas de despacho logístico urgente de medicamentos desde los hubs centrales (Bogotá, Medellín, Cali, Barranquilla) hacia los departamentos en déficit.
   - **Etiquetas Holográficas Flotantes (`TextLayer`)**: Información en vivo anclada a la cúspide de las columnas 3D.

2. **Línea de Tiempo Interactiva (Timeline Play/Pause)**:
   - Recorre mes a mes desde **2017 hasta 2027**.
   - Distingue claramente entre el **Histórico Real (2017-2024)** y las **Proyecciones de Inteligencia Artificial (2025-2027)** generadas con los modelos predictivos.
   - Controles multimedia: Play, Pause, Siguiente, Anterior, y selector de velocidad (1x, 2x, 4x).

3. **Modo Cinematográfico y Simulador Climático 3D (What-If)**:
   - **Pincel Climático 3D (🌧️ Nube / ☀️ Sol)**: Suelta una nube de tormenta o una ola de calor sobre cualquier departamento para ver partículas de lluvia 3D o rayos solares animados, onda de contagio hacia departamentos vecinos (40% de impacto), y recálculo en vivo de casos y arcos logísticos según las correlaciones reales de Pearson (`r`) extraídas del dataset CRISP-DM.
   - **Rotación IA (`Orbit`)**: Giro suave de 360 grados sobre el territorio nacional para proyectar en auditorio.
   - **Pitch 3D**: Alterna entre perspectiva isométrica tridimensional (52°) y plano cenital 2D (0°).

4. **Inspector Departamental en Tiempo Real**:
   - Muestra casos, demanda estimada, déficit/tensión farmacéutica y variables meteorológicas (Temperatura, Lluvias, Humedad).

---

## 🚀 Cómo Ejecutar la Aplicación

### Opción 1: Con el Lanzador Automático (Recomendado)
Haz doble clic en el archivo:
```
iniciar_mapa.bat
```

### Opción 2: Abrir Directamente en el Navegador
Abre el archivo:
```
index.html
```
en Google Chrome, Microsoft Edge o cualquier navegador moderno.

---

## 📁 Estructura de la Carpeta

```
mapa_3d_interactivo/
│
├── index.html                  # Interfaz principal HUD Glassmorphism Dark Mode
├── styles.css                  # Estilos tipo Command Center / Cyberpunk
├── app.js                      # Controlador WebGL 3D Deck.gl + MapLibre
├── iniciar_mapa.bat            # Acceso directo para el examen final
├── preparar_datos_3d.py        # Pipeline de extracción y proyecciones 2017-2027
│
└── data/
    ├── timeline_colombia_3d.json  # Base de datos optimizada en JSON
    └── timeline_colombia_3d.js    # Envoltura JS para ejecución local sin bloqueos CORS
```

