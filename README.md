# Victorian Monkey - Odoo Project

Progetto Odoo configurato per self-hosting con Docker Compose e Dokploy.

## Struttura del Progetto

```
.
├── addons/              # Moduli personalizzati Odoo
├── config/              # File di configurazione Odoo
│   └── odoo.conf       # Configurazione principale Odoo
├── docker-compose.yml   # Configurazione Docker Compose
├── Dockerfile          # Dockerfile personalizzato (opzionale)
├── requirements.txt    # Dipendenze Python
├── env.template        # Template per variabili d'ambiente
└── README.md           # Questo file
```

## Setup con Dokploy

Per una guida dettagliata passo-passo, consulta **[DEPLOY_DOKPLOY.md](DEPLOY_DOKPLOY.md)**.

### Quick Start

1. **Prepara il repository**:
   ```bash
   git add .
   git commit -m "Ready for Dokploy deployment"
   git push
   ```

2. **Crea progetto su Dokploy**:
   - Accedi alla dashboard Dokploy
   - Crea nuovo progetto → Seleziona "Docker Compose"
   - Collega il repository Git
   - Dokploy rileverà automaticamente `docker-compose.yml`

3. **Configura variabili d'ambiente**:
   - `POSTGRES_PASSWORD`: Password sicura per il database
   - `ADMIN_PASSWD`: Password admin Odoo (modifica anche in `config/odoo.conf`)

4. **Deploy**:
   - Clicca "Deploy" → Dokploy eseguirà `docker-compose build && docker-compose up -d`
   - Accedi a Odoo sul dominio configurato o `http://server-ip:8069`

### File Importanti per Dokploy

- ✅ `docker-compose.yml` - Configurazione Docker Compose
- ✅ `Dockerfile` - Build personalizzato con dipendenze
- ✅ `requirements.txt` - Dipendenze Python
- ✅ `config/odoo.conf` - Configurazione Odoo
- ✅ `.gitignore` - Esclude file sensibili

**📖 Per dettagli completi, vedi [DEPLOY_DOKPLOY.md](DEPLOY_DOKPLOY.md)**

## Sviluppo Locale

### Prerequisiti

- Docker e Docker Compose installati
- Git

### Avvio Locale

1. **Clona il repository**:
   ```bash
   git clone <repository-url>
   cd odoo
   ```

2. **Configura le variabili d'ambiente** (opzionale):
   ```bash
   cp env.template .env
   # Modifica .env con i tuoi valori
   ```

3. **Avvia i servizi**:
   ```bash
   docker-compose up -d
   ```

4. **Accedi a Odoo**:
   - Apri il browser su `http://localhost:8069`
   - Crea un nuovo database o seleziona uno esistente

### Comandi Utili

```bash
# Avvia i servizi
docker-compose up -d

# Ferma i servizi
docker-compose down

# Visualizza i log
docker-compose logs -f odoo

# Riavvia un servizio
docker-compose restart odoo

# Accedi al container Odoo
docker-compose exec odoo bash

# Backup del database
docker-compose exec db pg_dump -U odoo postgres > backup.sql
```

## Configurazione

### File di Configurazione

- **`config/odoo.conf.template`**: Template completo di configurazione Odoo
  - **IMPORTANTE**: Prima del primo avvio, copia il template:
    ```bash
    cp config/odoo.conf.template config/odoo.conf
    ```
  - Modifica `config/odoo.conf` e cambia:
    - `admin_passwd` → Password sicura per operazioni database
    - `db_password` → Password sicura per il database PostgreSQL
  - Il file `config/odoo.conf` è in `.gitignore` per sicurezza
  - Aggiusta `workers` in base alle risorse del server (raccomandato: CPU cores * 2 + 1)
  - Configura i limiti di memoria e CPU secondo le tue esigenze
  - Il template include commenti dettagliati per ogni sezione

### Variabili d'Ambiente

Copia `env.template` in `.env` e modifica i valori:

- `ODOO_VERSION`: Versione di Odoo (default: 19)
- `ODOO_PORT`: Porta HTTP (default: 8069)
- `POSTGRES_PASSWORD`: Password del database (cambiala!)
- `ADMIN_PASSWD`: Password admin Odoo (cambiala!)

## Moduli Personalizzati

I moduli personalizzati vanno inseriti nella cartella `addons/`. Ogni modulo deve:

- Seguire la struttura standard di Odoo
- Avere un file `__manifest__.py` valido
- Essere compatibile con la versione di Odoo specificata

## Backup e Restore

### Backup Database

```bash
docker-compose exec db pg_dump -U odoo postgres > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
docker-compose exec -T db psql -U odoo postgres < backup.sql
```

### Backup File

I file di Odoo sono salvati nel volume Docker `odoo-web-data`. Per fare backup:

```bash
docker run --rm -v odoo_odoo-web-data:/data -v $(pwd):/backup alpine tar czf /backup/odoo_files_backup.tar.gz /data
```

## Troubleshooting

### Odoo non si avvia

1. Controlla i log: `docker-compose logs odoo`
2. Verifica che il database sia pronto: `docker-compose logs db`
3. Controlla la configurazione in `config/odoo.conf`

### Problemi di permessi

Se hai problemi con i permessi dei file:

```bash
docker-compose exec odoo chown -R odoo:odoo /var/lib/odoo
```

### Reset completo

```bash
docker-compose down -v  # Rimuove anche i volumi
docker-compose up -d
```

## Note

- La versione di Odoo è impostata a 19.0 nel `docker-compose.yml`
- Per cambiare versione, modifica l'immagine Docker in `docker-compose.yml`
- I dati del database sono persistenti nel volume `odoo-db-data`
- I file di Odoo sono persistenti nel volume `odoo-web-data`
- Per maggiori informazioni, consulta la [documentazione Odoo](https://www.odoo.com/documentation/)
