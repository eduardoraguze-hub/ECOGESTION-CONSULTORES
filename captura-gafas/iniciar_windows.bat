@echo off
REM Inicia el organizador en segundo plano. Para que arranque solo al encender la PC:
REM   Win+R -> shell:startup -> pega un acceso directo a este archivo.
cd /d "%~dp0"
if not exist config.json copy config.ejemplo.json config.json
python -m pip install --quiet --user pillow
start "Evidencias Gafas" /min python organizador_evidencias.py vigilar
