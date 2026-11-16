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

echo ""
echo "✅ Avvio PDF Signer → http://localhost:5000"
echo "   (Ctrl+C per uscire)"
echo ""
.venv/bin/python app.py
