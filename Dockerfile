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
# Installiamo sempre psycopg2-binary per assicurarci che sia disponibile
RUN pip3 install --no-cache-dir --break-system-packages psycopg2-binary && \
    python3 -c "import psycopg2; print('psycopg2 installato:', psycopg2.__version__)"

# Installa gettext-base per envsubst (necessario per generare odoo.conf dal template)
RUN apt-get update && apt-get install -y gettext-base && rm -rf /var/lib/apt/lists/*

# Crea la directory per la configurazione interna (non montata come volume)
RUN mkdir -p /opt/odoo/config && \
    chown -R odoo:odoo /opt/odoo && \
    chmod 755 /opt/odoo/config

# Copia il template di configurazione nel container
COPY config/odoo.conf.template /opt/odoo/config/odoo.conf.template
RUN chown odoo:odoo /opt/odoo/config/odoo.conf.template

# Copia lo script per generare odoo.conf e l'entrypoint
COPY config/generate-odoo-conf.sh /usr/local/bin/generate-odoo-conf.sh
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/generate-odoo-conf.sh /usr/local/bin/docker-entrypoint.sh

# Aggiungi il venv al PATH e assicurati che Python trovi i moduli di sistema
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/usr/local/lib/python3.12/dist-packages:/usr/lib/python3/dist-packages:${PYTHONPATH:-}"

# Cambia utente dopo l'installazione
USER odoo

# Entrypoint personalizzato che genera odoo.conf prima di avviare Odoo
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Il resto della configurazione è gestita tramite docker-compose.yml

