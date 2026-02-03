# Migrazioni

Se dopo il deploy su staging/produzione compare l’errore:

`column tessera.invia_email_conferma does not exist`

1. **Soluzione consigliata:** fare l’**Upgrade del modulo** da Interfaccia Odoo:
   - App → Cerca "Associazioni Culturali" → menu a tre puntini → **Aggiorna**.

2. **Se non puoi usare l’Upgrade:** esegui a mano lo script SQL della versione corrispondente, ad es.:
   - `migrations/1.0.1/add_tessera_invia_email_conferma.sql`
   - Esempio: `psql -U odoo -d nome_database -f migrations/1.0.1/add_tessera_invia_email_conferma.sql`

Poi riavvia il server Odoo se necessario.
