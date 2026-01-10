# Dockerfile per Odoo personalizzato (opzionale)
# Se hai bisogno di personalizzazioni specifiche, usa questo Dockerfile
# Altrimenti il docker-compose.yml usa l'immagine ufficiale odoo:19

FROM odoo:19

# Installa dipendenze aggiuntive se necessario
USER root
RUN apt-get update && apt-get install -y \
    python3-pil \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
USER odoo

# Copia requirements personalizzati e installa dipendenze Python
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Il resto della configurazione è gestita tramite docker-compose.yml

