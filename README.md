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

### Prerequisiti

1. Server con Docker e Docker Compose installati
2. Dokploy installato e configurato sul server
3. Accesso SSH al server (se necessario)

### Deployment su Dokploy

1. **Prepara il repository**:
   - Assicurati che il repository sia su GitHub/GitLab
   - Verifica che tutti i file siano committati

2. **Configura su Dokploy**:
   - Accedi alla dashboard Dokploy
   - Crea un nuovo progetto
   - Seleziona "Docker Compose" come tipo di deployment
   - Collega il repository Git
   - Dokploy rileverà automaticamente il `docker-compose.yml`

3. **Configura le variabili d'ambiente** (opzionale):
   - Crea un file `.env` basato su `env.template`
   - Oppure configura le variabili direttamente in Dokploy
   - **IMPORTANTE**: Cambia `ADMIN_PASSWD` con una password sicura!

4. **Deploy**:
   - Dokploy eseguirà `docker-compose up -d`
   - I servizi saranno disponibili su `http://your-domain:8069`

### Configurazione Domini

Per configurare un dominio personalizzato in Dokploy:

1. Vai alle impostazioni del progetto
2. Aggiungi il dominio desiderato
3. Dokploy configurerà automaticamente il reverse proxy

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

- **`config/odoo.conf`**: Configurazione principale di Odoo
  - Modifica `admin_passwd` per cambiare la password admin
  - Aggiusta `workers` in base alle risorse del server
  - Configura i limiti di memoria e CPU

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
