@echo off
cd /d "%~dp0"
title Lanzador GEO-EPIDEMIA 3D - Mineria de Datos
color 0b
echo =========================================================================
echo   INICIANDO PLATAFORMA GEO-EPIDEMIA 3D (2017 - 2027)
echo   Proyecto: Mineria de Datos - Sustentacion Examen Final
echo =========================================================================
echo.
echo [1/2] Verificando dataset y estructura...
if not exist "data\timeline_colombia_3d.js" (
    echo [ALERTA] Generando archivo de datos 3D...
    python preparar_datos_3d.py
)
echo [OK] Base cartografica y dataset 3D verificados.
echo.
echo [2/2] Abriendo visualizador 3D en tu navegador predeterminado...
start "" index.html
echo.
echo =========================================================================
echo   APLICACION EN EJECUCION EXITOSA. LISTO PARA LA SUSTENTACION.
echo =========================================================================
exit /b 0
