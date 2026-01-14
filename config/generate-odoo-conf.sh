#!/bin/bash
# Script per generare odoo.conf dal template usando variabili d'ambiente

set -e

# Cerca il template in diverse posizioni (prima quella interna, poi quella montata)
TEMPLATE_FILE=""
for path in "/opt/odoo/config/odoo.conf.template" "/etc/odoo/odoo.conf.template"; do
    if [ -f "$path" ]; then
        TEMPLATE_FILE="$path"
        break
    fi
done

# Usa sempre una directory interna (non montata come volume) per il file generato
OUTPUT_FILE="/opt/odoo/config/odoo.conf"
TEMP_FILE="/tmp/odoo.conf.tmp"

# Verifica che il template esista
if [ -z "$TEMPLATE_FILE" ] || [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Errore: Template non trovato. Cercato in:"
    echo "  - /opt/odoo/config/odoo.conf.template"
    echo "  - /etc/odoo/odoo.conf.template"
    exit 1
fi

echo "Usando template: $TEMPLATE_FILE"

# Crea la directory di output (sempre scrivibile perché interna al container)
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Copia il template nel file temporaneo
cp "$TEMPLATE_FILE" "$TEMP_FILE"

# Sostituisci le variabili con i loro valori (gestendo i default)
# Usa sed per sostituire ${VAR:-default} con il valore della variabile o il default
sed -i "s|\${ADMIN_PASSWD:-admin}|${ADMIN_PASSWD:-admin}|g" "$TEMP_FILE"
sed -i "s|\${DB_HOST:-db}|${DB_HOST:-db}|g" "$TEMP_FILE"
sed -i "s|\${DB_PORT:-5432}|${DB_PORT:-5432}|g" "$TEMP_FILE"
sed -i "s|\${DB_USER:-odoo}|${DB_USER:-odoo}|g" "$TEMP_FILE"
sed -i "s|\${DB_PASSWORD:-odoo}|${DB_PASSWORD:-odoo}|g" "$TEMP_FILE"
sed -i "s|\${HTTP_PORT:-8069}|${HTTP_PORT:-8069}|g" "$TEMP_FILE"
sed -i "s|\${LOG_LEVEL:-info}|${LOG_LEVEL:-info}|g" "$TEMP_FILE"
sed -i "s|\${WORKERS:-2}|${WORKERS:-2}|g" "$TEMP_FILE"
sed -i "s|\${PROXY_MODE:-True}|${PROXY_MODE:-True}|g" "$TEMP_FILE"

# Sostituisci variabili senza default (se non impostate, rimuovi la riga o lascia vuoto)
if [ -n "$ODOO_DOMAIN" ]; then
    sed -i "s|\${ODOO_DOMAIN}|${ODOO_DOMAIN}|g" "$TEMP_FILE"
fi
if [ -n "$DB_NAME" ]; then
    sed -i "s|\${DB_NAME}|${DB_NAME}|g" "$TEMP_FILE"
fi

# Rimuovi eventuali righe con sintassi errata rimaste (es: ${VAR:-default} non sostituite)
sed -i '/\${[A-Z_]*:-/d' "$TEMP_FILE"
sed -i '/\${[A-Z_]*}/d' "$TEMP_FILE"

# Aggiungi db_name se DB_NAME è impostato
if [ -n "$DB_NAME" ]; then
    # Inserisci db_name dopo db_password
    sed -i "/^db_password = /a db_name = $DB_NAME" "$TEMP_FILE"
fi

# Rimuovi eventuali righe dbfilter e list_db esistenti (per evitare duplicati)
sed -i '/^dbfilter = /d' "$TEMP_FILE"
sed -i '/^list_db = /d' "$TEMP_FILE"

# Gestisci ODOO_DOMAIN: se impostato, usa dbfilter e list_db=False
# Se non impostato, usa configurazione multi-database
if [ -n "$ODOO_DOMAIN" ]; then
    # Trova la riga con "; Configurazione database filtering" e inserisci dopo
    sed -i "/^; Configurazione database filtering/a dbfilter = ^${ODOO_DOMAIN}$\nlist_db = False" "$TEMP_FILE"
else
    # Configurazione multi-database
    sed -i "/^; Configurazione database filtering/a dbfilter = ^%d$\nlist_db = True" "$TEMP_FILE"
fi

# Rimuovi righe vuote multiple
sed -i '/^$/N;/^\n$/d' "$TEMP_FILE"

# Copia il file finale nella directory interna (sempre scrivibile)
cp "$TEMP_FILE" "$OUTPUT_FILE"
rm -f "$TEMP_FILE"

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
