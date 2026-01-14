# Configurazione Reverse Proxy e Cloudflare per Odoo

## Problema Risolto

L'errore `KeyError: 'ir.http'` si verifica quando:
1. Il database Odoo non è stato ancora inizializzato
2. Il reverse proxy non passa correttamente gli header HTTP necessari
3. Il `dbfilter` non corrisponde correttamente al dominio

## Configurazione Odoo

Nel file `config/odoo.conf` sono state applicate le seguenti modifiche:

1. **`proxy_mode = True`**: Abilita la modalità proxy per gestire correttamente gli header del reverse proxy
2. **`dbfilter` commentato**: Permette la selezione del database quando si accede tramite reverse proxy

### Se usi un dominio specifico

Se vuoi usare un `dbfilter` con un dominio specifico, decommenta e configura:

```ini
dbfilter = ^yourdomain\.com$
```

## Configurazione Reverse Proxy (Nginx)

Il reverse proxy deve passare i seguenti header HTTP:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts per operazioni lunghe
        proxy_read_timeout 1200s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 1200s;
        
        # Buffer settings
        proxy_buffering off;
    }
    
    # WebSocket support (per longpolling)
    location /longpolling {
        proxy_pass http://localhost:8072;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Configurazione Cloudflare

### SSL/TLS
- Imposta la modalità SSL/TLS su **"Full"** o **"Full (strict)"**
- Non usare "Flexible" perché Odoo richiede HTTPS end-to-end

### Headers da preservare
Assicurati che Cloudflare preservi questi header:
- `Host`
- `X-Forwarded-For`
- `X-Forwarded-Proto`
- `X-Forwarded-Host`

### Page Rules (opzionale)
Crea una Page Rule per il tuo dominio Odoo:
- **URL**: `yourdomain.com/*`
- **Settings**: 
  - Cache Level: Bypass (Odoo gestisce la cache internamente)
  - Security Level: Medium

## Inizializzazione Database

Dopo aver configurato il reverse proxy:

1. Accedi a Odoo tramite il dominio configurato
2. Dovresti vedere la pagina di selezione/creazione database
3. Crea un nuovo database o seleziona uno esistente
4. Completa la configurazione iniziale

## Troubleshooting

### Errore `KeyError: 'ir.http'`
- **Causa**: Database non inizializzato
- **Soluzione**: Accedi direttamente a Odoo (bypassando il reverse proxy) per inizializzare il database, oppure verifica che `list_db = True` sia configurato

### Odoo non riconosce il dominio
- **Causa**: Header `Host` non passato correttamente
- **Soluzione**: Verifica che il reverse proxy passi `proxy_set_header Host $host;`

### Problemi con WebSocket/Longpolling
- **Causa**: Reverse proxy non configurato per WebSocket
- **Soluzione**: Aggiungi la configurazione `/longpolling` come mostrato sopra

### Errori 502 Bad Gateway
- **Causa**: Timeout troppo brevi
- **Soluzione**: Aumenta i timeout nel reverse proxy (vedi configurazione Nginx sopra)

## Verifica Configurazione

Dopo la configurazione, verifica che:

1. Gli header HTTP siano passati correttamente:
   ```bash
   curl -H "Host: yourdomain.com" http://localhost:8069/web/database/selector
   ```

2. Il database sia accessibile:
   ```bash
   docker exec odoo-db-1 psql -U odoo -d postgres -c "\l"
   ```

3. I log di Odoo non mostrino errori:
   ```bash
   docker logs odoo-odoo-1 --tail 50
   ```

## Note Importanti

- **Sicurezza**: Cambia `admin_passwd` in produzione
- **Performance**: Aumenta `workers` in base alle risorse del server
- **SSL**: Usa sempre HTTPS in produzione
- **Backup**: Configura backup regolari del database
