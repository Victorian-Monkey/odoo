#!/usr/bin/env bash
#
# odoovcloud.load.sh
# Wipe e reinstall: rimuove i moduli gestiti (anche quelli non più in modules.conf),
# poi clona ogni repo da modules.conf in /tmp e copia in ./addons/<modulo>.
#
# Formato modules.conf (una riga per modulo):
#   modulo=https://gitlab.com/moduli/esempio.git#master
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULES_CONF="${1:-${SCRIPT_DIR}/modules.conf}"
ADDONS_DIR="${SCRIPT_DIR}/addons"
MANAGED_LIST="${ADDONS_DIR}/.odoovcloud_managed"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"

if [[ ! -f "$MODULES_CONF" ]]; then
  echo "Errore: file non trovato: $MODULES_CONF"
  exit 1
fi

mkdir -p "$ADDONS_DIR"

# --- Fase 1: raccogli moduli correnti da modules.conf ---
current_moduli=()
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
  [[ "$line" =~ ^([^=]+)=(.+)$ ]] || continue
  modulo="${BASH_REMATCH[1]//[[:space:]]/}"
  url_ref="${BASH_REMATCH[2]}"
  [[ -z "$modulo" || -z "${url_ref//[[:space:]]/}" ]] && continue
  current_moduli+=( "$modulo" )
done < "$MODULES_CONF"

# --- Fase 2: wipe — rimuovi moduli non più in config (orphan) ---
if [[ -f "$MANAGED_LIST" ]]; then
  while IFS= read -r prev || [[ -n "$prev" ]]; do
    prev="${prev//[[:space:]]/}"
    [[ -z "$prev" ]] && continue
    if [[ ! " ${current_moduli[*]} " =~ " ${prev} " ]]; then
      if [[ -d "${ADDONS_DIR:?}/$prev" ]]; then
        echo "Rimozione (non più in config): $prev"
        rm -rf "${ADDONS_DIR:?}/$prev"
      fi
    fi
  done < "$MANAGED_LIST"
fi

# --- Fase 3: wipe e reinstall per ogni modulo in modules.conf ---
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

  if [[ "$line" =~ ^([^=]+)=(.+)$ ]]; then
    modulo="${BASH_REMATCH[1]}"
    url_ref="${BASH_REMATCH[2]}"
  else
    echo "Riga ignorata (formato non valido): $line"
    continue
  fi

  if [[ "$url_ref" =~ ^(.+)#([^#]+)$ ]]; then
    url="${BASH_REMATCH[1]}"
    ref="${BASH_REMATCH[2]}"
  else
    url="$url_ref"
    ref="master"
  fi

  modulo="${modulo//[[:space:]]/}"
  url="${url//[[:space:]]/}"
  ref="${ref//[[:space:]]/}"

  [[ -z "$modulo" || -z "$url" ]] && continue

  # Wipe
  if [[ -d "${ADDONS_DIR:?}/$modulo" ]]; then
    echo "Wipe: $modulo"
    rm -rf "${ADDONS_DIR:?}/$modulo"
  fi

  tmp_dir="/tmp/odoo_${modulo}_${TIMESTAMP}"

  echo "=== $modulo (ref: $ref) ==="
  echo "  Clone in $tmp_dir ..."
  git clone --depth 1 --branch "$ref" "$url" "$tmp_dir"

  echo "  Copia in $ADDONS_DIR/$modulo (solo file, senza .git) ..."
  cp -a "$tmp_dir" "$ADDONS_DIR/$modulo"
  rm -rf "$ADDONS_DIR/$modulo/.git"
  rm -rf "$tmp_dir"

  echo "  OK."
done < "$MODULES_CONF"

# --- Salva lista moduli gestiti per il prossimo wipe ---
printf '%s\n' "${current_moduli[@]}" > "$MANAGED_LIST"

echo "Fatto."
