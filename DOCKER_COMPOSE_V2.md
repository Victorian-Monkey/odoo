# 🐳 Docker Compose v2 - Guida Rapida

Questo progetto usa **Docker Compose v2** (sintassi moderna).

## 📋 Differenze Principali

### Comando

| Docker Compose v1 (OLD) | Docker Compose v2 (NEW) |
|------------------------|-------------------------|
| `docker-compose` | `docker compose` |
| (con trattino `-`) | (con spazio) |

### File docker-compose.yml

```yaml
# ❌ Docker Compose v1 (deprecato)
version: "3.9"
services:
  web:
    image: nginx

# ✅ Docker Compose v2 (moderno)
services:
  web:
    image: nginx
```

La riga `version: "x.x"` non è più necessaria in v2!

## 🔄 Comandi Aggiornati

### Operazioni Base

```bash
# Avvia servizi
docker compose up -d

# Ferma servizi
docker compose down

# Riavvia servizi
docker compose restart

# Visualizza status
docker compose ps

# Visualizza log
docker compose logs -f

# Pull immagini
docker compose pull

# Rebuild servizi
docker compose build

# Esegui comando in container
docker compose exec odoo-web bash
```

### Operazioni Avanzate

```bash
# Avvia servizio specifico
docker compose up -d odoo-web

# Scala servizi
docker compose up -d --scale odoo-web=3

# Visualizza configurazione
docker compose config

# Valida file
docker compose config --quiet

# Rimuovi volumi
docker compose down -v

# Forza ricreazione
docker compose up -d --force-recreate
```

## 🚀 Come Verificare la Versione

```bash
# Controlla Docker Compose
docker compose version

# Output esempio:
# Docker Compose version v2.33.1

# Controlla Docker Engine
docker version

# Output esempio:
# Client: Docker Engine - Community
# Version: 27.0.3
```

## 🔧 Installazione Docker Compose v2

Se non hai Docker Compose v2:

### Su Linux

```bash
# Rimuovi vecchia versione (se presente)
sudo apt remove docker-compose

# Docker Compose v2 viene con Docker Engine moderno
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verifica
docker compose version
```

### Su Windows/macOS

Docker Desktop include già Docker Compose v2.

Scarica da: https://www.docker.com/products/docker-desktop

## ⚠️ Se Hai Ancora v1

Se hai ancora `docker-compose` (v1) installato:

```bash
# Crea alias temporaneo
alias docker-compose='docker compose'

# Oppure crea link simbolico (Linux)
sudo ln -s /usr/libexec/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose
```

## 🎯 In Questo Progetto

Tutti gli script sono aggiornati per Docker Compose v2:

- ✅ `setup.sh` - Usa `docker compose`
- ✅ `update.sh` - Usa `docker compose`
- ✅ `README.md` - Tutti i comandi aggiornati
- ✅ `docker-compose.yml` - Nessuna riga `version:`

## 📚 Riferimenti

- [Docker Compose v2 Documentation](https://docs.docker.com/compose/)
- [Migrate to Compose V2](https://docs.docker.com/compose/migrate/)
- [What's New in v2](https://docs.docker.com/compose/compose-v2/)

---

**Nota**: Se vedi errori come "client version is too old", aggiorna Docker Engine e Docker Compose v2!