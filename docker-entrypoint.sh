#!/bin/bash
# Entrypoint script per Odoo che genera odoo.conf dal template

set -e

echo "=== Generazione configurazione Odoo ==="

# Genera odoo.conf dal template usando variabili d'ambiente
/usr/local/bin/generate-odoo-conf.sh

# Se AUTO_UPDATE_MODULES è impostato, aggiorna i moduli
if [ "${AUTO_UPDATE_MODULES:-False}" = "True" ]; then
    echo "=== Aggiornamento automatico moduli ==="
    
    # Attendi che il database sia pronto
    echo "Attesa database..."
    until PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c '\q' 2>/dev/null; do
        echo "Database non ancora pronto, attesa..."
        sleep 2
    done
    
    echo "Database pronto, aggiornamento moduli..."
    ${ODOO_BIN:-odoo} \
      -c ${ODOO_CONF:-/opt/odoo/config/odoo.conf} \
      -d ${ODOO_DOMAIN} \
      -u all \
      --stop-after-init \
      --http-port=${HTTP_PORT:-8069} || {
        echo "⚠️  Errore durante l'aggiornamento moduli, continuo comunque..."
    }
    echo "✓ Aggiornamento moduli completato"
fi

echo "=== Avvio Odoo ==="

# Esegui il comando originale (passato come argomenti)
exec "$@"
