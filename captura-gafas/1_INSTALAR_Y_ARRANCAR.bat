@echo off
chcp 65001 >nul
title Evidencias Gafas - Instalacion
cd /d "%~dp0"
echo ============================================================
echo   ORGANIZADOR DE EVIDENCIAS - INSTALACION (solo una vez)
echo ============================================================
where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo No encontre Python. Lo instalo ahora...
  winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  echo.
  echo Python instalado. CIERRA esta ventana y vuelve a abrir 1_INSTALAR_Y_ARRANCAR.
  pause
  exit /b
)
echo [1/4] Instalando componente de fotos...
python -m pip install --quiet --user pillow
echo [2/4] Creando configuracion...
if not exist config.json copy config.ejemplo.json config.json >nul
echo [3/4] Programando arranque automatico al encender la PC...
set "INICIO=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
> "%INICIO%\Evidencias_Gafas.bat" echo @echo off
>> "%INICIO%\Evidencias_Gafas.bat" echo cd /d "%~dp0"
>> "%INICIO%\Evidencias_Gafas.bat" echo start "" pythonw "%~dp0organizador_evidencias.py" vigilar
echo [4/4] Arrancando el organizador en segundo plano...
start "" pythonw "%~dp0organizador_evidencias.py" vigilar
echo.
python organizador_evidencias.py estado
echo.
echo ============================================================
echo   LISTO. El organizador ya esta trabajando y arrancara solo
echo   cada vez que enciendas la PC. Puedes cerrar esta ventana.
echo ============================================================
pause
