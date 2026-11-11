@echo off
chcp 65001 >nul
cd /d "%~dp0"
python organizador_evidencias.py estado
echo.
echo --- Ultimas 15 evidencias procesadas ---
powershell -NoProfile -Command "if (Test-Path organizador.log) { Get-Content organizador.log -Tail 15 -Encoding UTF8 } else { 'Aun no hay actividad.' }"
pause
