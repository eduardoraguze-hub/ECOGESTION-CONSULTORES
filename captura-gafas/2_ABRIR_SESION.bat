@echo off
chcp 65001 >nul
title Abrir sesion de auditoria
cd /d "%~dp0"
python organizador_evidencias.py menu
pause
