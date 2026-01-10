# Configurazione Odoo

Questa cartella contiene i file di configurazione per Odoo.

## File

- **`odoo.conf.template`**: Template di configurazione completo con commenti
- **`odoo.conf`**: File di configurazione effettivo (non committato, in `.gitignore`)

## Setup Iniziale

1. **Copia il template**:
   ```bash
   cp config/odoo.conf.template config/odoo.conf
   ```

2. **Modifica le credenziali**:
   ```bash
   nano config/odoo.conf
   # oppure
   vim config/odoo.conf
   ```

3. **Cambia almeno queste impostazioni**:
   - `admin_passwd = CHANGE_THIS_PASSWORD` → Usa una password sicura
   - `db_password = CHANGE_THIS_PASSWORD` → Usa una password sicura

## Configurazione per Docker

Se usi Docker Compose, le credenziali possono essere passate anche tramite variabili d'ambiente nel `docker-compose.yml`:

```yaml
environment:
  - HOST=db
  - USER=odoo
  - PASSWORD=your-secure-password
```

## Configurazione per Dokploy

In Dokploy, configura le variabili d'ambiente nella dashboard del progetto invece di modificare il file direttamente.

## Sicurezza

⚠️ **IMPORTANTE**: 
- Il file `odoo.conf` è in `.gitignore` e NON viene committato
- Non condividere mai il file `odoo.conf` con credenziali reali
- Usa password forti e uniche per ogni ambiente
- In produzione, considera l'uso di variabili d'ambiente o un sistema di gestione segreti

## Personalizzazione

Il template include tutte le opzioni principali. Scommenta e configura le sezioni opzionali secondo le tue esigenze:
- Email (SMTP)
- Proxy mode
- Gevent
- Database connection pool
- Session settings

