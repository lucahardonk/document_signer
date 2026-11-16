#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# Crea venv se non esiste
if [ ! -d ".venv" ]; then
  echo "Creazione venv..."
  python3 -m venv .venv
fi

# Installa dipendenze
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt

# Porta: primo argomento (es. ./run.sh 8080), default 5000
PORT="${1:-5000}"

echo ""
echo "✅ Avvio PDF Signer → http://localhost:$PORT"
echo "   (Ctrl+C per uscire)"
echo ""
.venv/bin/python app.py --port "$PORT"
