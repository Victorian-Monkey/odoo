# 🐒 Victorian Monkey - Odoo Community Edition

Stack di produzione completo per **Odoo 19.0 Community Edition** con Traefik, PostgreSQL esterno, Redis, MinIO e monitoring.

## 📋 Stack Completo

- **Odoo 19.0 Community** - ERP/CRM open source
- **Traefik v3.1** - Reverse proxy con SSL automatico (Let's Encrypt)
- **PostgreSQL** - Database esterno (non incluso nel compose)
- **Redis 7** - Cache e sessioni
- **MinIO** - Object storage S3-compatible
- **Prometheus** - Monitoring e metriche
- **Grafana** - Dashboard e visualizzazione

## 🚀 Quick Start

### 1. Prerequisiti

- VPS con Docker e Docker Compose installati
- Database PostgreSQL esterno accessibile
- Domini DNS configurati (vedi sotto)
- Minimo 2GB RAM, 2 CPU cores raccomandati

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

# Copia e modifica odoo.conf
cp conf/odoo.conf.example config/odoo.conf
nano config/odoo.conf
```

#### Variabili CRITICHE da configurare:

**Nel file `.env`:**
```env
# Database esterno
HOST=your-postgres-host.com
USER=odoo
PASSWORD=your_secure_password

# Master password Odoo
ADMIN_PASSWD=your_master_password_here

# Domini
TRAEFIK_HOSTS=Host(`victorianmonkey.org`) || Host(`www.victorianmonkey.org`)

# MinIO
MINIO_ROOT_PASSWORD=your_minio_password
```

**Nel file `config/odoo.conf`:**
```ini
admin_passwd = your_master_password_here
db_host = your-postgres-host.com
db_user = odoo
db_password = your_secure_password
```

### 4. DNS Configuration

Configura i seguenti record A presso il tuo provider DNS:

```
victorianmonkey.org              A    YOUR_VPS_IP
www.victorianmonkey.org          A    YOUR_VPS_IP
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
docker compose logs -f odoo-web

# Verifica lo stato
docker compose ps
```

### 7. Primo Accesso

1. Vai su https://victorianmonkey.org
2. Crea il primo database (usa il master password configurato)
3. Installa i moduli necessari
4. Configura il tuo sistema!

## 📁 Struttura Progetto

```
vm-odoo/
├── docker-compose.yml          # Configurazione stack Docker
├── .env.example                # Template variabili d'ambiente
├── .env                        # Tue configurazioni (NON committare!)
├── setup.sh                    # Script setup automatico
├── README.md                   # Questo file
│
├── addons/                     # I tuoi moduli custom Odoo
│   └── README.md              # Guida sviluppo addons
│
├── config/
│   └── odoo.conf              # Configurazione Odoo
│
├── conf/
│   └── odoo.conf.example      # Template configurazione
│
├── traefik/
│   ├── dynamic.yml            # Configurazione Traefik dinamica
│   └── acme.json              # Certificati SSL (auto-generati)
│
├── monitoring/
│   └── prometheus.yml         # Configurazione Prometheus
│
└── data/                      # Dati persistenti (volumi Docker)
    ├── filestore/             # File Odoo
    ├── redis/                 # Dati Redis
    ├── minio/                 # Object storage
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

### Odoo Commands

```bash
# Accedi al container Odoo
docker exec -it vm-odoo-odoo-web-1 bash

# Update modulo
docker exec -it vm-odoo-odoo-web-1 odoo \
  -u module_name \
  -d your_database \
  --stop-after-init

# Installa modulo
docker exec -it vm-odoo-odoo-web-1 odoo \
  -i module_name \
  -d your_database \
  --stop-after-init

# Lista database
docker exec -it vm-odoo-odoo-web-1 odoo \
  --list-databases

# Shell Odoo (debugging)
docker exec -it vm-odoo-odoo-web-1 odoo shell -d your_database
```

### Backup

```bash
# Backup database (dal tuo PostgreSQL server)
pg_dump -h your-postgres-host -U odoo -F c your_database > backup.dump

# Backup filestore
tar -czf filestore_backup.tar.gz data/filestore/

# Backup completo
./backup.sh  # (da creare)
```

### Restore

```bash
# Restore database
pg_restore -h your-postgres-host -U odoo -d new_database backup.dump

# Restore filestore
tar -xzf filestore_backup.tar.gz -C data/
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
# Errori Odoo
docker compose logs odoo-web | grep ERROR

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

# Sviluppa il tuo modulo...

# Installa in Odoo
docker compose restart odoo-web
# Poi dall'interfaccia Odoo: Apps > Update Apps List > Cerca "my_module"
```

## 🔧 Troubleshooting

### Odoo non si avvia

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