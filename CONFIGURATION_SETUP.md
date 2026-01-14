# Setup Configurazione Odoo con Variabili d'Ambiente

## Panoramica

Il sistema di configurazione Odoo è stato aggiornato per utilizzare variabili d'ambiente invece di file di configurazione hardcoded. Il file `odoo.conf` viene generato automaticamente all'avvio del container dal template `config/odoo.conf.template`.

## ✅ Vantaggi

- ✅ **Sicurezza**: Nessuna password committata nel repository
- ✅ **Flessibilità**: Configurazione diversa per ogni ambiente (dev, staging, prod)
- ✅ **Semplicità**: Un solo template, configurazione tramite variabili
- ✅ **Dokploy-ready**: Perfetto per deployment su Dokploy

## 📁 File Coinvolti

### File Template (committati)
- `config/odoo.conf.template` - Template di configurazione
- `config/generate-odoo-conf.sh` - Script di generazione
- `docker-entrypoint.sh` - Entrypoint del container
- `Dockerfile` - Aggiornato per includere gli script
- `env.template` - Template delle variabili d'ambiente

### File Generati (NON committati)
- `config/odoo.conf` - Generato automaticamente (in `.gitignore`)
- `.env` - File locale con variabili (in `.gitignore`)

## 🚀 Setup Rapido

### 1. Per Docker Compose Locale

```bash
# Copia il template delle variabili
cp env.template .env

# Modifica .env con i tuoi valori
nano .env

# Avvia i container
docker-compose up -d
```

Il file `odoo.conf` verrà generato automaticamente all'avvio.

### 2. Per Dokploy

1. **Configura le variabili d'ambiente nella dashboard Dokploy**
   - Vai alle impostazioni del progetto
   - Sezione "Environment Variables"
   - Aggiungi tutte le variabili necessarie (vedi `env.template`)

2. **Deploy**
   - Dokploy genererà automaticamente `odoo.conf` all'avvio

## 📝 Variabili d'Ambiente

### Obbligatorie

```env
ADMIN_PASSWD=your_secure_password
DB_PASSWORD=your_db_password
```

### Opzionali (con default)

```env
# Database
DB_HOST=db                    # default: db
DB_PORT=5432                  # default: 5432
DB_USER=odoo                  # default: odoo
DB_NAME=                      # Opzionale: nome database specifico

# Odoo
ODOO_DOMAIN=odoo.victorianmonkey.org  # Se impostato: installazione singola
HTTP_PORT=8069                # default: 8069
LOG_LEVEL=info                # default: info
WORKERS=2                     # default: 2
PROXY_MODE=True               # default: True
```

### Esempio Completo

```env
# Database
POSTGRES_DB=odoo
POSTGRES_USER=odoo
POSTGRES_PASSWORD=secure_db_password_123
DB_HOST=db
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=secure_db_password_123

# Odoo
ADMIN_PASSWD=secure_admin_password_456
ODOO_DOMAIN=odoo.victorianmonkey.org
HTTP_PORT=8069
LOG_LEVEL=info
WORKERS=2
PROXY_MODE=True
```

## 🔧 Come Funziona

1. **All'avvio del container**:
   - `docker-entrypoint.sh` viene eseguito
   - Chiama `generate-odoo-conf.sh`
   - Lo script legge `odoo.conf.template`
   - Sostituisce le variabili d'ambiente usando `envsubst`
   - Gestisce condizioni speciali (ODOO_DOMAIN, DB_NAME)
   - Genera `odoo.conf` in `/etc/odoo/odoo.conf`
   - Avvia Odoo con la configurazione generata

2. **Gestione Condizioni**:
   - Se `ODOO_DOMAIN` è impostato → installazione singola (`dbfilter` + `list_db=False`)
   - Se `ODOO_DOMAIN` non è impostato → multi-database (`dbfilter = ^%d$` + `list_db=True`)
   - Se `DB_NAME` è impostato → aggiunge `db_name = ...`

## 🧪 Test Locale

```bash
# Testa la generazione della configurazione
docker-compose build odoo
docker-compose run --rm odoo /usr/local/bin/generate-odoo-conf.sh

# Verifica il file generato
docker-compose exec odoo cat /etc/odoo/odoo.conf
```

## 🔍 Verifica Configurazione

```bash
# Controlla le variabili d'ambiente nel container
docker-compose exec odoo env | grep -E "(DB_|ODOO_|ADMIN_)"

# Verifica il file generato
docker-compose exec odoo cat /etc/odoo/odoo.conf

# Controlla i log per vedere la configurazione usata
docker-compose logs odoo | grep "Configurazione generata"
```

## ⚠️ Note Importanti

1. **Password**: Cambia sempre le password di default prima di usare in produzione
2. **Sincronizzazione**: `DB_PASSWORD` e `POSTGRES_PASSWORD` devono corrispondere
3. **Dominio**: `ODOO_DOMAIN` deve corrispondere al dominio configurato nel reverse proxy
4. **Git**: `odoo.conf` è in `.gitignore` - non committarlo mai
5. **Modifiche**: Se modifichi il template, ricostruisci l'immagine Docker

## 🐛 Troubleshooting

### Il file odoo.conf non viene generato

```bash
# Verifica che lo script esista
docker-compose exec odoo ls -la /usr/local/bin/generate-odoo-conf.sh

# Controlla i log dell'entrypoint
docker-compose logs odoo | grep "Generazione configurazione"
```

### Variabili non vengono sostituite

```bash
# Verifica che le variabili siano impostate
docker-compose exec odoo env | grep DB_HOST

# Controlla che envsubst sia installato
docker-compose exec odoo which envsubst
```

### Configurazione errata

```bash
# Rigenera la configurazione
docker-compose restart odoo

# Verifica il file generato
docker-compose exec odoo cat /etc/odoo/odoo.conf
```

## 📚 Documentazione Aggiuntiva

- `config/README.md` - Documentazione dettagliata della configurazione
- `DEPLOY_DOKPLOY.md` - Guida deployment su Dokploy
- `REVERSE_PROXY_SETUP.md` - Configurazione reverse proxy

## 🔄 Migrazione da Configurazione Vecchia

Se hai già un file `odoo.conf` esistente:

1. **Estrai i valori** dal file esistente
2. **Crea `.env`** con le variabili corrispondenti
3. **Rimuovi** `config/odoo.conf` (verrà rigenerato)
4. **Riavvia** i container

Il sistema genererà automaticamente la nuova configurazione.
