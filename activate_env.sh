#!/bin/bash
echo "Attivazione ambiente virtuale Python..."
source .venv/bin/activate
echo "Ambiente attivato!"
echo "Per disattivare: deactivate"
exec "$SHELL"
