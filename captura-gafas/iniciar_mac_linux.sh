#!/usr/bin/env bash
# Inicia el organizador en segundo plano y deja el log en organizador.log
cd "$(dirname "$0")"
[ -f config.json ] || cp config.ejemplo.json config.json
python3 -m pip install --quiet --user pillow 2>/dev/null || true
nohup python3 organizador_evidencias.py vigilar >> organizador.log 2>&1 &
echo "Organizador iniciado (PID $!). Log: $(pwd)/organizador.log"
