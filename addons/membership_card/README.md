# Modulo Membership Card per Odoo 19

Modulo completo per la gestione delle membership card di un'associazione italiana.

## Funzionalità

### Gestione Membri
- Anagrafica completa con dati italiani (Codice Fiscale, P.IVA)
- Supporto per membri privati e aziendali
- Gestione indirizzi con province italiane
- Tracciamento scadenze e rinnovi

### Tipi di Membership
- Configurazione flessibile dei tipi di membership
- Durata personalizzabile (in mesi)
- Prezzi configurabili
- Supporto per esenzione IVA
- Validazione Codice Fiscale e P.IVA italiana

### Card di Membership
- Generazione automatica di card con numero univoco
- Barcode e QR Code per verifica
- Gestione card perse/rubate
- Sostituzione card
- Stampa card personalizzabile

### API REST
- Endpoint completi per integrazione frontend
- Supporto CORS per applicazioni web
- Verifica card tramite numero o barcode
- CRUD completo per membri e card

## Installazione

1. Copia il modulo nella cartella `addons/` di Odoo
2. Aggiorna la lista delle app: `Apps > Update Apps List`
3. Cerca "Gestione Membership Card" e installa
4. Il modulo creerà automaticamente 3 tipi di membership di esempio

## Utilizzo

### Creare un Membro

1. Vai su **Membership > Membri**
2. Clicca su **Crea**
3. Compila i dati del membro:
   - Nome completo
   - Email e telefono
   - Indirizzo
   - Codice Fiscale (obbligatorio per alcuni tipi)
   - P.IVA (se azienda)
4. Seleziona il tipo di membership
5. Salva - la card verrà generata automaticamente

### Gestire le Card

- **Stampa Card**: Dalla vista membro o card, clicca su "Stampa Card"
- **Sostituire Card**: Se una card è persa/rubata, usa il pulsante "Sostituisci Card"
- **Rinnovare Membership**: Dalla vista membro, clicca su "Rinnova Membership"

### API REST

Il modulo espone le seguenti API:

#### GET /api/membership/members
Lista tutti i membri
- Parametri: `active_only` (boolean), `membership_type_id` (int)

#### GET /api/membership/members/{id}
Dettagli di un membro specifico

#### POST /api/membership/members
Crea un nuovo membro
- Body JSON con: `name`, `membership_type_id`, `email`, `phone`, etc.

#### GET /api/membership/cards/{card_number}
Verifica una card tramite numero o barcode

#### GET /api/membership/types
Lista tutti i tipi di membership attivi

**Nota**: Le API sono attualmente pubbliche per facilitare lo sviluppo. 
**IMPORTANTE**: In produzione, implementa autenticazione token-based!

## Personalizzazione

### Modificare il Template della Card

Modifica il file `reports/membership_card_template.xml` per personalizzare l'aspetto della card stampata.

### Aggiungere Campi Personalizzati

Puoi estendere i modelli `membership.member`, `membership.type` o `membership.card` per aggiungere campi personalizzati.

## Supporto per Associazioni Italiane

Il modulo include:
- Validazione Codice Fiscale italiano (16 caratteri)
- Validazione P.IVA italiana (11 cifre)
- Supporto per esenzione IVA
- Gestione province italiane
- Formato card con dati italiani

## Licenza

LGPL-3

## Autore

Victorian Monkey

