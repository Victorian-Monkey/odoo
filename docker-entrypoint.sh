#!/bin/bash
# Entrypoint script per Odoo che genera odoo.conf dal template

set -e

echo "=== Generazione configurazione Odoo ==="

# Genera odoo.conf dal template usando variabili d'ambiente
/usr/local/bin/generate-odoo-conf.sh

echo "=== Avvio Odoo ==="

# Esegui il comando originale (passato come argomenti)
exec "$@"
