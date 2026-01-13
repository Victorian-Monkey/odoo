# Dockerfile per Odoo personalizzato (opzionale)
# Se hai bisogno di personalizzazioni specifiche, usa questo Dockerfile
# Altrimenti il docker-compose.yml usa l'immagine ufficiale odoo:19

FROM odoo:19

# Installa dipendenze aggiuntive se necessario
USER root
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    gcc \
    g++ \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements personalizzati e installa dipendenze Python in un venv
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# Installa psycopg2-binary nel sistema Python (necessario per script Odoo come wait-for-psql.py)
# che usano direttamente il Python di sistema, non il venv
RUN pip3 install --no-cache-dir --break-system-packages psycopg2-binary

# Aggiungi il venv al PATH per l'utente odoo
ENV PATH="/opt/venv/bin:$PATH"

# Cambia utente dopo l'installazione
USER odoo

# Il resto della configurazione è gestita tramite docker-compose.yml

