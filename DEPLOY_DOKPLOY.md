# Guida Deployment su Dokploy

Questa guida ti aiuterà a deployare il progetto Odoo su Dokploy.

## Prerequisiti

1. **Server con Dokploy installato**
   - Dokploy deve essere già installato e configurato sul tuo server
   - Accesso alla dashboard Dokploy

2. **Repository Git**
   - Il progetto deve essere su GitHub, GitLab o un altro repository Git
   - Il repository deve essere accessibile da Dokploy

3. **Docker e Docker Compose**
   - Dokploy richiede Docker e Docker Compose sul server

## Passo 1: Prepara il Repository

Assicurati che tutti i file necessari siano committati:

```bash
git add .
git commit -m "Preparazione per deployment Dokploy"
git push
```

File importanti che devono essere presenti:
- ✅ `docker-compose.yml`
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ `config/odoo.conf`
- ✅ `addons/` (con i moduli personalizzati)

## Passo 2: Crea il Progetto su Dokploy

1. **Accedi alla Dashboard Dokploy**
   - Apri il browser e vai all'URL del tuo server Dokploy
   - Effettua il login

2. **Crea un Nuovo Progetto**
   - Clicca su "New Project" o "Nuovo Progetto"
   - Inserisci un nome per il progetto (es: "odoo-victorian-monkey")

3. **Seleziona il Tipo di Deployment**
   - Scegli **"Docker Compose"** come tipo di deployment
   - Dokploy rileverà automaticamente il file `docker-compose.yml`

4. **Collega il Repository Git**
   - Seleziona il tuo provider Git (GitHub, GitLab, etc.)
   - Autorizza l'accesso se richiesto
   - Seleziona il repository del progetto
   - Scegli il branch (solitamente `main` o `master`)

## Passo 3: Configura le Variabili d'Ambiente

Dokploy permette di configurare variabili d'ambiente. Crea un file `.env` o configura le variabili nella dashboard:

### Variabili Consigliate

```env
# Database
POSTGRES_DB=odoo
POSTGRES_USER=odoo
POSTGRES_PASSWORD=<password-sicura>

# Odoo Admin
ADMIN_PASSWD=<password-admin-sicura>

# Opzionali
ODOO_VERSION=19
ODOO_PORT=8069
```

**IMPORTANTE**: 
- Cambia `POSTGRES_PASSWORD` con una password sicura
- Cambia `ADMIN_PASSWD` con una password sicura per Odoo
- Non committare il file `.env` nel repository (è già in `.gitignore`)

### Configurazione in Dokploy

1. Vai alle impostazioni del progetto
2. Sezione "Environment Variables"
3. Aggiungi le variabili necessarie
4. Oppure carica un file `.env`

## Passo 4: Configura il Dominio

1. **Aggiungi un Dominio**
   - Vai alle impostazioni del progetto
   - Sezione "Domains" o "Domini"
   - Aggiungi il dominio desiderato (es: `odoo.tuosito.com`)
   - Dokploy configurerà automaticamente il reverse proxy

2. **Configura SSL**
   - Dokploy può configurare automaticamente Let's Encrypt
   - Abilita SSL/TLS per il dominio

## Passo 5: Deploy

1. **Avvia il Deployment**
   - Clicca su "Deploy" o "Deploy Now"
   - Dokploy eseguirà:
     ```bash
     docker-compose build
     docker-compose up -d
     ```

2. **Monitora il Deployment**
   - Vedi i log in tempo reale nella dashboard
   - Verifica che tutti i servizi si avviino correttamente

3. **Verifica lo Stato**
   - Controlla che i container siano in esecuzione:
     - `odoo` (servizio principale)
     - `db` (PostgreSQL)

## Passo 6: Configurazione Iniziale Odoo

1. **Accedi a Odoo**
   - Apri il browser sul dominio configurato o sull'IP del server
   - Porta 8069 se non hai configurato un dominio

2. **Crea il Database**
   - Segui il wizard di configurazione iniziale
   - Inserisci i dati dell'admin
   - Seleziona i moduli da installare

3. **Installa i Moduli Personalizzati**
   - Vai su **Apps > Update Apps List**
   - Cerca e installa:
     - "Gestione Membership Card"
     - "POS Restaurant Web Menu"

## Passo 7: Configurazione Post-Deployment

### Aggiorna la Password Admin in Odoo

Modifica il file `config/odoo.conf` o usa le variabili d'ambiente:

```bash
# Nel container Odoo
docker-compose exec odoo bash
# Modifica /etc/odoo/odoo.conf
admin_passwd = <tua-password-sicura>
```

### Backup Automatici

Configura backup regolari del database:

```bash
# Script di backup (puoi aggiungerlo come cron job in Dokploy)
docker-compose exec db pg_dump -U odoo odoo > backup_$(date +%Y%m%d).sql
```

## Troubleshooting

### I container non si avviano

1. **Controlla i Log**
   ```bash
   # Nella dashboard Dokploy o via SSH
   docker-compose logs odoo
   docker-compose logs db
   ```

2. **Verifica le Variabili d'Ambiente**
   - Assicurati che tutte le variabili siano configurate correttamente

3. **Verifica i Permessi**
   - Assicurati che Docker abbia i permessi necessari

### Odoo non è accessibile

1. **Verifica le Porte**
   - Controlla che la porta 8069 sia esposta
   - Verifica il firewall del server

2. **Verifica il Reverse Proxy**
   - Se usi un dominio, verifica la configurazione del reverse proxy in Dokploy

### Errori di Dipendenze Python

1. **Ricostruisci l'Immagine**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Verifica requirements.txt**
   - Assicurati che tutte le dipendenze siano elencate

### Database Connection Error

1. **Verifica le Credenziali**
   - Controlla `POSTGRES_USER` e `POSTGRES_PASSWORD`
   - Verifica che corrispondano in `config/odoo.conf`

2. **Attendi il Database**
   - Il servizio Odoo aspetta che il database sia pronto (healthcheck)

## Comandi Utili

### Accesso ai Container

```bash
# Accedi al container Odoo
docker-compose exec odoo bash

# Accedi al container Database
docker-compose exec db psql -U odoo odoo
```

### Riavvia i Servizi

```bash
# Riavvia Odoo
docker-compose restart odoo

# Riavvia tutto
docker-compose restart
```

### Visualizza i Log

```bash
# Log di Odoo
docker-compose logs -f odoo

# Log del Database
docker-compose logs -f db

# Log di tutto
docker-compose logs -f
```

### Backup e Restore

```bash
# Backup database
docker-compose exec db pg_dump -U odoo odoo > backup.sql

# Restore database
docker-compose exec -T db psql -U odoo odoo < backup.sql
```

## Aggiornamenti Futuri

Quando aggiorni il codice:

1. **Push al Repository**
   ```bash
   git add .
   git commit -m "Aggiornamento"
   git push
   ```

2. **Redeploy su Dokploy**
   - Dokploy può essere configurato per auto-deploy su push
   - Oppure clicca manualmente su "Redeploy"

3. **Ricostruisci se necessario**
   - Se hai modificato il Dockerfile o requirements.txt, Dokploy ricostruirà automaticamente

## Note Importanti

- ⚠️ **Sicurezza**: Cambia sempre le password di default
- ⚠️ **Backup**: Configura backup regolari del database
- ⚠️ **Monitoraggio**: Monitora i log per problemi
- ⚠️ **Aggiornamenti**: Mantieni Odoo e i moduli aggiornati
- ⚠️ **SSL**: Usa sempre HTTPS in produzione

## Supporto

Per problemi specifici di Dokploy, consulta la [documentazione ufficiale di Dokploy](https://dokploy.com/docs).

Per problemi con Odoo, consulta la [documentazione Odoo](https://www.odoo.com/documentation/).

