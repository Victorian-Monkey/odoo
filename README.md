# 🐒 Victorian Monkey - Production Stack

Stack di produzione completo con **n8n**, **Ollama AI**, Traefik, Redis, MinIO e monitoring.

## 📋 Stack Completo

- **n8n** - Workflow automation platform (con metriche Prometheus)
- **Ollama + Open WebUI** - AI/LLM locale con interfaccia web (autenticazione richiesta)
- **Traefik v3.6** - Reverse proxy con SSL automatico (Let's Encrypt)
- **Redis 7** - Cache per n8n
- **Prometheus** - Monitoring e metriche
- **Grafana** - Dashboard e visualizzazione (con dashboard n8n preconfigurata)

## 🚀 Quick Start

### 1. Prerequisiti

- VPS con Docker e Docker Compose installati
- Domini DNS configurati (vedi sotto)
- Minimo 4GB RAM, 2 CPU cores raccomandati (8GB per Ollama con modelli grandi)

### 2. Setup Iniziale

```bash
# Clone del repository
git clone <your-repo-url>
cd vm-odoo

# Esegui lo script di setup
chmod +x setup.sh
./setup.sh
```

Lo script di setup verificherà:
- ✓ Docker e Docker Compose installati
- ✓ Creazione delle directory necessarie
- ✓ Configurazione di Traefik
- ✓ File di configurazione
- ✓ Permessi corretti
- ✓ DNS e firewall

### 3. Configurazione

```bash
# Copia e modifica .env
cp .env.example .env
nano .env
```

#### Variabili CRITICHE da configurare:

**Nel file `.env`:**
```env
# Traefik SSL
ACME_EMAIL=your-email@example.com

# n8n (opzionale - usa PostgreSQL)
N8N_HOST=n8n.victorianmonkey.org
# N8N_DB_HOST=your-postgres-host.com
# N8N_DB_NAME=n8n
# N8N_DB_USER=n8n
# N8N_DB_PASSWORD=your_secure_password

# Ollama WebUI
OLLAMA_WEBUI_SECRET_KEY=generate-with-openssl-rand-hex-32
# Generate with: htpasswd -nb admin yourpassword
OLLAMA_BASIC_AUTH=admin:$$apr1$$xyz$$abc
```

### 4. DNS Configuration

Configura i seguenti record A presso il tuo provider DNS:

```
n8n.victorianmonkey.org          A    YOUR_VPS_IP
ai.victorianmonkey.org           A    YOUR_VPS_IP
grafana.victorianmonkey.org      A    YOUR_VPS_IP
prometheus.victorianmonkey.org   A    YOUR_VPS_IP
```

### 5. Firewall

```bash
# Consenti solo porte necessarie
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 6. Start!

```bash
# Avvia tutti i servizi
docker compose up -d

# Controlla i log
docker compose logs -f n8n

# Verifica lo stato
docker compose ps
```

### 7. Primo Accesso

**n8n:** `https://n8n.victorianmonkey.org`
- Crea il tuo account admin al primo accesso
- Configura workflows e automazioni

**Ollama AI:** `https://ai.victorianmonkey.org`
- Login con credenziali Basic Auth configurate
- Poi crea account nell'interfaccia WebUI
- Scarica modelli: Settings > Models > Pull a model (es: `llama2`, `mistral`)

**Grafana:** `https://grafana.victorianmonkey.org`
- Username: `admin`
- Password: configurata in `.env` (`GF_SECURITY_ADMIN_PASSWORD`)
- Importa dashboard n8n: `monitoring/n8n-dashboard.json`

**Prometheus:** `https://prometheus.victorianmonkey.org`
- Metriche n8n disponibili su `/metrics`
4. Configura il tuo sistema!

## 📁 Struttura Progetto

```
vm-odoo/
├── docker-compose.yml          # Configurazione stack Docker
├── .env.example                # Template variabili d'ambiente
├── .env                        # Tue configurazioni (NON committare!)
├── setup.sh                    # Script setup automatico
├── update.sh                   # Script update automatico
├── README.md                   # Questo file
│
├── traefik/
│   ├── dynamic.yml            # Configurazione dinamica Traefik
│   └── acme.json              # Certificati SSL (auto-generato)
│
├── monitoring/
│   ├── prometheus.yml         # Configurazione Prometheus
│   └── n8n-dashboard.json     # Dashboard Grafana per n8n
│
└── data/                      # Dati persistenti (volumi Docker)
    ├── n8n/                   # Database SQLite e workflows n8n
    ├── ollama/                # Modelli AI Ollama
    ├── ollama-webui/          # Config Open WebUI
    ├── redis/                 # Dati Redis
    ├── prometheus/            # Metriche
    └── grafana/               # Dashboard
```

## 🔒 Sicurezza

### BasicAuth per Monitoring

Genera password per Prometheus e Grafana:

```bash
docker run --rm httpd:alpine htpasswd -nb admin yourpassword
```

Copia l'output e aggiornalo in `traefik/dynamic.yml`:

```yaml
prometheus-auth:
  basicAuth:
    users:
      - "admin:$apr1$..."
```

### Master Password

Il `admin_passwd` in `odoo.conf` e `.env` è **CRITICO**:
- Permette di creare/eliminare database
- Backup e restore
- **NON condividerlo mai**
- Usa una password lunga e complessa

### Firewall

**NON esporre porte interne direttamente:**
- PostgreSQL (5432) - solo da VPS Odoo
- Redis (6379) - solo interno Docker
- MinIO (9000) - solo interno Docker

## 🛠️ Comandi Utili

### Gestione Container

```bash
# Avvia stack
docker compose up -d

# Ferma stack
docker compose down

# Riavvia solo Odoo
docker compose restart odoo-web

# Visualizza log in tempo reale
docker compose logs -f odoo-web

# Visualizza tutti i log
docker compose logs -f

# Status servizi
docker compose ps
```

### n8n Commands

```bash
# Accedi al container n8n
docker exec -it vm-odoo-n8n-1 sh

# Export workflows
docker exec vm-odoo-n8n-1 n8n export:workflow --all --output=/data/backup/

# Import workflows
docker exec vm-odoo-n8n-1 n8n import:workflow --input=/data/backup/workflows.json
```

### Ollama Commands

```bash
# Lista modelli installati
docker exec vm-odoo-ollama-1 ollama list

# Scarica un modello
docker exec vm-odoo-ollama-1 ollama pull llama2

# Rimuovi un modello
docker exec vm-odoo-ollama-1 ollama rm llama2

# Test modello da CLI
docker exec -it vm-odoo-ollama-1 ollama run llama2 "Hello, how are you?"
```

### Backup

```bash
# Backup n8n (SQLite database)
tar -czf n8n_backup_$(date +%Y%m%d).tar.gz data/n8n/

# Backup Ollama models
tar -czf ollama_backup_$(date +%Y%m%d).tar.gz data/ollama/

# Backup Grafana dashboards
tar -czf grafana_backup_$(date +%Y%m%d).tar.gz data/grafana/

# Backup completo
tar -czf vm_stack_backup_$(date +%Y%m%d).tar.gz data/ .env
```

### Restore

```bash
# Restore n8n
tar -xzf n8n_backup_20250116.tar.gz -C ./

# Restore Ollama
tar -xzf ollama_backup_20250116.tar.gz -C ./

# Riavvia servizi dopo restore
docker compose restart n8n ollama
```

### Update da Git

```bash
# Aggiorna il progetto e riavvia servizi
./update.sh

# Lo script farà automaticamente:
# 1. Backup configurazione corrente
# 2. Git pull delle ultime modifiche
# 3. Stash modifiche locali (opzionale)
# 4. Pull nuove immagini Docker
# 5. Restart servizi
# 6. Verifica configurazioni aggiornate
```

## 📊 Monitoring

### Prometheus
- URL: https://prometheus.victorianmonkey.org
- Username: admin (configurato in traefik/dynamic.yml)
- Password: (quella che hai generato)

### Grafana
- URL: https://grafana.victorianmonkey.org
- Username: admin
- Password: (configurato in .env - GF_SECURITY_ADMIN_PASSWORD)

### Log Monitoring

```bash
# Errori n8n
docker compose logs n8n | grep ERROR

# Errori Ollama
docker compose logs ollama ollama-webui | grep -i error

# Traffico Traefik
docker compose logs traefik

# Tutti gli errori
docker compose logs | grep -i error
```

## 🎨 Sviluppo Addons

Vedi la guida completa in [`addons/README.md`](addons/README.md)

### Quick Example

```bash
# Crea nuovo modulo
cd addons
mkdir my_module
cd my_module

# Crea file base
touch __init__.py __manifest__.py
mkdir models views security

# Sviluppa il tuo workflow...
# n8n supporta hot-reload automatico
```

### n8n non si avvia

```bash
# Controlla i log
docker compose logs odoo-web

# Errori comuni:
# - Database non raggiungibile: verifica HOST, USER, PASSWORD in .env
# - Permessi: verifica data/filestore con ls -la
# - Porta occupata: verifica con netstat -tulpn | grep 8069
```

### Certificati SSL non si generano

```bash
# Verifica DNS
dig victorianmonkey.org

# Controlla log Traefik
docker compose logs traefik

# Verifica acme.json permessi
ls -la traefik/acme.json  # Deve essere 600
chmod 600 traefik/acme.json
```

### Database connection failed

```bash
# Testa connessione da VPS
psql -h your-postgres-host -U odoo -d postgres

# Verifica firewall database
# Assicurati che il tuo IP VPS sia whitelisted nel PostgreSQL
```

### Prestazioni lente

```bash
# Aumenta workers in docker-compose.yml
# workers=6 → workers=8 (basato su CPU disponibili)

# Verifica RAM
free -h

# Verifica CPU
top

# Considera di abilitare Redis per cache
```

## 📈 Scaling & Optimization

### Vertical Scaling (stessa VPS)

```yaml
# In docker-compose.yml
odoo-web:
  command: >
    --workers=8  # Aumenta workers
    --max-cron-threads=2
```

### Horizontal Scaling (multiple VPS)

1. Separa `odoo-web` e `odoo-cron` su VPS diverse
2. Usa load balancer davanti a multiple istanze web
3. Condividi `data/filestore` via NFS o S3
4. Usa Redis per sessioni condivise

### Performance Tips

- Abilita Redis per cache
- Usa MinIO per filestore distribuito
- PostgreSQL: aumenta `shared_buffers` e `work_mem`
- Abilita gzip compression in Traefik
- Usa CDN per static assets

## 🔄 Updates

### Update Automatico (Consigliato)

```bash
# Script automatico che fa tutto
./update.sh
```

Lo script `update.sh` esegue automaticamente:
- ✅ Backup della configurazione corrente
- ✅ Git pull delle ultime modifiche
- ✅ Gestione modifiche locali (stash)
- ✅ Pull immagini Docker aggiornate
- ✅ Restart servizi
- ✅ Controllo aggiornamenti configurazione
- ✅ Display log e status

### Update Manuale

#### Update Progetto da Git
```bash
# Backup configurazione
cp .env backups/.env.backup
cp config/odoo.conf backups/odoo.conf.backup

# Pull modifiche
git pull origin main

# Riavvia servizi
docker compose down
docker compose pull
docker compose up -d
```

#### Update Solo Odoo

```bash
# Backup prima!
docker compose down
docker pull odoo:19.0
docker compose up -d

# Update database (se necessario)
docker exec vm-odoo-odoo-web-1 odoo -u all -d your_database --stop-after-init
docker compose restart odoo-web
```

#### Update Altri Servizi

```bash
docker compose pull
docker compose up -d
```

## 📚 Documentazione Utile

- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [Traefik Docs](https://doc.traefik.io/traefik/)
- [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL](https://www.postgresql.org/docs/)

## 🐛 Bug Reports & Support

Per problemi o domande:
- Email: ops@victorianmonkey.org
- Issues: [GitHub Issues](<your-repo-url>/issues)

## 📝 License

Questo setup è rilasciato sotto licenza MIT.

**Nota**: Odoo stesso è sotto LGPL v3.

## 🤝 Contributing

Contributi benvenuti! Per favore:
1. Fork del repository
2. Crea un branch per la feature
3. Commit delle modifiche
4. Push e apri una Pull Request

---

**Made with ❤️ by Victorian Monkey Team**

🐒 Happy Odoo-ing! 🚀