#!/bin/bash
# Entrypoint script per Odoo che genera odoo.conf dal template

set -e

echo "=== Generazione configurazione Odoo ==="

# Genera odoo.conf dal template usando variabili d'ambiente
/usr/local/bin/generate-odoo-conf.sh

# Se AUTO_UPDATE_MODULES è impostato, aggiorna i moduli
if [ "${AUTO_UPDATE_MODULES:-False}" = "True" ]; then
    echo "=== Aggiornamento automatico moduli ==="
    
    # Determina il nome del database
    DB_TO_UPDATE="${DB_NAME}"
    
    # Se DB_NAME non è impostato, prova a determinarlo dal dbfilter o usa il primo database disponibile
    if [ -z "$DB_TO_UPDATE" ]; then
        if [ -n "${ODOO_DOMAIN}" ]; then
            # Per installazione singola, il database potrebbe avere un nome basato sul dominio
            # Prova a trovare un database che corrisponde
            DB_TO_UPDATE=$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -tAc "SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres' LIMIT 1" 2>/dev/null || echo "")
        fi
    fi
    
    if [ -n "$DB_TO_UPDATE" ]; then
        echo "Aggiornamento moduli per database: ${DB_TO_UPDATE}"
        
        # Attendi che il database sia pronto
        echo "Attesa database..."
        until PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_TO_UPDATE}" -c '\q' 2>/dev/null; do
            echo "Database non ancora pronto, attesa..."
            sleep 2
        done
        
        echo "Database pronto, aggiornamento moduli..."
        odoo --config=/opt/odoo/config/odoo.conf \
             -u all \
             -d "${DB_TO_UPDATE}" \
             --stop-after-init \
             --log-level="${LOG_LEVEL:-info}" || {
            echo "⚠️  Errore durante l'aggiornamento moduli, continuo comunque..."
        }
        echo "✓ Aggiornamento moduli completato"
    else
        echo "⚠️  Database non specificato, salto l'aggiornamento moduli"
        echo "   Imposta DB_NAME o ODOO_DOMAIN per abilitare l'aggiornamento automatico"
    fi
fi

echo "=== Avvio Odoo ==="

# Esegui il comando originale (passato come argomenti)
exec "$@"
