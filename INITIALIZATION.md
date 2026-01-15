# Inizializzazione Database Odoo

## Problema Comune

Con `list_db=False` e `dbfilter` configurato, Odoo non mostra l'interfaccia di creazione database. Questo è normale per installazioni singole, ma richiede un approccio diverso per l'inizializzazione.

## Soluzioni

### Opzione 1: Abilita temporaneamente LIST_DB (Consigliato)

1. **Modifica la variabile d'ambiente**:
   ```bash
   # In .env o docker-compose.yml
   LIST_DB=True
   ```

2. **Riavvia il container**:
   ```bash
   docker-compose restart odoo
   ```

3. **Accedi a Odoo** e crea il database tramite l'interfaccia web

4. **Dopo la creazione**, ripristina `LIST_DB=False`:
   ```bash
   LIST_DB=False
   docker-compose restart odoo
   ```

### Opzione 2: Crea il Database Manualmente

1. **Crea il database PostgreSQL**:
   ```bash
   docker-compose exec db psql -U odoo -d postgres -c "CREATE DATABASE odoo;"
   ```

2. **Inizializza il database Odoo**:
   ```bash
   docker-compose exec odoo odoo --config=/opt/odoo/config/odoo.conf \
     -d odoo \
     --init=base \
     --stop-after-init \
     --without-demo=all
   ```

3. **Crea l'utente admin** (opzionale, se non creato durante l'init):
   ```bash
   docker-compose exec odoo odoo --config=/opt/odoo/config/odoo.conf \
     -d odoo \
     --stop-after-init \
     shell
   ```
   
   Poi in Python:
   ```python
   env['res.users'].create({
       'name': 'Admin',
       'login': 'admin',
       'password': 'admin',
       'groups_id': [(6, 0, [env.ref('base.group_system').id])]
   })
   ```

### Opzione 3: Usa lo Script di Inizializzazione

Crea uno script `init-db.sh`:

```bash
#!/bin/bash
DB_NAME="${DB_NAME:-odoo}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"

# Crea database
docker-compose exec -T db psql -U odoo -d postgres <<EOF
SELECT 'CREATE DATABASE $DB_NAME'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
EOF

# Inizializza Odoo
docker-compose exec odoo odoo --config=/opt/odoo/config/odoo.conf \
  -d "$DB_NAME" \
  --init=base \
  --stop-after-init \
  --without-demo=all \
  --admin-email="$ADMIN_EMAIL" \
  --admin-password="$ADMIN_PASSWORD"
```

Esegui:
```bash
chmod +x init-db.sh
./init-db.sh
```

## Verifica ADMIN_PASSWD

Se ricevi errori `Access Denied` durante la creazione del database:

1. **Verifica che ADMIN_PASSWD sia impostato**:
   ```bash
   docker-compose exec odoo env | grep ADMIN_PASSWD
   ```

2. **Verifica nel file di configurazione**:
   ```bash
   docker-compose exec odoo cat /opt/odoo/config/odoo.conf | grep admin_passwd
   ```

3. **Assicurati di usare la stessa password** quando crei il database tramite l'interfaccia web

## Configurazione Consigliata per Inizializzazione

Per la prima inizializzazione, usa questa configurazione:

```env
# .env
LIST_DB=True
ODOO_DOMAIN=odoo.victorianmonkey.org
ADMIN_PASSWD=your_secure_password
DB_NAME=odoo
```

Dopo l'inizializzazione, cambia:

```env
LIST_DB=False
```

## Troubleshooting

### Errore "Access Denied"

- Verifica che `ADMIN_PASSWD` nel file di configurazione corrisponda alla password usata nell'interfaccia web
- Controlla i log: `docker-compose logs odoo | grep -i "access\|denied\|password"`

### Database non trovato

- Con `dbfilter` configurato, Odoo cerca un database con nome specifico
- Assicurati che il database esista prima di accedere
- Verifica: `docker-compose exec db psql -U odoo -l`

### Interfaccia di creazione non visibile

- Con `list_db=False`, l'interfaccia non è accessibile
- Abilita temporaneamente `LIST_DB=True` per l'inizializzazione
