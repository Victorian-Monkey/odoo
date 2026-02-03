# AGENT.md – Associazioni Culturali (Odoo 19)

Guida per agenti AI e sviluppatori che lavorano su questo modulo.

---

## 1. Panoramica del progetto

**Modulo:** Associazioni Culturali  
**Versione Odoo:** 19  
**Lingua dominio:** Italiano (etichette, messaggi, documentazione interna)

Modulo per la **gestione del tesseramento** di associazioni culturali: iscrizione online, dati fiscali/soci, pagamento integrato (Odoo Payment), creazione tessera e area riservata “Le mie tessere”.

### Funzionalità principali

- **Backend:** associazioni culturali, piani di tesseramento (annuale solare / calendario), tessere, tesseramenti in attesa di pagamento.
- **Profilo socio (associato):** nome/cognome legale, nome di elezione, codice fiscale (con validazione e opzione “non ho codice fiscale”), data/luogo di nascita, indirizzo, telefono; collegamento a `res.users` (reclama profilo).
- **Website:** form tesseramento (`/tesseramento`), pagamento, success/error; area “Le mie tessere” (`/my/tessere`), rinnovo, reclama profilo.
- **Integrazioni:** `payment`, `mail`, `mass_mailing` (newsletter in fase iscrizione).

### Dipendenze (manifest)

`base`, `website`, `auth_signup`, `payment`, `mail`, `mass_mailing`.

---

## 2. Struttura del modulo

```
associazioni-culturali/
├── __manifest__.py
├── models/
│   ├── associato.py          # Socio: email, nome/cognome legale, nome elezione, CF, data nascita, indirizzo, user_id
│   ├── associazione_culturale.py
│   ├── piano_tesseramento.py
│   ├── tessera.py            # Tessera: piano, associato, associazione, date, stato, invia_email_conferma
│   ├── tesseramento_pending.py
│   ├── payment_transaction.py
│   └── res_users.py          # Estensione res.users (associato_ids, ecc.)
├── controllers/
│   └── tesseramento_controller.py   # Route website, submit, payment return, rinnovo, reclama
├── views/
│   ├── associazioni_culturali_views.xml   # Associato, Associazione, menu
│   ├── tessera_views.xml
│   ├── piano_tesseramento_views.xml
│   └── tesseramento_website_templates.xml # Form tesseramento, my tessere, rinnovo, reclama
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── data/
│   ├── cron_data.xml
│   ├── email_templates.xml
│   └── website_menu.xml
├── migrations/               # Script SQL manuali se necessario (vedi README in migrations/)
└── tests/
```

---

## 3. Convenzioni tecniche Odoo 19

- **Viste lista:** usare `<list>` / `</list>`, non `<tree>`.
- **view_mode:** usare `list,form` (non `tree,form`).
- **Attributi vista:** non usare `attrs` né `states`; usare `invisible="...`", `required="..."`, `readonly="..."` con espressioni di dominio (es. `invisible="stato == 'annullata'"`).
- **Campo calcolato da `id`:** non mettere `id` in `@api.depends`; ricalcolare in `create()` e fare `flush_recordset(['name'])` dopo la creazione se il nome dipende dall’id.
- **Cron:** non usare `numbercall`/`doall`; il codice del cron usare `model._cron_metodo()` (riferimento al modello target).
- **Form website POST:** includere sempre `<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>` nei form che fanno POST verso route con `csrf=True`.

---

## 4. Documentazione Odoo da leggere

Riferimenti ufficiali Odoo 19 (documentation e developer reference):

- **Developer documentation (indice):**  
  https://www.odoo.com/documentation/19.0/developer.html
- **ORM (modelli, campi, API):**  
  https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
- **Viste (XML, list/form/search):**  
  https://www.odoo.com/documentation/19.0/developer/reference/frontend/views.html
- **HTTP / controller (route, request, CSRF):**  
  https://www.odoo.com/documentation/19.0/developer/reference/backend/http.html
- **Website (QWeb, template, assets):**  
  https://www.odoo.com/documentation/19.0/developer/website.html
- **Testing:**  
  https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html
- **Upgrade / migrazioni:**  
  https://www.odoo.com/documentation/19.0/developer/reference/upgrades/upgrade_scripts.html

Sostituire `19.0` con la versione effettiva se diversa (es. 18.0, 20.0).

---

## 5. Prompt ottimizzato per sviluppatore Python / moduli Odoo

Usa il blocco qui sotto come contesto di sistema (o prompt iniziale) per un assistente che deve modificare questo modulo. Adatta lingua e livello di dettaglio se serve.

```markdown
Sei uno sviluppatore Python con esperienza in moduli Odoo. Stai lavorando sul modulo **Associazioni Culturali** per **Odoo 19**.

Contesto progetto:
- Modulo: tesseramento per associazioni culturali (soci, piani, tessere, pagamenti online, area “Le mie tessere”).
- Modelli principali: associato, associazione.culturale, piano.tesseramento, tessera, tesseramento.pending; estensioni su res.users e payment.transaction.
- Stack: Odoo 19, Python 3, XML (viste, QWeb), JavaScript minimo (toggle form website).

Regole tecniche da rispettare:
1. **Odoo 19:** viste lista con `<list>` (non tree); view_mode `list,form`; niente `attrs`/`states` (usare `invisible`, `required`, `readonly` con espressioni).
2. **Compute/store:** non dipendere da `id` in `@api.depends`; se il nome (o altro campo stored) dipende dall’id, calcolarlo in `create()` e fare `flush_recordset`.
3. **Website form POST:** includere sempre il token CSRF (`request.csrf_token()`) nei form che inviano a route con `csrf=True`.
4. **Lingua:** etichette e messaggi utente in italiano; commenti e docstring possono essere in italiano o inglese.
5. **Codice:** stile coerente con il modulo (PEP 8, no abbreviazioni inutili); sollevare `ValidationError`/`UserError` con messaggi chiari quando appropriato.

Prima di modificare:
- Leggere i file coinvolti (modello, controller, vista, template).
- Verificare dipendenze da altri moduli (payment, mail, mass_mailing) e da `res.users`/`res.partner`.
- Per cambi allo schema DB: considerare upgrade del modulo e, se necessario, script in `migrations/` (vedi README in quella cartella).

Riferimenti rapidi:
- ORM e viste: documentazione developer Odoo 19 (orm, views).
- Controller e CSRF: documentazione backend HTTP Odoo 19.
- Website: documentazione website e QWeb Odoo 19.
```

---

## 6. Dove trovare cosa

| Cosa | Dove |
|------|------|
| Modelli backend | `models/*.py` |
| Route website e logica submit/pagamento | `controllers/tesseramento_controller.py` |
| Form e pagine website | `views/tesseramento_website_templates.xml` |
| Viste backend (associato, tessera, piano, associazione) | `views/associazioni_culturali_views.xml`, `tessera_views.xml`, `piano_tesseramento_views.xml` |
| Permessi e gruppi | `security/security.xml`, `security/ir.model.access.csv` |
| Cron, email, menu website | `data/cron_data.xml`, `data/email_templates.xml`, `data/website_menu.xml` |
| Migrazioni DB manuali | `migrations/` (e README in quella cartella) |
| Documentazione funzionale dettagliata | `MODULE_DOCUMENTATION.md` |

---

*Ultimo aggiornamento: 2026-02. Modulo target: Odoo 19.*
