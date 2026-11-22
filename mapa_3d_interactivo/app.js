/**
 * ============================================================================
 * CONTROLADOR PRINCIPAL — GEO-EPIDEMIA 3D COLOMBIA (EDICIÓN SUSTENTACIÓN PRO)
 * Motor: Deck.gl v8.9 + MapLibre GL + GeoJSON 3D + Simulador Climático What-If
 *        + Tour Guiado + Pulsos Logísticos + Sparkline 2017-2027 + Explicabilidad IA
 * ============================================================================
 */

(function () {
    const isMobileViewport = () => window.innerWidth <= 960;

    // Parámetros de Cámara inicial centrada en Colombia
    function getInitialViewState() {
        return {
            longitude: -73.8,
            latitude: 4.8,
            zoom: isMobileViewport() ? 4.75 : 5.55,
            minZoom: 4.2,
            maxZoom: 12,
            pitch: 52,
            bearing: -15
        };
    }

    // 1. Estado Global
    const state = {
        dataset: null,
        geojsonColombia: null,
        periodos: [],
        eventoActual: 'DENGUE',
        indicePeriodo: 0,
        isPlaying: false,
        playInterval: null,
        velocidad: 1200,
        pitch3D: true,
        autoRotate: false,
        mostrarPoligonos: true,
        mostrarArcos: true,
        deptoSeleccionado: null,
        viewState: getInitialViewState(),
        escenaActiva: null,
        macroActivo: null, // 'nino' | 'nina' | null
        zenMode: false,

        // Estado del Simulador Climático 3D (Nube / Sol)
        herramientaClima: 'cursor', // 'cursor' | 'nube' | 'sol'
        intensidadClima: 2,         // 1 | 2 | 3
        focosClimaticos: [],        // [{ depto, lat, lon, tipo, intensidad }]
        frameSimuladoActual: null,
        capasDatosBase: [],

        // Loop unificado de animación 3D (pulsos arcos, radares críticos, clima, rotación)
        animTick: 0,
        animId: null,
        lastAnimRender: 0
    };

    // Radio de onda de contagio climático (~2.65 grados ≈ ~290 km)
    const RADIO_CONTAGIO_GRADOS = 2.65;

    // Semillas determinísticas para partículas de lluvia / rayos solares
    const PARTICULAS_LLUVIA = Array.from({ length: 28 }, (_, i) => ({
        dx: Math.cos(i * 2.39996) * (0.18 + (i % 7) * 0.14),
        dy: Math.sin(i * 2.39996) * (0.18 + (i % 5) * 0.15),
        offset: (i * 0.137) % 1
    }));

    const RAYOS_SOL = Array.from({ length: 12 }, (_, i) => ({
        angle: (i / 12) * Math.PI * 2,
        offset: (i * 0.19) % 1
    }));

    // Mapeo canónico de nombres GeoJSON -> Dataset
    const MAPEO_NOMBRES_GEOJSON = {
        'ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA': 'SAN ANDRES',
        'SANTAFE DE BOGOTA D.C': 'BOGOTA',
        'LA GUAJIRA': 'GUAJIRA',
        'NARIÑO': 'NARINO',
        'NORTE DE SANTANDER': 'NORTE SANTANDER'
    };

    // Escenas del Tour Guiado Cinematográfico ("Modo Jurado")
    const ESCENAS_TOUR = {
        brote2019: {
            tag: 'ESCENA 1 · EVIDENCIA HISTÓRICA',
            titulo: 'Brote Crítico de Dengue · Tolima y Meta (Julio 2019)',
            desc: 'Pico epidémico real SIVIGILA usado en nuestra validación matemática (r = 0.949). Observa la presión crítica sobre stock y los despachos urgentes desde Bogotá.',
            evento: 'DENGUE',
            periodo: '2019-07',
            macro: null,
            rotate: false,
            focusDepto: 'TOLIMA',
            camera: { longitude: -74.75, latitude: 4.35, zoom: 6.85, pitch: 58, bearing: -24 }
        },
        proyeccion2027: {
            tag: 'ESCENA 2 · PROYECCIÓN MACHINE LEARNING',
            titulo: 'Escenario Predictivo Nacional 2027 (Random Forest + Estacionalidad)',
            desc: 'Proyección hacia 2027 bajo tendencia de calentamiento progresivo: la demanda hospitalaria crece más rápido que la oferta farmacéutica en regiones periféricas.',
            evento: 'DENGUE',
            periodo: '2027-06',
            macro: null,
            rotate: true,
            focusDepto: null,
            camera: { longitude: -73.8, latitude: 4.8, zoom: 5.55, pitch: 55, bearing: 16 }
        },
        elnino: {
            tag: 'ESCENA 3 · SIMULADOR WHAT-IF EN VIVO',
            titulo: 'Crisis Climática: Fenómeno del Niño (+Calor Extremo 3x)',
            desc: 'Simulación en tiempo real usando correlaciones reales de Pearson (IDEAM/NASA): la ola de calor dispara focos epidémicos y activa nuevos puentes logísticos.',
            evento: 'DENGUE',
            periodo: '2026-04',
            macro: 'nino',
            rotate: false,
            focusDepto: 'META',
            camera: { longitude: -74.4, latitude: 6.1, zoom: 5.75, pitch: 54, bearing: -10 }
        },
        logistica: {
            tag: 'ESCENA 4 · RED LOGÍSTICA NACIONAL',
            titulo: 'Despacho Farmacéutico desde 4 Hubs Estratégicos (SISMED)',
            desc: 'Vista consolidada de todas las patologías: pulsos 3D muestran el flujo de reabastecimiento urgente desde Bogotá, Medellín, Cali y Barranquilla hacia zonas críticas.',
            evento: 'CONSOLIDADO_GENERAL',
            periodo: '2027-05',
            macro: null,
            rotate: true,
            focusDepto: null,
            camera: { longitude: -74.1, latitude: 5.3, zoom: 5.45, pitch: 48, bearing: 8 }
        }
    };

    function normalizarNombre(nombre) {
        if (!nombre) return '';
        const limpio = nombre.trim().toUpperCase();
        return MAPEO_NOMBRES_GEOJSON[limpio] || limpio;
    }

    let deckOverlay = null;
    let mapInstance = null;

    // 2. Inicialización
    window.addEventListener('DOMContentLoaded', () => {
        if (window.lucide) lucide.createIcons();

        if (window.GEOJSON_COLOMBIA) {
            state.geojsonColombia = window.GEOJSON_COLOMBIA;
        }

        if (window.DATASET_3D_COLOMBIA) {
            state.dataset = window.DATASET_3D_COLOMBIA;
            inicializarApp();
        } else {
            const statusEl = document.getElementById('loading-status');
            if (statusEl) {
                statusEl.textContent = 'Error: No se cargó timeline_colombia_3d.js. Ejecuta preparar_datos_3d.py.';
            }
            console.error('No se encontró el objeto global DATASET_3D_COLOMBIA.');
        }
    });

    function ocultarLoader() {
        const loader = document.getElementById('loading-overlay');
        if (loader) {
            setTimeout(() => loader.classList.add('hidden'), 350);
        }
    }

    function inicializarApp() {
        state.periodos = state.dataset.metadata.periodos;

        // En proyectores de baja altura (<= 820px) iniciar leyenda colapsada para liberar espacio
        if (window.innerHeight <= 820) {
            const legendPanel = document.getElementById('legend-panel');
            if (legendPanel) legendPanel.classList.add('collapsed');
        }

        // Poblar Select de Patologías
        const selectEvento = document.getElementById('select-evento');
        selectEvento.innerHTML = '';
        state.dataset.metadata.eventos_disponibles.forEach(ev => {
            const opt = document.createElement('option');
            opt.value = ev;
            opt.textContent = ev.replace(/_/g, ' ');
            if (ev === 'DENGUE') opt.selected = true;
            selectEvento.appendChild(opt);
        });

        // Poblar Salto Rápido de Departamentos
        const selectJump = document.getElementById('select-depto-jump');
        const deptosOrdenados = Object.keys(state.dataset.metadata.coordenadas || {}).sort();
        deptosOrdenados.forEach(dep => {
            const opt = document.createElement('option');
            opt.value = dep;
            opt.textContent = dep;
            selectJump.appendChild(opt);
        });

        // Configurar Slider
        const slider = document.getElementById('timeline-slider');
        slider.min = 0;
        slider.max = state.periodos.length - 1;
        slider.value = 0;

        // Inicializar Mapa MapLibre Base (Esri Dark Gray Canvas)
        mapInstance = new maplibregl.Map({
            container: 'map-container',
            style: {
                version: 8,
                sources: {
                    'esri-dark-base': {
                        type: 'raster',
                        tiles: [
                            'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'
                        ],
                        tileSize: 256,
                        attribution: '&copy; Esri, HERE, Garmin, OpenStreetMap'
                    },
                    'esri-dark-ref': {
                        type: 'raster',
                        tiles: [
                            'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}'
                        ],
                        tileSize: 256
                    }
                },
                layers: [
                    {
                        id: 'esri-dark-base-layer',
                        type: 'raster',
                        source: 'esri-dark-base',
                        minzoom: 0,
                        maxzoom: 16
                    },
                    {
                        id: 'esri-dark-ref-layer',
                        type: 'raster',
                        source: 'esri-dark-ref',
                        minzoom: 0,
                        maxzoom: 16
                    }
                ]
            },
            center: [state.viewState.longitude, state.viewState.latitude],
            zoom: state.viewState.zoom,
            pitch: state.viewState.pitch,
            bearing: state.viewState.bearing,
            interactive: false
        });

        // Iluminación 3D escultórica sutil (realza relieve de columnas y departamentos)
        const deckEffects = [];
        if (deck.LightingEffect && deck.AmbientLight && deck.DirectionalLight) {
            const ambientLight = new deck.AmbientLight({
                color: [220, 235, 255],
                intensity: 1.45
            });
            const dirLight1 = new deck.DirectionalLight({
                color: [255, 250, 240],
                intensity: 1.8,
                direction: [-1, -2, -3]
            });
            const dirLight2 = new deck.DirectionalLight({
                color: [90, 190, 255],
                intensity: 0.9,
                direction: [2, 1, -2]
            });
            deckEffects.push(new deck.LightingEffect({ ambientLight, dirLight1, dirLight2 }));
        }

        // Inicializar Deck.gl con cámara controlada (map: false evita instancia mapbox duplicada)
        deckOverlay = new deck.DeckGL({
            container: 'map-container',
            map: false,
            viewState: state.viewState,
            effects: deckEffects,
            controller: true,
            onViewStateChange: ({ viewState, interactionState }) => {
                // Si el usuario arrastra manualmente, pausar auto-rotación para no pelear con el mouse
                if (interactionState && interactionState.isDragging && state.autoRotate) {
                    setAutoRotate(false);
                }
                state.viewState = viewState;
                deckOverlay.setProps({ viewState: state.viewState });
                if (mapInstance) {
                    mapInstance.jumpTo({
                        center: [viewState.longitude, viewState.latitude],
                        zoom: viewState.zoom,
                        bearing: viewState.bearing,
                        pitch: viewState.pitch
                    });
                }
            },
            getTooltip: renderTooltip,
            layers: []
        });

        configurarEventosUI();
        configurarAtajosTeclado();
        actualizarBadgeCorrelacion();
        actualizarVista();
        iniciarLoopAnimacion();
        ocultarLoader();
    }

    // Vuelo cinematográfico controlado con FlyToInterpolator
    function volarA(target, duration = 1150) {
        const nextView = {
            ...state.viewState,
            ...target,
            transitionDuration: duration,
            transitionInterpolator: new deck.FlyToInterpolator()
        };
        state.viewState = nextView;
        if (deckOverlay) {
            deckOverlay.setProps({ viewState: state.viewState });
        }
    }

    function enfocarDepartamento(deptoObj, abrirInspector = true) {
        if (!deptoObj) return;
        setAutoRotate(false);
        volarA({
            longitude: deptoObj.lon,
            latitude: deptoObj.lat,
            zoom: isMobileViewport() ? 6.2 : 7.15,
            pitch: state.pitch3D ? 58 : 0,
            bearing: -18
        }, 1100);

        if (abrirInspector) {
            if (isMobileViewport()) cerrarDrawersMoviles();
            mostrarInspector(deptoObj);
        }
    }

    // 3. Motor Científico del Simulador Climático (Correlaciones reales CRISP-DM)
    function obtenerCorrelacionEvento(evento) {
        const dicc = state.dataset.metadata.correlaciones_clima || {};
        return dicc[evento] || { r_temp: 0.15, r_lluvia: -0.10, r_hum: -0.10, n: 0 };
    }

    function clasificarCriticidad(casos, meds) {
        const demandaEstimada = Math.round(casos * 4.5);
        const ratioPresion = demandaEstimada / Math.max(1.0, meds);

        let alerta = 'ESTABLE';
        let color = [16, 185, 129, 185];
        let alturaFactor = 0.8;

        if (ratioPresion >= 1.2 || (casos > 350 && ratioPresion >= 0.8)) {
            alerta = 'CRÍTICO';
            color = [239, 68, 68, 225];
            alturaFactor = 2.5;
        } else if (ratioPresion >= 0.6 || casos > 150) {
            alerta = 'ALERTA';
            color = [245, 158, 11, 205];
            alturaFactor = 1.6;
        }

        const elevacion = Math.min(125000.0, Math.max(1500.0, casos * 350.0 * alturaFactor));
        return { demandaEstimada, ratioPresion, alerta, color, elevacion };
    }

    function simularFrame(rawFrame, evento) {
        if (!state.focosClimaticos.length) {
            return {
                ...rawFrame,
                totales: {
                    ...rawFrame.totales,
                    casosBase: rawFrame.totales.casos,
                    deltaCasos: 0
                }
            };
        }

        const corr = obtenerCorrelacionEvento(evento);
        const centros = state.dataset.metadata.centros_distribucion || {};
        const deptosSim = [];
        const arcosSim = [];
        let casosBaseTotal = 0;

        rawFrame.deptos.forEach(d => {
            casosBaseTotal += d.casos;

            let dTemp = 0;
            let dLluvia = 0;
            let dHum = 0;
            let esEpicentro = false;
            let afectado = false;

            state.focosClimaticos.forEach(foco => {
                let peso = 0;
                if (foco.depto === d.depto) {
                    peso = 1.0;
                    esEpicentro = true;
                } else {
                    const dist = Math.hypot(d.lat - foco.lat, d.lon - foco.lon);
                    if (dist <= RADIO_CONTAGIO_GRADOS) {
                        peso = 0.4;
                    }
                }

                if (peso > 0) {
                    afectado = true;
                    const I = foco.intensidad;
                    if (foco.tipo === 'nube') {
                        dLluvia += 180 * I * peso;
                        dHum += 12 * I * peso;
                        dTemp -= 2.2 * I * peso;
                    } else if (foco.tipo === 'sol') {
                        dTemp += 3.5 * I * peso;
                        dLluvia -= 65 * I * peso;
                        dHum -= 14 * I * peso;
                    }
                }
            });

            if (!afectado) {
                deptosSim.push({
                    ...d,
                    casosBase: d.casos,
                    deltaCasos: 0,
                    pctCambio: 0,
                    afectadoPorSim: false,
                    esEpicentro: false
                });
                return;
            }

            const nuevaTemp = Math.round(Math.max(5.0, Math.min(42.0, d.temp + dTemp)) * 10) / 10;
            const nuevaLluvia = Math.round(Math.max(5.0, d.lluvia + dLluvia) * 10) / 10;
            const nuevaHum = Math.round(Math.max(25.0, Math.min(99.0, d.hum + dHum)) * 10) / 10;

            const realDTemp = nuevaTemp - d.temp;
            const realDLluvia = nuevaLluvia - d.lluvia;
            const realDHum = nuevaHum - d.hum;

            const zTemp = realDTemp / 4.5;
            const zLluvia = realDLluvia / 140.0;
            const zHum = realDHum / 14.0;

            const score = (corr.r_temp * zTemp) + (corr.r_lluvia * zLluvia) + (corr.r_hum * zHum);
            const fuerzaBase = Math.abs(corr.r_temp) + Math.abs(corr.r_lluvia) + Math.abs(corr.r_hum);
            const multiplicadorEscala = fuerzaBase < 0.25 ? 2.4 : 1.45;
            const factorCasos = Math.max(0.25, Math.min(3.8, 1.0 + score * multiplicadorEscala));

            const nuevosCasos = Math.max(0, Math.round(d.casos * factorCasos));
            const deltaCasos = nuevosCasos - d.casos;
            const pctCambio = d.casos > 0 ? Math.round((deltaCasos / d.casos) * 100) : 0;

            const clasif = clasificarCriticidad(nuevosCasos, d.meds);

            deptosSim.push({
                ...d,
                casos: nuevosCasos,
                casosBase: d.casos,
                deltaCasos,
                pctCambio,
                temp: nuevaTemp,
                lluvia: nuevaLluvia,
                hum: nuevaHum,
                demanda_est: clasif.demandaEstimada,
                ratio_presion: Math.round(clasif.ratioPresion * 1000) / 10,
                alerta: clasif.alerta,
                color: clasif.color,
                elevacion: clasif.elevacion,
                afectadoPorSim: true,
                esEpicentro
            });
        });

        deptosSim.forEach(item => {
            if (item.alerta === 'CRÍTICO' || item.alerta === 'ALERTA') {
                let mejorCentro = 'BOGOTA';
                let minDist = 999.0;
                Object.entries(centros).forEach(([cKey, cVal]) => {
                    const dist = Math.hypot(item.lat - cVal.lat, item.lon - cVal.lon);
                    if (dist < minDist) {
                        minDist = dist;
                        mejorCentro = cKey;
                    }
                });
                const cSource = centros[mejorCentro];
                if (cSource) {
                    arcosSim.push({
                        origen: mejorCentro,
                        origen_nombre: cSource.nombre,
                        origen_coords: [cSource.lon, cSource.lat],
                        destino: item.depto,
                        destino_coords: [item.lon, item.lat],
                        criticidad: item.alerta,
                        volumen_despacho: Math.round(item.demanda_est * 0.75),
                        color_arco: item.alerta === 'CRÍTICO' ? [255, 75, 75, 230] : [255, 180, 0, 180]
                    });
                }
            }
        });

        const totalCasos = deptosSim.reduce((acc, item) => acc + item.casos, 0);
        return {
            deptos: deptosSim,
            arcos: arcosSim,
            totales: {
                casos: totalCasos,
                casosBase: casosBaseTotal,
                deltaCasos: totalCasos - casosBaseTotal,
                meds: deptosSim.reduce((acc, item) => acc + item.meds, 0),
                criticos: deptosSim.filter(item => item.alerta === 'CRÍTICO').length,
                alertas: deptosSim.filter(item => item.alerta === 'ALERTA').length,
                estables: deptosSim.filter(item => item.alerta === 'ESTABLE').length
            }
        };
    }

    // 4. Manejo de Clic en Departamento & Macro-Escenarios Climáticos
    function manejarClicDepartamento(deptoObj) {
        if (!deptoObj) return;

        if (state.herramientaClima === 'nube' || state.herramientaClima === 'sol') {
            state.macroActivo = null;
            actualizarBotonesMacro();
            aplicarFocoClimatico(deptoObj, state.herramientaClima, state.intensidadClima);
            const deptoAct = state.frameSimuladoActual?.deptos.find(d => d.depto === deptoObj.depto) || deptoObj;
            mostrarInspector(deptoAct);
        } else {
            if (isMobileViewport()) cerrarDrawersMoviles();
            mostrarInspector(deptoObj);
        }
    }

    function aplicarFocoClimatico(deptoObj, tipo, intensidad) {
        const idx = state.focosClimaticos.findIndex(f => f.depto === deptoObj.depto);
        const nuevoFoco = {
            depto: deptoObj.depto,
            lat: deptoObj.lat,
            lon: deptoObj.lon,
            tipo,
            intensidad
        };

        if (idx >= 0) {
            state.focosClimaticos[idx] = nuevoFoco;
        } else {
            state.focosClimaticos.push(nuevoFoco);
        }
        actualizarVista();
    }

    function activarMacroEscenario(tipoMacro) {
        if (state.macroActivo === tipoMacro) {
            limpiarTodosFocos();
            return;
        }

        const coords = state.dataset.metadata.coordenadas || {};
        const targetsNino = ['TOLIMA', 'META', 'ATLANTICO', 'CESAR', 'VALLE DEL CAUCA', 'ANTIOQUIA'];
        const targetsNina = ['CHOCO', 'ANTIOQUIA', 'CAUCA', 'NARINO', 'CAQUETA', 'AMAZONAS'];

        const lista = tipoMacro === 'nino' ? targetsNino : targetsNina;
        const tipoFoco = tipoMacro === 'nino' ? 'sol' : 'nube';

        state.macroActivo = tipoMacro;
        state.intensidadClima = 3;
        document.querySelectorAll('.btn-intensity').forEach(b => {
            b.classList.toggle('active', parseInt(b.dataset.level) === 3);
        });

        state.focosClimaticos = lista
            .filter(dep => coords[dep])
            .map(dep => ({
                depto: dep,
                lat: coords[dep].lat,
                lon: coords[dep].lon,
                tipo: tipoFoco,
                intensidad: 3
            }));

        actualizarBotonesMacro();
        actualizarVista();
    }

    function actualizarBotonesMacro() {
        const btnNino = document.getElementById('btn-macro-nino');
        const btnNina = document.getElementById('btn-macro-nina');
        if (btnNino) btnNino.classList.toggle('active', state.macroActivo === 'nino');
        if (btnNina) btnNina.classList.toggle('active', state.macroActivo === 'nina');
    }

    function quitarFocoDepartamento(nombreDepto) {
        state.focosClimaticos = state.focosClimaticos.filter(f => f.depto !== nombreDepto);
        if (!state.focosClimaticos.length) state.macroActivo = null;
        actualizarBotonesMacro();
        actualizarVista();
    }

    function limpiarTodosFocos() {
        state.focosClimaticos = [];
        state.macroActivo = null;
        actualizarBotonesMacro();
        actualizarVista();
    }

    // 5. Renderizado de Capas Deck.gl Base
    function construirCapasBase(dataFrame) {
        const deptoMap = new Map();
        dataFrame.deptos.forEach(d => deptoMap.set(d.depto, d));

        const capas = [];

        // CAPA 0: GeoJsonLayer 3D de Departamentos de Colombia
        if (state.mostrarPoligonos && state.geojsonColombia) {
            capas.push(new deck.GeoJsonLayer({
                id: 'colombia-geojson-3d',
                data: state.geojsonColombia,
                pickable: true,
                stroked: true,
                filled: true,
                extruded: true,
                wireframe: true,
                lineWidthMinPixels: 1.5,
                getLineColor: f => {
                    const deptoNombre = normalizarNombre(f.properties.NOMBRE_DPT);
                    const d = deptoMap.get(deptoNombre);
                    if (d && d.alerta === 'CRÍTICO') return [239, 68, 68, 255];
                    if (d && d.alerta === 'ALERTA') return [245, 158, 11, 230];
                    return [56, 189, 248, 165];
                },
                getFillColor: f => {
                    const deptoNombre = normalizarNombre(f.properties.NOMBRE_DPT);
                    const d = deptoMap.get(deptoNombre);
                    if (d) {
                        const alpha = d.afectadoPorSim ? 112 : 72;
                        return [d.color[0], d.color[1], d.color[2], alpha];
                    }
                    return [20, 35, 65, 50];
                },
                getElevation: f => {
                    const deptoNombre = normalizarNombre(f.properties.NOMBRE_DPT);
                    const d = deptoMap.get(deptoNombre);
                    return d ? Math.min(25000, d.casos * 35 + 2000) : 1000;
                },
                autoHighlight: true,
                highlightColor: [255, 255, 255, 115],
                onClick: info => {
                    if (info.object && info.object.properties) {
                        const deptoNombre = normalizarNombre(info.object.properties.NOMBRE_DPT);
                        const d = deptoMap.get(deptoNombre);
                        if (d) manejarClicDepartamento(d);
                    }
                },
                transitions: {
                    getElevation: { duration: 550, type: 'spring' },
                    getFillColor: { duration: 400 },
                    getLineColor: { duration: 400 }
                }
            }));
        }

        // CAPA 1: ColumnLayer 3D
        capas.push(new deck.ColumnLayer({
            id: 'column-layer-3d',
            data: dataFrame.deptos,
            diskResolution: 22,
            radius: 14500,
            extruded: true,
            pickable: true,
            elevationScale: 1,
            getPosition: d => [d.lon, d.lat],
            getFillColor: d => d.color,
            getElevation: d => d.elevacion,
            autoHighlight: true,
            highlightColor: [255, 255, 255, 125],
            material: {
                ambient: 0.65,
                diffuse: 0.82,
                shininess: 48,
                specularColor: [255, 255, 255]
            },
            onClick: info => {
                if (info.object) manejarClicDepartamento(info.object);
            },
            transitions: {
                getElevation: { duration: 500, type: 'spring' },
                getFillColor: { duration: 400 }
            }
        }));

        // CAPA 2: ArcLayer 3D Logístico + Hubs Farmacéuticos Nacionales
        if (state.mostrarArcos && dataFrame.arcos && dataFrame.arcos.length > 0) {
            capas.push(new deck.ArcLayer({
                id: 'arc-logistics-3d',
                data: dataFrame.arcos,
                pickable: true,
                getWidth: d => (d.criticidad === 'CRÍTICO' ? 3.5 : 2.0),
                getSourcePosition: d => d.origen_coords,
                getTargetPosition: d => d.destino_coords,
                getSourceColor: [56, 189, 248, 145],
                getTargetColor: d => d.color_arco,
                getHeight: 0.65,
                tilt: 12,
                autoHighlight: true
            }));

            const centrosArr = Object.entries(state.dataset.metadata.centros_distribucion || {}).map(([key, val]) => ({
                key,
                ...val
            }));

            capas.push(new deck.ScatterplotLayer({
                id: 'hubs-base-3d',
                data: centrosArr,
                pickable: false,
                stroked: true,
                filled: true,
                radiusUnits: 'meters',
                getPosition: d => [d.lon, d.lat, 4500],
                getRadius: 24000,
                getFillColor: [56, 189, 248, 90],
                getLineColor: [125, 211, 252, 240],
                getLineWidth: 3200
            }));
        }

        // CAPA 3: TextLayer Flotante 3D
        capas.push(new deck.TextLayer({
            id: 'text-labels-3d',
            data: dataFrame.deptos.filter(d => d.alerta === 'CRÍTICO' || d.casos > 180 || d.esEpicentro),
            getPosition: d => [d.lon, d.lat, d.elevacion + 7000],
            getText: d => {
                if (d.afectadoPorSim && d.deltaCasos !== 0) {
                    const signo = d.deltaCasos > 0 ? '+' : '';
                    return `${d.depto}\n(${d.casos.toLocaleString()} | ${signo}${d.pctCambio}%)`;
                }
                return `${d.depto}\n(${d.casos.toLocaleString()} casos)`;
            },
            getSize: 11.5,
            getColor: [255, 255, 255, 245],
            getTextAnchor: 'middle',
            getAlignmentBaseline: 'bottom',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 700,
            background: true,
            getBackgroundColor: [6, 10, 19, 215],
            backgroundPadding: [4, 2]
        }));

        return capas;
    }

    // 6. Capas Visuales 3D Animadas (Radares Críticos + Pulsos Logísticos + Clima 3D)
    function construirCapasAnimadas() {
        const df = state.frameSimuladoActual;
        if (!df) return [];

        const tick = state.animTick;
        const capasAnim = [];

        // A) Anillos Radar Pulsantes en Departamentos CRÍTICOS
        const deptosCriticos = df.deptos.filter(d => d.alerta === 'CRÍTICO');
        if (deptosCriticos.length > 0) {
            const wave = (tick * 0.38) % 1;
            const alpha = Math.round((1 - wave) * 215);
            capasAnim.push(new deck.ScatterplotLayer({
                id: 'critical-radars-3d',
                data: deptosCriticos,
                pickable: false,
                stroked: true,
                filled: false,
                radiusUnits: 'meters',
                getPosition: d => [d.lon, d.lat, 4000],
                getRadius: () => 22000 + wave * 68000,
                getLineColor: [239, 68, 68, alpha],
                getLineWidth: 3400,
                updateTriggers: {
                    getRadius: [tick],
                    getLineColor: [tick]
                }
            }));
        }

        // B) Pulsos Luminosos Viajando por los Arcos Logísticos 3D
        if (state.mostrarArcos && df.arcos && df.arcos.length > 0) {
            const pulsos = [];
            df.arcos.forEach((arc, idx) => {
                const [x0, y0] = arc.origen_coords;
                const [x1, y1] = arc.destino_coords;
                const distDeg = Math.hypot(x1 - x0, y1 - y0);
                if (distDeg < 0.15) return;

                const peakZ = Math.min(185000, Math.max(45000, distDeg * 38000));
                // 2 paquetes de energía viajando por cada arco
                for (let k = 0; k < 2; k++) {
                    const t = (tick * 0.28 + idx * 0.17 + k * 0.5) % 1;
                    const lon = x0 + (x1 - x0) * t;
                    const lat = y0 + (y1 - y0) * t;
                    const z = 4 * t * (1 - t) * peakZ + 6000;
                    pulsos.push({
                        pos: [lon, lat, z],
                        color: arc.criticidad === 'CRÍTICO' ? [255, 120, 120, 250] : [253, 224, 71, 240],
                        radius: arc.criticidad === 'CRÍTICO' ? 11500 : 8500
                    });
                }
            });

            if (pulsos.length > 0) {
                capasAnim.push(new deck.ScatterplotLayer({
                    id: 'arc-pulses-3d',
                    data: pulsos,
                    pickable: false,
                    billboard: true,
                    radiusUnits: 'meters',
                    getPosition: d => d.pos,
                    getRadius: d => d.radius,
                    getFillColor: d => d.color
                }));
            }
        }

        // C) Capas del Simulador Climático 3D (Nubes, Lluvia, Soles, Rayos, Ondas)
        if (state.focosClimaticos.length > 0) {
            const pulso = 0.5 + 0.5 * Math.sin(tick * 2.5);
            const radioOnda = (tick * 0.45) % 1;

            capasAnim.push(new deck.ScatterplotLayer({
                id: 'climate-wave-zones',
                data: state.focosClimaticos,
                pickable: false,
                stroked: true,
                filled: true,
                radiusUnits: 'meters',
                getPosition: d => [d.lon, d.lat, 3500],
                getRadius: 270000,
                getFillColor: d => d.tipo === 'nube' ? [56, 189, 248, 22] : [245, 158, 11, 22],
                getLineColor: d => d.tipo === 'nube' ? [56, 189, 248, 120 + pulso * 70] : [251, 191, 36, 120 + pulso * 70],
                getLineWidth: 3500,
                updateTriggers: { getLineColor: [tick] }
            }));

            capasAnim.push(new deck.ScatterplotLayer({
                id: 'climate-epicenter-pulse',
                data: state.focosClimaticos,
                pickable: false,
                stroked: true,
                filled: false,
                radiusUnits: 'meters',
                getPosition: d => [d.lon, d.lat, 5000],
                getRadius: () => 40000 + radioOnda * 210000,
                getLineColor: d => {
                    const alpha = Math.round((1 - radioOnda) * 230);
                    return d.tipo === 'nube' ? [56, 189, 248, alpha] : [251, 191, 36, alpha];
                },
                getLineWidth: 4500,
                updateTriggers: { getRadius: [tick], getLineColor: [tick] }
            }));

            const lineasLluvia = [];
            const lineasSol = [];
            const cuerposNube = [];
            const cuerposSol = [];

            state.focosClimaticos.forEach(foco => {
                const zCielo = 132000;
                const escala = 0.8 + foco.intensidad * 0.25;

                if (foco.tipo === 'nube') {
                    const puffs = [
                        { dx: 0, dy: 0, r: 64000 * escala, c: [148, 163, 184, 215] },
                        { dx: -0.45 * escala, dy: -0.1, r: 48000 * escala, c: [100, 116, 139, 210] },
                        { dx: 0.48 * escala, dy: 0.08, r: 50000 * escala, c: [100, 116, 139, 210] },
                        { dx: 0.1 * escala, dy: 0.25, r: 44000 * escala, c: [203, 213, 225, 220] }
                    ];
                    puffs.forEach(p => {
                        cuerposNube.push({
                            pos: [foco.lon + p.dx, foco.lat + p.dy, zCielo + Math.sin(tick) * 2000],
                            radius: p.r,
                            color: p.c
                        });
                    });

                    const numGotas = 10 + foco.intensidad * 6;
                    for (let i = 0; i < numGotas; i++) {
                        const p = PARTICULAS_LLUVIA[i % PARTICULAS_LLUVIA.length];
                        const fase = (tick * (0.9 + foco.intensidad * 0.25) + p.offset) % 1;
                        const zTop = zCielo * (1 - fase);
                        const zBottom = Math.max(0, zTop - 22000);
                        lineasLluvia.push({
                            source: [foco.lon + p.dx * escala, foco.lat + p.dy * escala, zTop],
                            target: [foco.lon + p.dx * escala + 0.05, foco.lat + p.dy * escala - 0.04, zBottom]
                        });
                    }
                } else {
                    cuerposSol.push({
                        pos: [foco.lon, foco.lat, zCielo],
                        radius: (72000 + pulso * 18000) * escala,
                        color: [245, 158, 11, 95]
                    });
                    cuerposSol.push({
                        pos: [foco.lon, foco.lat, zCielo + 1000],
                        radius: 44000 * escala,
                        color: [253, 224, 71, 240]
                    });

                    RAYOS_SOL.forEach((rayo, idx) => {
                        if (idx % (4 - foco.intensidad) !== 0 && foco.intensidad < 3) return;
                        const ang = rayo.angle + tick * 0.4;
                        const rDist = 0.85 * escala;
                        const wave = (tick * 0.6 + rayo.offset) % 1;
                        const zStart = zCielo - 10000;
                        const zEnd = zStart * (1 - wave * 0.85);
                        lineasSol.push({
                            source: [foco.lon + Math.cos(ang) * 0.15, foco.lat + Math.sin(ang) * 0.15, zStart],
                            target: [foco.lon + Math.cos(ang) * rDist, foco.lat + Math.sin(ang) * rDist, zEnd]
                        });
                    });
                }
            });

            if (cuerposNube.length > 0) {
                capasAnim.push(new deck.ScatterplotLayer({
                    id: 'climate-clouds-3d',
                    data: cuerposNube,
                    pickable: false,
                    billboard: true,
                    radiusUnits: 'meters',
                    getPosition: d => d.pos,
                    getRadius: d => d.radius,
                    getFillColor: d => d.color
                }));
            }

            if (lineasLluvia.length > 0) {
                capasAnim.push(new deck.LineLayer({
                    id: 'climate-rain-drops-3d',
                    data: lineasLluvia,
                    pickable: false,
                    getSourcePosition: d => d.source,
                    getTargetPosition: d => d.target,
                    getColor: [56, 189, 248, 225],
                    getWidth: 2.8
                }));
            }

            if (cuerposSol.length > 0) {
                capasAnim.push(new deck.ScatterplotLayer({
                    id: 'climate-suns-3d',
                    data: cuerposSol,
                    pickable: false,
                    billboard: true,
                    radiusUnits: 'meters',
                    getPosition: d => d.pos,
                    getRadius: d => d.radius,
                    getFillColor: d => d.color
                }));
            }

            if (lineasSol.length > 0) {
                capasAnim.push(new deck.LineLayer({
                    id: 'climate-sun-rays-3d',
                    data: lineasSol,
                    pickable: false,
                    getSourcePosition: d => d.source,
                    getTargetPosition: d => d.target,
                    getColor: [253, 224, 71, 185],
                    getWidth: 2.5
                }));
            }

            capasAnim.push(new deck.TextLayer({
                id: 'climate-badges-3d',
                data: state.focosClimaticos,
                getPosition: d => [d.lon, d.lat, 152000],
                getText: d => d.tipo === 'nube' ? `TORMENTA ${d.intensidad}x` : `OLA CALOR ${d.intensidad}x`,
                getSize: 11,
                getColor: d => d.tipo === 'nube' ? [125, 211, 252, 255] : [253, 224, 71, 255],
                getTextAnchor: 'middle',
                getAlignmentBaseline: 'bottom',
                fontFamily: 'JetBrains Mono, monospace',
                fontWeight: 700,
                background: true,
                getBackgroundColor: [7, 11, 20, 225],
                backgroundPadding: [5, 3]
            }));
        }

        return capasAnim;
    }

    function iniciarLoopAnimacion() {
        if (state.animId) return;

        function loop(timestamp) {
            // Rotación orbital suave (60fps)
            if (state.autoRotate && deckOverlay) {
                const nextBearing = ((state.viewState.bearing || 0) + 0.14) % 360;
                state.viewState = {
                    ...state.viewState,
                    bearing: nextBearing,
                    transitionDuration: 0
                };
                deckOverlay.setProps({ viewState: state.viewState });
                if (mapInstance) {
                    mapInstance.jumpTo({
                        center: [state.viewState.longitude, state.viewState.latitude],
                        zoom: state.viewState.zoom,
                        bearing: nextBearing,
                        pitch: state.viewState.pitch
                    });
                }
            }

            // Capas animadas WebGL (~24fps suaves para cero lag en portátiles)
            if (timestamp - state.lastAnimRender > 42 && deckOverlay && state.capasDatosBase.length > 0) {
                state.animTick += 0.06;
                state.lastAnimRender = timestamp;
                deckOverlay.setProps({
                    layers: [...state.capasDatosBase, ...construirCapasAnimadas()]
                });
            }

            state.animId = requestAnimationFrame(loop);
        }
        state.animId = requestAnimationFrame(loop);
    }

    // 7. Actualización Integral de Vista, KPIs, Ranking y Simulador
    function actualizarVista() {
        const periodoActual = state.periodos[state.indicePeriodo];
        const timelineEvento = state.dataset.timeline[state.eventoActual];
        if (!timelineEvento || !timelineEvento[periodoActual]) return;

        const rawFrame = timelineEvento[periodoActual];
        const dataFrame = simularFrame(rawFrame, state.eventoActual);
        state.frameSimuladoActual = dataFrame;
        state.capasDatosBase = construirCapasBase(dataFrame);

        deckOverlay.setProps({
            layers: [...state.capasDatosBase, ...construirCapasAnimadas()]
        });

        // KPIs Cabecera
        document.getElementById('kpi-casos').textContent = dataFrame.totales.casos.toLocaleString();
        document.getElementById('kpi-meds').textContent = dataFrame.totales.meds.toLocaleString();
        document.getElementById('kpi-criticos').textContent = dataFrame.totales.criticos;
        document.getElementById('kpi-alertas').textContent = dataFrame.totales.alertas;

        const kpiDelta = document.getElementById('kpi-casos-delta');
        if (state.focosClimaticos.length > 0 && dataFrame.totales.deltaCasos !== 0) {
            const dTot = dataFrame.totales.deltaCasos;
            kpiDelta.textContent = `${dTot > 0 ? '+' : ''}${dTot.toLocaleString()}`;
            kpiDelta.className = `kpi-delta ${dTot > 0 ? 'up' : 'down'}`;
        } else {
            kpiDelta.className = 'kpi-delta hidden';
        }

        // Timeline Display
        document.getElementById('timeline-slider').value = state.indicePeriodo;
        document.getElementById('timeline-periodo-tag').textContent = periodoActual;

        const tipoBadge = document.getElementById('timeline-tipo-tag');
        const esProyeccion = periodoActual >= state.dataset.metadata.inicio_proyeccion;
        if (esProyeccion) {
            tipoBadge.textContent = 'PROYECCIÓN IA (2025-27)';
            tipoBadge.className = 'tipo-badge badge-ia';
        } else {
            tipoBadge.textContent = 'HISTÓRICO REAL';
            tipoBadge.className = 'tipo-badge badge-real';
        }

        actualizarRanking(dataFrame);
        actualizarEstadoSimuladorUI(dataFrame);

        if (state.deptoSeleccionado) {
            const deptoActualizado = dataFrame.deptos.find(d => d.depto === state.deptoSeleccionado.depto);
            if (deptoActualizado) {
                mostrarInspector(deptoActualizado);
            }
        }
    }

    // Top 5 Departamentos Críticos en Vivo
    function actualizarRanking(dataFrame) {
        const container = document.getElementById('ranking-list');
        if (!container) return;

        const ordenados = [...dataFrame.deptos]
            .sort((a, b) => (b.ratio_presion - a.ratio_presion) || (b.casos - a.casos))
            .slice(0, 5);

        const maxRatio = Math.max(100, ordenados[0]?.ratio_presion || 100);

        container.innerHTML = ordenados.map((d, i) => {
            const color = d.alerta === 'CRÍTICO' ? '#ef4444' : (d.alerta === 'ALERTA' ? '#f59e0b' : '#10b981');
            const pctWidth = Math.min(100, Math.max(8, Math.round((d.ratio_presion / maxRatio) * 100)));
            return `
                <button type="button" class="rank-row" data-depto="${d.depto}" title="Clic para volar a ${d.depto}">
                    <div class="rank-top">
                        <span class="rank-name">${i + 1}. ${d.depto}</span>
                        <span class="rank-meta" style="color:${color}">${d.casos.toLocaleString()} c · ${d.ratio_presion}%</span>
                    </div>
                    <div class="rank-bar-bg">
                        <div class="rank-bar-fill" style="width:${pctWidth}%; background:${color};"></div>
                    </div>
                </button>
            `;
        }).join('');

        container.querySelectorAll('.rank-row').forEach(btn => {
            btn.addEventListener('click', () => {
                const dep = dataFrame.deptos.find(x => x.depto === btn.dataset.depto);
                if (dep) enfocarDepartamento(dep, true);
            });
        });
    }

    function actualizarBadgeCorrelacion() {
        const corr = obtenerCorrelacionEvento(state.eventoActual);
        const badge = document.getElementById('sim-corr-badge');
        if (!badge) return;
        const fNum = v => `${v >= 0 ? '+' : ''}${v.toFixed(2)}`;
        badge.textContent = `Correlación ML: Temp ${fNum(corr.r_temp)} | Lluvia ${fNum(corr.r_lluvia)}`;
    }

    function actualizarEstadoSimuladorUI(dataFrame) {
        const btnReset = document.getElementById('btn-reset-climate');
        const statusEl = document.getElementById('sim-active-status');

        if (!state.focosClimaticos.length) {
            btnReset.classList.add('hidden');
            statusEl.textContent = state.herramientaClima === 'cursor'
                ? 'Elige un Macro-Escenario o Nube/Sol y haz clic en el mapa'
                : 'Haz clic sobre cualquier departamento del mapa 3D';
            return;
        }

        btnReset.classList.remove('hidden');
        const afectados = dataFrame.deptos.filter(d => d.afectadoPorSim).length;
        if (state.macroActivo) {
            const label = state.macroActivo === 'nino' ? '☀️ Fenómeno del Niño' : '🌧️ Fenómeno de La Niña';
            statusEl.innerHTML = `<strong>${label}</strong> activo (${afectados} deptos impactados)`;
            return;
        }

        const resumen = state.focosClimaticos.slice(0, 3).map(f => {
            const dInfo = dataFrame.deptos.find(d => d.depto === f.depto);
            const icono = f.tipo === 'nube' ? '🌧️' : '☀️';
            const deltaStr = dInfo && dInfo.deltaCasos !== 0
                ? ` (${dInfo.deltaCasos > 0 ? '+' : ''}${dInfo.pctCambio}%)`
                : '';
            return `${icono} ${f.depto}${deltaStr}`;
        }).join(' · ');
        const extra = state.focosClimaticos.length > 3 ? ` +${state.focosClimaticos.length - 3}` : '';
        statusEl.innerHTML = `<strong>${state.focosClimaticos.length} foco(s)</strong> (${afectados} deptos): ${resumen}${extra}`;
    }

    // 8. Tooltip Inteligente 3D (en móviles se usa directamente el Bottom-Sheet táctil)
    function renderTooltip({ object }) {
        if (!object || isMobileViewport()) return null;

        if (object.origen_coords) {
            return {
                html: `
                    <div style="font-family: Inter, sans-serif; padding: 6px; font-size: 12px; color: #fff;">
                        <strong style="color: #38bdf8;">DESPACHO FARMACÉUTICO DE EMERGENCIA</strong><br>
                        <strong>Ruta:</strong> ${object.origen_nombre} &rarr; ${object.destino}<br>
                        <strong>Criticidad:</strong> ${object.criticidad}<br>
                        <strong>Volumen Requerido:</strong> ${object.volumen_despacho.toLocaleString()} und
                    </div>
                `,
                style: {
                    backgroundColor: 'rgba(11, 18, 34, 0.96)',
                    border: '1px solid #38bdf8',
                    borderRadius: '8px',
                    boxShadow: '0 8px 24px rgba(0,0,0,0.65)'
                }
            };
        }

        let deptoData = object;
        if (object.properties && object.properties.NOMBRE_DPT) {
            const deptoNombre = normalizarNombre(object.properties.NOMBRE_DPT);
            const df = state.frameSimuladoActual;
            deptoData = df ? df.deptos.find(d => d.depto === deptoNombre) : null;
            if (!deptoData) {
                deptoData = {
                    depto: deptoNombre, capital: 'Colombia', alerta: 'ESTABLE',
                    casos: 0, meds: 0, ratio_presion: 0, temp: 24, lluvia: 100, hum: 75, es_proyeccion: false
                };
            }
        }

        const colorAlerta = deptoData.alerta === 'CRÍTICO' ? '#ef4444' : (deptoData.alerta === 'ALERTA' ? '#f59e0b' : '#10b981');
        const simTag = deptoData.afectadoPorSim && deptoData.deltaCasos !== 0
            ? `<div style="color:${deptoData.deltaCasos > 0 ? '#fca5a5' : '#6ee7b7'}; font-size:10px; font-weight:700; margin-top:2px;">⚡ Simulación Clima: ${deptoData.deltaCasos > 0 ? '+' : ''}${deptoData.deltaCasos.toLocaleString()} casos (${deptoData.pctCambio > 0 ? '+' : ''}${deptoData.pctCambio}%)</div>`
            : '';

        const hintHerramienta = state.herramientaClima !== 'cursor'
            ? `<div style="color:#38bdf8; font-size:10px; margin-top:4px; font-weight:600;">Clic para soltar ${state.herramientaClima === 'nube' ? '🌧️ Tormenta' : '☀️ Ola de Calor'} aquí</div>`
            : `<div style="color:#94a3b8; font-size:9.5px; margin-top:4px;">Clic para abrir Inspector + Curva 2017-2027</div>`;

        return {
            html: `
                <div style="font-family: Inter, sans-serif; padding: 8px; font-size: 12px; color: #fff; min-width: 195px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <strong style="font-size:13.5px;">${deptoData.depto}</strong>
                        <span style="color: ${colorAlerta}; font-weight:800; font-size:10px; border:1px solid ${colorAlerta}; padding:1px 5px; border-radius:3px;">
                            ${deptoData.alerta}
                        </span>
                    </div>
                    <div style="color:#94a3b8; font-size:11px; margin-bottom:6px;">Capital: ${deptoData.capital}</div>
                    <div style="margin-bottom:2px;"><strong>Casos Mes:</strong> <span style="color:#38bdf8;">${deptoData.casos.toLocaleString()}</span></div>
                    <div style="margin-bottom:2px;"><strong>Stock Meds:</strong> ${deptoData.meds.toLocaleString()} und</div>
                    <div style="margin-bottom:2px;"><strong>Tensión Logística:</strong> <span style="color:${colorAlerta}; font-weight:bold;">${deptoData.ratio_presion}%</span></div>
                    <div style="color:#94a3b8; font-size:10px; margin-top:4px;">🌡️ ${deptoData.temp}°C | 🌧️ ${deptoData.lluvia}mm | 💧 ${deptoData.hum}%</div>
                    ${simTag}
                    <div style="font-size:9px; color:#c084fc; margin-top:3px;">${deptoData.es_proyeccion ? '★ Predicción Machine Learning' : '• Registro SIVIGILA'}</div>
                    ${hintHerramienta}
                </div>
            `,
            style: {
                backgroundColor: 'rgba(11, 18, 34, 0.96)',
                border: `1px solid ${colorAlerta}`,
                borderRadius: '8px',
                boxShadow: '0 8px 24px rgba(0,0,0,0.65)'
            }
        };
    }

    // 9. Inspector Lateral Detallado + Sparkline 2017-2027 + Explicabilidad IA
    function renderSparkline(deptoNombre) {
        const box = document.getElementById('ins-sparkline');
        const peakTag = document.getElementById('ins-spark-peak');
        if (!box) return;

        const timelineEv = state.dataset.timeline[state.eventoActual] || {};
        const inicioProj = state.dataset.metadata.inicio_proyeccion;

        const serie = state.periodos.map((per, idx) => {
            const frame = timelineEv[per];
            const rec = frame ? frame.deptos.find(d => d.depto === deptoNombre) : null;
            return {
                idx,
                per,
                casos: rec ? rec.casos : 0,
                esProj: per >= inicioProj
            };
        });

        const maxVal = Math.max(10, ...serie.map(s => s.casos));
        const peakObj = serie.reduce((best, s) => (s.casos > best.casos ? s : best), serie[0]);
        if (peakTag && peakObj) {
            peakTag.textContent = `Pico: ${peakObj.casos.toLocaleString()} (${peakObj.per})`;
        }

        const W = 260, H = 62, padX = 4, padY = 6;
        const innerW = W - padX * 2;
        const innerH = H - padY * 2;
        const xOf = i => padX + (i / Math.max(1, serie.length - 1)) * innerW;
        const yOf = v => padY + innerH - (v / maxVal) * innerH;

        const realPts = serie.filter(s => !s.esProj);
        const projPts = serie.filter(s => s.esProj);
        const splitIdx = realPts.length > 0 ? realPts[realPts.length - 1].idx : 0;

        const realPath = realPts.map((s, k) => `${k === 0 ? 'M' : 'L'}${xOf(s.idx).toFixed(1)},${yOf(s.casos).toFixed(1)}`).join(' ');
        const projFull = realPts.length > 0 ? [realPts[realPts.length - 1], ...projPts] : projPts;
        const projPath = projFull.map((s, k) => `${k === 0 ? 'M' : 'L'}${xOf(s.idx).toFixed(1)},${yOf(s.casos).toFixed(1)}`).join(' ');

        const allPath = serie.map((s, k) => `${k === 0 ? 'M' : 'L'}${xOf(s.idx).toFixed(1)},${yOf(s.casos).toFixed(1)}`).join(' ');
        const areaPath = `${allPath} L${xOf(serie.length - 1).toFixed(1)},${(H - padY).toFixed(1)} L${xOf(0).toFixed(1)},${(H - padY).toFixed(1)} Z`;

        const cur = serie[state.indicePeriodo] || serie[0];
        const curX = xOf(cur.idx).toFixed(1);
        const curY = yOf(cur.casos).toFixed(1);
        const splitX = xOf(splitIdx).toFixed(1);

        box.innerHTML = `
            <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
                <defs>
                    <linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.32"/>
                        <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.02"/>
                    </linearGradient>
                </defs>
                <line x1="${splitX}" y1="${padY}" x2="${splitX}" y2="${H - padY}" stroke="rgba(168,85,247,0.45)" stroke-dasharray="3 3" stroke-width="1"/>
                <path d="${areaPath}" fill="url(#sparkFill)"/>
                <path d="${realPath}" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linejoin="round"/>
                <path d="${projPath}" fill="none" stroke="#c084fc" stroke-width="2" stroke-dasharray="4 2" stroke-linejoin="round"/>
                <circle cx="${curX}" cy="${curY}" r="4.2" fill="#ffffff" stroke="${cur.esProj ? '#c084fc' : '#38bdf8'}" stroke-width="2.2"/>
            </svg>
        `;

        // Clic en el sparkline para viajar directamente a ese mes
        const svgEl = box.querySelector('svg');
        if (svgEl) {
            svgEl.addEventListener('click', (e) => {
                const rect = svgEl.getBoundingClientRect();
                const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
                state.indicePeriodo = Math.round(ratio * (state.periodos.length - 1));
                actualizarVista();
            });
        }
    }

    function renderExplicabilidadML(depto) {
        const listEl = document.getElementById('ins-ml-reasons');
        if (!listEl) return;

        const corr = obtenerCorrelacionEvento(state.eventoActual);
        const razones = [];

        if (depto.casos > 378) {
            razones.push(`<strong>Brote Atípico (IQR):</strong> ${depto.casos.toLocaleString()} casos supera el umbral nacional (&gt;378 casos/mes).`);
        } else if (depto.casos > 150) {
            razones.push(`<strong>Incidencia Elevada:</strong> ${depto.casos.toLocaleString()} casos activa vigilancia preventiva del Árbol de Decisión.`);
        } else {
            razones.push(`<strong>Incidencia Controlada:</strong> ${depto.casos.toLocaleString()} casos por debajo del umbral epidémico IQR (378).`);
        }

        if (depto.ratio_presion >= 120) {
            razones.push(`<strong>Regla Logística Crítica:</strong> Presión demanda/stock de <strong>${depto.ratio_presion}%</strong> (&ge;120% → desabastecimiento inminente).`);
        } else if (depto.ratio_presion >= 60) {
            razones.push(`<strong>Tensión de Inventario:</strong> Presión de <strong>${depto.ratio_presion}%</strong> exige pre-posicionamiento preventivo.`);
        } else {
            razones.push(`<strong>Cobertura Estable:</strong> Presión de <strong>${depto.ratio_presion}%</strong> dentro de margen operativo SISMED.`);
        }

        const dirTemp = corr.r_temp >= 0 ? 'positiva' : 'inversa';
        razones.push(`<strong>Factor Climático (IDEAM):</strong> Sensibilidad ${dirTemp} a temperatura (r=${corr.r_temp >= 0 ? '+' : ''}${corr.r_temp.toFixed(2)}) · ${depto.es_proyeccion ? 'Proyección IA 2025-27' : 'Dato verificado SIVIGILA'}.`);

        listEl.innerHTML = razones.map(r => `<li>${r}</li>`).join('');
    }

    function mostrarInspector(depto) {
        state.deptoSeleccionado = depto;
        const panel = document.getElementById('inspector-card');
        panel.classList.remove('hidden');

        // En pantallas de baja altura, colapsar ranking automáticamente para que el Inspector luzca completo
        if (window.innerHeight <= 860) {
            const rankPanel = document.getElementById('ranking-panel');
            if (rankPanel) rankPanel.classList.add('collapsed');
        }

        document.getElementById('ins-depto').textContent = depto.depto;
        document.getElementById('ins-capital').innerHTML = `<i data-lucide="map-pin"></i> Capital: ${depto.capital}`;

        const badge = document.getElementById('ins-badge');
        badge.textContent = depto.alerta;
        badge.className = `badge-status status-${depto.alerta.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')}`;

        const badgeSim = document.getElementById('ins-sim-delta');
        if (depto.afectadoPorSim && depto.deltaCasos !== 0) {
            const signo = depto.deltaCasos > 0 ? '+' : '';
            badgeSim.textContent = `${signo}${depto.pctCambio}% Clima`;
            badgeSim.className = `badge-sim-delta ${depto.deltaCasos > 0 ? 'up' : 'down'}`;
        } else {
            badgeSim.className = 'badge-sim-delta hidden';
        }

        document.getElementById('ins-casos').textContent = depto.casos.toLocaleString();
        document.getElementById('ins-meds').textContent = `${depto.meds.toLocaleString()} u`;
        document.getElementById('ins-demanda').textContent = `${depto.demanda_est ? depto.demanda_est.toLocaleString() : 0} u`;
        document.getElementById('ins-tension').textContent = `${depto.ratio_presion}%`;

        document.getElementById('ins-temp').textContent = `${depto.temp} °C`;
        document.getElementById('ins-lluvia').textContent = `${depto.lluvia} mm`;
        document.getElementById('ins-hum').textContent = `${depto.hum} %`;

        renderSparkline(depto.depto);
        renderExplicabilidadML(depto);

        const focoActivo = state.focosClimaticos.find(f => f.depto === depto.depto);
        document.getElementById('btn-ins-nube').classList.toggle('active', focoActivo?.tipo === 'nube');
        document.getElementById('btn-ins-sol').classList.toggle('active', focoActivo?.tipo === 'sol');
        document.getElementById('btn-ins-clear').classList.toggle('hidden', !focoActivo);

        const descLogistica = document.getElementById('ins-logistics-desc');
        if (depto.alerta === 'CRÍTICO') {
            descLogistica.innerHTML = `⚠️ <strong class="text-red">DESABASTECIMIENTO SEVERO:</strong> Demanda supera stock en ${depto.ratio_presion}%. Activar compra extraordinaria y puente aéreo urgente desde el Hub más cercano.`;
        } else if (depto.alerta === 'ALERTA') {
            descLogistica.innerHTML = `⚡ <strong class="text-amber">TENSIÓN MODERADA:</strong> Consumo acelerado. Pre-posicionar stock regulador 45 días antes del pico climático.`;
        } else {
            descLogistica.innerHTML = `✅ <strong class="text-green">INVENTARIO SEGURO:</strong> Cobertura hospitalaria superior a 45 días de contingencia regular.`;
        }

        if (isMobileViewport()) {
            document.getElementById('mobile-backdrop')?.classList.remove('hidden');
        }
        if (window.lucide) lucide.createIcons();
    }

    // 10. Tour Guiado Cinematográfico ("Modo Jurado")
    function ejecutarEscenaTour(sceneKey) {
        const escena = ESCENAS_TOUR[sceneKey];
        if (!escena) return;

        state.escenaActiva = sceneKey;
        document.querySelectorAll('.btn-tour').forEach(b => {
            b.classList.toggle('active', b.dataset.scene === sceneKey);
        });

        // Cambiar Patología si existe
        const selectEv = document.getElementById('select-evento');
        if (state.dataset.timeline[escena.evento]) {
            state.eventoActual = escena.evento;
            if (selectEv) selectEv.value = escena.evento;
            actualizarBadgeCorrelacion();
        }

        // Cambiar Periodo exacto
        const idxPer = state.periodos.indexOf(escena.periodo);
        if (idxPer >= 0) {
            state.indicePeriodo = idxPer;
        }

        // Asegurar capas 3D activas
        state.mostrarPoligonos = true;
        state.mostrarArcos = true;
        state.pitch3D = true;
        document.getElementById('btn-toggle-poligonos')?.classList.add('active');
        document.getElementById('btn-toggle-arcos')?.classList.add('active');
        document.getElementById('btn-pitch-3d')?.classList.add('active');

        // Configurar Macro-Escenario Climático
        state.focosClimaticos = [];
        state.macroActivo = null;
        actualizarBotonesMacro();

        if (escena.macro) {
            activarMacroEscenario(escena.macro);
        } else {
            actualizarVista();
        }

        // Rotación y Cámara Cinematográfica
        setAutoRotate(false);
        const targetCam = {
            ...escena.camera,
            zoom: isMobileViewport() ? Math.max(4.6, escena.camera.zoom - 0.8) : escena.camera.zoom
        };
        volarA(targetCam, 1300);

        if (escena.rotate) {
            setTimeout(() => setAutoRotate(true), 1350);
        }

        // Inspector
        if (escena.focusDepto && state.frameSimuladoActual) {
            const dep = state.frameSimuladoActual.deptos.find(d => d.depto === escena.focusDepto);
            if (dep) mostrarInspector(dep);
        } else {
            document.getElementById('inspector-card')?.classList.add('hidden');
            state.deptoSeleccionado = null;
        }

        // Mostrar Banner Narrativo
        document.getElementById('story-step-tag').textContent = escena.tag;
        document.getElementById('story-title').textContent = escena.titulo;
        document.getElementById('story-desc').textContent = escena.desc;
        document.getElementById('story-banner').classList.remove('hidden');

        // Cerrar drawers móviles para ver el vuelo 3D
        cerrarDrawersMoviles();
    }

    // 11. Helpers de Modo Cine, Rotación y Drawers Móviles
    function setAutoRotate(activo) {
        state.autoRotate = activo;
        document.getElementById('btn-auto-rotate')?.classList.toggle('active', activo);
    }

    function toggleZenMode(forceVal) {
        state.zenMode = typeof forceVal === 'boolean' ? forceVal : !state.zenMode;
        document.body.classList.toggle('zen-mode', state.zenMode);
        document.getElementById('btn-exit-zen')?.classList.toggle('hidden', !state.zenMode);
        if (state.zenMode) cerrarDrawersMoviles();
    }

    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen?.();
        } else {
            document.exitFullscreen?.();
        }
    }

    function abrirDrawerMovil(lado, focoSeccion = null) {
        const left = document.getElementById('hud-left-col');
        const right = document.getElementById('hud-right-col');
        const backdrop = document.getElementById('mobile-backdrop');

        // Ocultar bottom-sheet inspector al abrir un drawer lateral
        document.getElementById('inspector-card')?.classList.add('hidden');
        state.deptoSeleccionado = null;

        if (lado === 'left') {
            right?.classList.remove('drawer-open');
            const opened = left?.classList.toggle('drawer-open');
            backdrop?.classList.toggle('hidden', !opened);
            if (opened && focoSeccion === 'tour') {
                document.getElementById('tour-panel')?.classList.remove('collapsed');
                document.getElementById('ranking-panel')?.classList.add('collapsed');
            } else if (opened && focoSeccion === 'ranking') {
                document.getElementById('ranking-panel')?.classList.remove('collapsed');
                document.getElementById('tour-panel')?.classList.add('collapsed');
            }
        } else {
            left?.classList.remove('drawer-open');
            const opened = right?.classList.toggle('drawer-open');
            backdrop?.classList.toggle('hidden', !opened);
        }
    }

    function cerrarDrawersMoviles() {
        document.getElementById('hud-left-col')?.classList.remove('drawer-open');
        document.getElementById('hud-right-col')?.classList.remove('drawer-open');
        const insOpen = !document.getElementById('inspector-card')?.classList.contains('hidden');
        if (!insOpen || !isMobileViewport()) {
            document.getElementById('mobile-backdrop')?.classList.add('hidden');
        }
    }

    function cerrarInspector() {
        document.getElementById('inspector-card')?.classList.add('hidden');
        state.deptoSeleccionado = null;
        cerrarDrawersMoviles();
    }

    function toggleCrispModal(forceOpen) {
        const modal = document.getElementById('crispdm-modal');
        if (!modal) return;
        const willOpen = typeof forceOpen === 'boolean' ? forceOpen : modal.classList.contains('hidden');
        modal.classList.toggle('hidden', !willOpen);
        if (willOpen) {
            cerrarDrawersMoviles();
            if (window.lucide) lucide.createIcons();
        }
    }

    function abrirLightbox(src, title) {
        const lb = document.getElementById('crispdm-lightbox');
        if (!lb) return;
        document.getElementById('lightbox-img').src = src;
        document.getElementById('lightbox-title').textContent = title || 'Evidencia CRISP-DM';
        lb.classList.remove('hidden');
    }

    function cerrarLightbox() {
        document.getElementById('crispdm-lightbox')?.classList.add('hidden');
    }

    // 12. Configuración de Listeners y Controles
    function seleccionarHerramientaClima(tool) {
        state.herramientaClima = tool;
        document.querySelectorAll('.btn-sim-tool').forEach(b => {
            b.classList.toggle('active', b.dataset.tool === tool);
        });

        const mapEl = document.getElementById('map-container');
        mapEl.classList.toggle('cursor-rain', tool === 'nube');
        mapEl.classList.toggle('cursor-sun', tool === 'sol');

        if (state.frameSimuladoActual) {
            actualizarEstadoSimuladorUI(state.frameSimuladoActual);
        }
    }

    function configurarEventosUI() {
        // Selector de Patología
        document.getElementById('select-evento').addEventListener('change', (e) => {
            state.eventoActual = e.target.value;
            actualizarBadgeCorrelacion();
            actualizarVista();
        });

        // Salto rápido a cualquier departamento
        document.getElementById('select-depto-jump').addEventListener('change', (e) => {
            const nombre = e.target.value;
            if (!nombre || !state.frameSimuladoActual) return;
            const dep = state.frameSimuladoActual.deptos.find(d => d.depto === nombre);
            if (dep) enfocarDepartamento(dep, true);
            e.target.value = '';
        });

        // Header acciones (ADN CRISP-DM, Zen, Fullscreen, Shortcuts)
        document.getElementById('btn-open-crispdm')?.addEventListener('click', () => toggleCrispModal(true));
        document.getElementById('btn-close-crispdm')?.addEventListener('click', () => toggleCrispModal(false));
        const crispModal = document.getElementById('crispdm-modal');
        crispModal?.addEventListener('click', (e) => {
            if (e.target === crispModal) toggleCrispModal(false);
        });

        // Pestañas del Modal ADN CRISP-DM
        document.querySelectorAll('.crisp-tab').forEach(tabBtn => {
            tabBtn.addEventListener('click', () => {
                const targetTab = tabBtn.dataset.tab;
                document.querySelectorAll('.crisp-tab').forEach(b => b.classList.toggle('active', b === tabBtn));
                document.querySelectorAll('.crisp-pane').forEach(p => p.classList.toggle('active', p.id === `tab-${targetTab}`));
            });
        });

        // Galería Lightbox de gráficas reales de Python
        document.querySelectorAll('.crisp-fig').forEach(fig => {
            fig.addEventListener('click', () => {
                abrirLightbox(fig.dataset.zoomSrc, fig.dataset.zoomTitle);
            });
        });
        document.getElementById('btn-close-lightbox')?.addEventListener('click', cerrarLightbox);
        const lbModal = document.getElementById('crispdm-lightbox');
        lbModal?.addEventListener('click', (e) => {
            if (e.target === lbModal) cerrarLightbox();
        });

        // Botón Volar a Tolima 2019-07 desde la pestaña Métodos Numéricos
        document.getElementById('btn-crisp-fly-tolima')?.addEventListener('click', () => {
            toggleCrispModal(false);
            ejecutarEscenaTour('brote2019');
        });

        document.getElementById('btn-zen-mode')?.addEventListener('click', () => toggleZenMode(true));
        document.getElementById('btn-exit-zen')?.addEventListener('click', () => toggleZenMode(false));
        document.getElementById('btn-fullscreen')?.addEventListener('click', toggleFullscreen);

        const shortcutsModal = document.getElementById('shortcuts-modal');
        document.getElementById('btn-shortcuts')?.addEventListener('click', () => shortcutsModal?.classList.remove('hidden'));
        document.getElementById('btn-close-shortcuts')?.addEventListener('click', () => shortcutsModal?.classList.add('hidden'));
        shortcutsModal?.addEventListener('click', (e) => {
            if (e.target === shortcutsModal) shortcutsModal.classList.add('hidden');
        });

        // Banner Narrativo cerrar
        document.getElementById('btn-close-story')?.addEventListener('click', () => {
            document.getElementById('story-banner')?.classList.add('hidden');
        });

        // Tour del Jurado botones
        document.querySelectorAll('.btn-tour').forEach(btn => {
            btn.addEventListener('click', () => ejecutarEscenaTour(btn.dataset.scene));
        });

        // Widgets colapsables (Tour & Ranking)
        document.querySelectorAll('[data-collapse]').forEach(btn => {
            btn.addEventListener('click', () => {
                const target = document.getElementById(btn.dataset.collapse);
                if (target) target.classList.toggle('collapsed');
            });
        });

        // Botón Volar dentro del Inspector
        document.getElementById('btn-ins-fly')?.addEventListener('click', () => {
            if (state.deptoSeleccionado) enfocarDepartamento(state.deptoSeleccionado, false);
        });

        // Dock nativo móvil + drawers + backdrop
        document.getElementById('dock-tour')?.addEventListener('click', () => abrirDrawerMovil('left', 'tour'));
        document.getElementById('dock-ranking')?.addEventListener('click', () => abrirDrawerMovil('left', 'ranking'));
        document.getElementById('dock-clima')?.addEventListener('click', () => abrirDrawerMovil('right'));
        document.getElementById('dock-crispdm')?.addEventListener('click', () => toggleCrispModal(true));

        document.getElementById('mobile-backdrop')?.addEventListener('click', () => {
            cerrarInspector();
            cerrarDrawersMoviles();
        });
        document.querySelectorAll('.btn-drawer-close').forEach(btn => {
            btn.addEventListener('click', cerrarDrawersMoviles);
        });

        // Slider del Timeline
        document.getElementById('timeline-slider').addEventListener('input', (e) => {
            state.indicePeriodo = parseInt(e.target.value);
            actualizarVista();
        });

        // Botones Media
        document.getElementById('btn-play').addEventListener('click', alternarReproduccion);
        document.getElementById('btn-prev').addEventListener('click', () => {
            if (state.indicePeriodo > 0) {
                state.indicePeriodo--;
                actualizarVista();
            }
        });
        document.getElementById('btn-next').addEventListener('click', () => {
            if (state.indicePeriodo < state.periodos.length - 1) {
                state.indicePeriodo++;
                actualizarVista();
            }
        });

        // Velocidades
        document.querySelectorAll('.btn-speed').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.btn-speed').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const multiplicador = parseFloat(btn.dataset.speed);
                state.velocidad = 1200 / multiplicador;
                if (state.isPlaying) {
                    clearInterval(state.playInterval);
                    state.playInterval = setInterval(avanzarPaso, state.velocidad);
                }
            });
        });

        // Macro-Escenarios Climáticos (El Niño / La Niña)
        document.getElementById('btn-macro-nino')?.addEventListener('click', () => activarMacroEscenario('nino'));
        document.getElementById('btn-macro-nina')?.addEventListener('click', () => activarMacroEscenario('nina'));

        // Herramientas Simulador Climático
        document.querySelectorAll('.btn-sim-tool').forEach(btn => {
            btn.addEventListener('click', () => seleccionarHerramientaClima(btn.dataset.tool));
        });

        document.querySelectorAll('.btn-intensity').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.btn-intensity').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                state.intensidadClima = parseInt(btn.dataset.level);
                if (state.focosClimaticos.length > 0) {
                    state.focosClimaticos = state.focosClimaticos.map(f => ({
                        ...f,
                        intensidad: state.intensidadClima
                    }));
                    actualizarVista();
                }
            });
        });

        document.getElementById('btn-reset-climate').addEventListener('click', limpiarTodosFocos);

        // Botones climáticos del Inspector
        document.getElementById('btn-ins-nube').addEventListener('click', () => {
            if (state.deptoSeleccionado) {
                state.macroActivo = null;
                actualizarBotonesMacro();
                aplicarFocoClimatico(state.deptoSeleccionado, 'nube', state.intensidadClima);
            }
        });

        document.getElementById('btn-ins-sol').addEventListener('click', () => {
            if (state.deptoSeleccionado) {
                state.macroActivo = null;
                actualizarBotonesMacro();
                aplicarFocoClimatico(state.deptoSeleccionado, 'sol', state.intensidadClima);
            }
        });

        document.getElementById('btn-ins-clear').addEventListener('click', () => {
            if (state.deptoSeleccionado) quitarFocoDepartamento(state.deptoSeleccionado.depto);
        });

        // Cerrar Inspector
        document.getElementById('btn-close-inspector').addEventListener('click', cerrarInspector);

        // Leyenda colapsable
        const btnToggleLegend = document.getElementById('btn-toggle-legend');
        const legendPanel = document.getElementById('legend-panel');
        if (btnToggleLegend && legendPanel) {
            btnToggleLegend.addEventListener('click', () => legendPanel.classList.toggle('collapsed'));
        }

        // Toggle Polígonos 3D
        const btnPoligonos = document.getElementById('btn-toggle-poligonos');
        btnPoligonos?.addEventListener('click', () => {
            state.mostrarPoligonos = !state.mostrarPoligonos;
            btnPoligonos.classList.toggle('active', state.mostrarPoligonos);
            actualizarVista();
        });

        // Toggle Pitch 3D (con transición suave controlada)
        const btnPitch = document.getElementById('btn-pitch-3d');
        btnPitch?.addEventListener('click', () => {
            state.pitch3D = !state.pitch3D;
            btnPitch.classList.toggle('active', state.pitch3D);
            volarA({ pitch: state.pitch3D ? 52 : 0 }, 750);
        });

        // Toggle Rotación Cinematográfica
        document.getElementById('btn-auto-rotate')?.addEventListener('click', () => {
            setAutoRotate(!state.autoRotate);
        });

        // Toggle Arcos Logísticos
        const btnArcos = document.getElementById('btn-toggle-arcos');
        btnArcos?.addEventListener('click', () => {
            state.mostrarArcos = !state.mostrarArcos;
            btnArcos.classList.toggle('active', state.mostrarArcos);
            actualizarVista();
        });

        // Centrar Colombia 3D
        document.getElementById('btn-reset-cam')?.addEventListener('click', () => {
            setAutoRotate(false);
            state.pitch3D = true;
            document.getElementById('btn-pitch-3d')?.classList.add('active');
            volarA(getInitialViewState(), 1000);
        });
    }

    // 13. Atajos de Teclado para la Sustentación
    function configurarAtajosTeclado() {
        document.addEventListener('keydown', (e) => {
            if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) return;

            const key = e.key.toLowerCase();
            if (e.code === 'Space') {
                e.preventDefault();
                alternarReproduccion();
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                if (state.indicePeriodo < state.periodos.length - 1) {
                    state.indicePeriodo++;
                    actualizarVista();
                }
            } else if (e.key === 'ArrowLeft') {
                e.preventDefault();
                if (state.indicePeriodo > 0) {
                    state.indicePeriodo--;
                    actualizarVista();
                }
            } else if (key === 'c') {
                toggleCrispModal();
            } else if (key === 'h') {
                toggleZenMode();
            } else if (key === 'r') {
                setAutoRotate(!state.autoRotate);
            } else if (key === 'f') {
                toggleFullscreen();
            } else if (e.key === '1') {
                ejecutarEscenaTour('brote2019');
            } else if (e.key === '2') {
                ejecutarEscenaTour('proyeccion2027');
            } else if (e.key === '3') {
                ejecutarEscenaTour('elnino');
            } else if (e.key === '4') {
                ejecutarEscenaTour('logistica');
            } else if (e.key === 'Escape') {
                const lb = document.getElementById('crispdm-lightbox');
                const crisp = document.getElementById('crispdm-modal');
                const modal = document.getElementById('shortcuts-modal');
                if (lb && !lb.classList.contains('hidden')) {
                    cerrarLightbox();
                } else if (crisp && !crisp.classList.contains('hidden')) {
                    toggleCrispModal(false);
                } else if (modal && !modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                } else if (state.zenMode) {
                    toggleZenMode(false);
                } else {
                    document.getElementById('story-banner')?.classList.add('hidden');
                    cerrarInspector();
                }
            }
        });
    }

    // 14. Reproducción Automática del Timeline
    function alternarReproduccion() {
        state.isPlaying = !state.isPlaying;
        const btnPlay = document.getElementById('btn-play');

        if (state.isPlaying) {
            btnPlay.innerHTML = '<i data-lucide="pause"></i>';
            if (state.indicePeriodo >= state.periodos.length - 1) {
                state.indicePeriodo = 0;
            }
            state.playInterval = setInterval(avanzarPaso, state.velocidad);
        } else {
            btnPlay.innerHTML = '<i data-lucide="play"></i>';
            clearInterval(state.playInterval);
        }
        if (window.lucide) lucide.createIcons();
    }

    function avanzarPaso() {
        if (state.indicePeriodo < state.periodos.length - 1) {
            state.indicePeriodo++;
            actualizarVista();
        } else {
            alternarReproduccion();
        }
    }
})();
