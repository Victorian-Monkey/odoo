#!/bin/bash
# Script per generare odoo.conf dal template usando variabili d'ambiente

set -e

TEMPLATE_FILE="/etc/odoo/odoo.conf.template"
OUTPUT_FILE="/etc/odoo/odoo.conf"

# Verifica che il template esista
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Errore: Template non trovato: $TEMPLATE_FILE"
    exit 1
fi

# Crea la directory se non esiste
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Genera odoo.conf dal template usando envsubst
envsubst '${ADMIN_PASSWD} ${DB_HOST} ${DB_PORT} ${DB_USER} ${DB_PASSWORD} ${DB_NAME} ${ODOO_DOMAIN} ${HTTP_PORT} ${LOG_LEVEL} ${WORKERS} ${PROXY_MODE} ${EMAIL_FROM} ${SMTP_SERVER} ${SMTP_PORT} ${SMTP_SSL} ${SMTP_USER} ${SMTP_PASSWORD} ${DB_MAXCONN}' < "$TEMPLATE_FILE" > "$OUTPUT_FILE.tmp"

# Aggiungi db_name se DB_NAME è impostato
if [ -n "$DB_NAME" ]; then
    # Inserisci db_name dopo db_password
    sed -i "/^db_password = /a db_name = $DB_NAME" "$OUTPUT_FILE.tmp"
fi

# Gestisci ODOO_DOMAIN: se impostato, usa dbfilter e list_db=False
# Se non impostato, usa configurazione multi-database
if [ -n "$ODOO_DOMAIN" ]; then
    # Trova la riga con "; Configurazione database filtering" e inserisci dopo
    sed -i "/^; Configurazione database filtering/a dbfilter = ^${ODOO_DOMAIN}$\nlist_db = False" "$OUTPUT_FILE.tmp"
else
    # Configurazione multi-database
    sed -i "/^; Configurazione database filtering/a dbfilter = ^%d$\nlist_db = True" "$OUTPUT_FILE.tmp"
fi

# Rimuovi righe vuote multiple
sed -i '/^$/N;/^\n$/d' "$OUTPUT_FILE.tmp"

# Sposta il file finale
mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"

# Verifica che il file sia stato creato
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Errore: Impossibile creare $OUTPUT_FILE"
    exit 1
fi

echo "✓ Configurazione generata: $OUTPUT_FILE"

# Mostra un riepilogo delle variabili usate (senza mostrare le password)
echo "Configurazione generata con:"
echo "  - DB_HOST: ${DB_HOST:-db} (default)"
echo "  - DB_PORT: ${DB_PORT:-5432} (default)"
echo "  - DB_USER: ${DB_USER:-odoo} (default)"
echo "  - ODOO_DOMAIN: ${ODOO_DOMAIN:-non impostato (multi-database)}"
echo "  - HTTP_PORT: ${HTTP_PORT:-8069} (default)"
echo "  - LOG_LEVEL: ${LOG_LEVEL:-info} (default)"
echo "  - WORKERS: ${WORKERS:-2} (default)"
echo "  - PROXY_MODE: ${PROXY_MODE:-True} (default)"
