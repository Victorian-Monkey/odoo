# Configurazione Odoo

Questa cartella contiene i file di configurazione per Odoo.

## File

- **`odoo.conf.template`**: Template di configurazione con variabili d'ambiente
- **`odoo.conf`**: File di configurazione generato automaticamente (NON committato, in `.gitignore`)
- **`generate-odoo-conf.sh`**: Script che genera `odoo.conf` dal template

## Come Funziona

Il file `odoo.conf` viene generato automaticamente all'avvio del container Docker dal template `odoo.conf.template` usando le variabili d'ambiente.

### Processo di Generazione

1. All'avvio del container, lo script `docker-entrypoint.sh` viene eseguito
2. Lo script chiama `generate-odoo-conf.sh`
3. Lo script usa `envsubst` per sostituire le variabili d'ambiente nel template
4. Il file `odoo.conf` viene generato in `/etc/odoo/odoo.conf`
5. Odoo viene avviato con la configurazione generata

## Variabili d'Ambiente

### Obbligatorie

- `ADMIN_PASSWD`: Password per operazioni sul database
- `DB_PASSWORD`: Password del database PostgreSQL

### Opzionali (con default)

- `DB_HOST`: Host del database (default: `db`)
- `DB_PORT`: Porta del database (default: `5432`)
- `DB_USER`: Utente database (default: `odoo`)
- `ODOO_DOMAIN`: Dominio per installazione singola (es: `odoo.victorianmonkey.org`)
  - Se impostato: configura `dbfilter` e `list_db=False`
  - Se non impostato: usa configurazione multi-database
- `HTTP_PORT`: Porta HTTP (default: `8069`)
- `LOG_LEVEL`: Livello di log (default: `info`)
- `WORKERS`: Numero di worker (default: `2`)
- `PROXY_MODE`: Abilita proxy mode (default: `True`)

### Opzionali Avanzate

- `DB_NAME`: Nome database specifico (lascia vuoto per multi-db)
- `EMAIL_FROM`, `SMTP_SERVER`, `SMTP_PORT`, `SMTP_SSL`, `SMTP_USER`, `SMTP_PASSWORD`: Configurazione email
- `DB_MAXCONN`: Database connection pool (default: `64`)

## Configurazione per Docker Compose

Crea un file `.env` nella root del progetto (vedi `../env.template`):

```bash
cp env.template .env
# Modifica .env con i tuoi valori
```

Le variabili in `.env` vengono caricate automaticamente da Docker Compose.

## Configurazione per Dokploy

Configura le variabili d'ambiente nella dashboard di Dokploy:

1. Vai alle impostazioni del progetto
2. Sezione "Environment Variables"
3. Aggiungi tutte le variabili necessarie (vedi `../env.template`)

## Esempio di Configurazione

### Installazione Singola (odoo.victorianmonkey.org)

```env
ADMIN_PASSWD=your_secure_password
DB_PASSWORD=your_db_password
ODOO_DOMAIN=odoo.victorianmonkey.org
PROXY_MODE=True
```

### Installazione Multi-Database

```env
ADMIN_PASSWD=your_secure_password
DB_PASSWORD=your_db_password
# Non impostare ODOO_DOMAIN per abilitare multi-database
PROXY_MODE=True
```

## Troubleshooting

### Il file odoo.conf non viene generato

1. Verifica che lo script `generate-odoo-conf.sh` sia eseguibile
2. Controlla i log del container: `docker logs odoo-odoo-1`
3. Verifica che il template esista: `docker exec odoo-odoo-1 ls -la /etc/odoo/odoo.conf.template`

### Variabili d'ambiente non vengono sostituite

1. Verifica che le variabili siano impostate: `docker exec odoo-odoo-1 env | grep DB_`
2. Controlla che il formato sia corretto: `${VAR_NAME:-default}`
3. Verifica che `envsubst` sia installato nel container

### Configurazione non corretta

1. Verifica il file generato: `docker exec odoo-odoo-1 cat /etc/odoo/odoo.conf`
2. Controlla i log di Odoo per errori di configurazione
3. Riavvia il container per rigenerare la configurazione

## Modifiche al Template

Se modifichi `odoo.conf.template`:

1. **Non committare mai** `odoo.conf` (è già in `.gitignore`)
2. Testa le modifiche localmente prima di fare push
3. Documenta le nuove variabili d'ambiente in questo README
4. Aggiorna `env.template` se necessario

## Sicurezza

⚠️ **IMPORTANTE**: 
- Il file `odoo.conf` contiene password in chiaro e NON viene committato
- Usa sempre password forti e uniche per ogni ambiente
- Non condividere mai il file `odoo.conf` generato
- In produzione, usa un sistema di gestione segreti (es: Docker secrets, Kubernetes secrets)
