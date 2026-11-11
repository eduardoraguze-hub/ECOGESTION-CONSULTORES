@echo off
chcp 65001 >nul
cd /d "%~dp0"
python organizador_evidencias.py cerrar
pause
