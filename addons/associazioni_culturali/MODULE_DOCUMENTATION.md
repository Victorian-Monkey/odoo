# Documentazione Modulo Associazioni Culturali

## Panoramica

Il modulo **Associazioni Culturali** gestisce il tesseramento online per associazioni culturali, integrando:
- Gestione associazioni culturali
- Piani di tesseramento (annuale solare o calendario)
- Tessere per utenti
- Pagamento online integrato
- Vista utente per gestire le proprie tessere

## Architettura del Modulo

### Modelli Principali

#### 1. **Associazione Culturale** (`associazione.culturale`)
- Collegata a un'azienda (`res.partner`)
- Gestisce informazioni anagrafiche e fiscali
- Relazione One2many con tessere

#### 2. **Piano Tesseramento** (`piano.tesseramento`)
- **Tipo**: 
  - `annuale_solare`: Scade il 31 dicembre dell'anno di riferimento
  - `calendario`: Scade dopo 12 mesi dalla data di emissione
- Definisce il costo della tessera
- Relazione One2many con tessere

#### 3. **Tessera** (`tessera`)
- Relazione a tre: Piano + Utente + Associazione
- Calcolo automatico:
  - Nome tessera (formato: ASSOCIAZIONE-USER-ANNO-NUMERO)
  - Data scadenza (in base al tipo di piano)
  - Stato (attiva/scaduta/annullata)
- Stati:
  - `attiva`: Tessera valida e non scaduta
  - `scaduta`: Data scadenza passata
  - `annullata`: Tessera annullata manualmente

#### 4. **Tesseramento Pending** (`tesseramento.pending`)
- Salva i dati del tesseramento in attesa di pagamento
- Stati:
  - `pending`: In attesa di pagamento
  - `paid`: Pagato ma tessera non ancora creata
  - `completed`: Tessera creata
  - `cancelled`: Annullato

#### 5. **Res Users Esteso**
- Campi fiscali aggiunti:
  - codice_fiscale, data_nascita, luogo_nascita
  - street, street2, city, zip, state_id, country_id
  - phone
- Relazione One2many con tessere
- Metodi computed:
  - `tessera_attuale_id`: Tessera attiva più recente
  - `tessera_in_scadenza`: True se scade entro 30 giorni
  - `get_tessere_passate()`: Lista tessere scadute/annullate

## Flusso di Tesseramento

### 1. Form di Tesseramento (`/tesseramento`)
- L'utente deve essere loggato
- Compila:
  - Associazione
  - Piano di tesseramento
  - Dati fiscali completi (obbligatori)
- I dati fiscali vengono salvati nell'utente (`res.users`)

### 2. Creazione Tesseramento Pending
- Viene creato un record `tesseramento.pending` con stato `pending`
- Viene creata una transazione di pagamento (`payment.transaction`)
- L'utente viene reindirizzato alla pagina di pagamento

### 3. Pagamento
- L'utente completa il pagamento tramite il provider configurato
- Il provider gestisce il pagamento e chiama il callback

### 4. Callback Pagamento
- Route: `/tesseramento/payment/return`
- Se pagamento completato:
  - Aggiorna `tesseramento.pending` a stato `paid`
  - Chiama `action_completa_tessera()` che:
    - Crea la tessera
    - Aggiorna lo stato a `completed`
- Reindirizza a `/tesseramento/success`

### 5. Pagina Successo
- Mostra i dettagli della tessera creata
- Numero tessera, associazione, piano, date, importo

## Vista Utente (`/my/tessere`)

### Funzionalità
- **Tessera Attuale**: Mostra la tessera attiva con avviso se in scadenza (entro 30 giorni)
- **Form Rinnovo**: Permette di rinnovare la tessera
- **Tessere Passate**: Tabella con tutte le tessere scadute o annullate

## Integrazione Pagamenti

### Provider Supportati
- Qualsiasi provider configurato in Odoo (Stripe, PayPal, ecc.)
- Il primo provider attivo e pubblicato viene utilizzato

### Flusso Pagamento
1. Creazione transazione con riferimento `TESS-{pending_id}`
2. Redirect alla pagina di pagamento del provider
3. Callback automatico dopo il pagamento
4. Completamento automatico del tesseramento

### Gestione Errori
- Se il pagamento fallisce o viene annullato:
  - `tesseramento.pending` viene marcato come `cancelled`
  - L'utente vede un messaggio di errore
  - Può riprovare

## Calcolo Date Scadenza

### Piano Annuale Solare
- Scade sempre il **31 dicembre** dell'anno di riferimento
- Esempio: Emissione 15/06/2024, anno riferimento 2024 → Scade 31/12/2024

### Piano Calendario
- Scade dopo **365 giorni** dalla data di emissione
- Esempio: Emissione 15/06/2024 → Scade 15/06/2025

## Stati Tessera

### Calcolo Automatico
- Lo stato viene calcolato automaticamente in base alla data di scadenza
- Se `data_scadenza < oggi` → `scaduta`
- Se `data_scadenza >= oggi` → `attiva`
- Se stato = `annullata`, non viene modificato automaticamente

### Cron Job
- `_cron_aggiorna_stati()`: Aggiorna automaticamente le tessere scadute
- Da configurare come azione schedulata in Odoo

## Test Unitari

### Copertura
- ✅ Test ResUsers (5 test)
- ✅ Test Tessera (12 test)
- ✅ Test PianoTesseramento (6 test)
- ✅ Test AssociazioneCulturale (4 test)
- ✅ Test TesseramentoPending (5 test)

**Totale: 32 test case**

### Esecuzione
```bash
odoo-bin -c odoo.conf --test-enable --stop-after-init -d your_database -u associazioni_culturali
```

## Situazioni da Sistemare / Migliorare

### ⚠️ Problemi Identificati

1. **Link Pagamento**
   - Il metodo per ottenere il link di pagamento potrebbe non funzionare con tutti i provider
   - **Soluzione**: Verificare che `/payment/process?tx_id={tx.id}` funzioni correttamente
   - **Alternativa**: Usare `payment.link.wizard` se disponibile

2. **Callback Pagamento**
   - Il callback potrebbe non essere chiamato automaticamente da tutti i provider
   - **Soluzione**: Verificare che il provider configurato supporti i callback
   - **Alternativa**: Implementare polling o webhook specifici

3. **Gestione Provider Mancante**
   - Se non ci sono provider configurati, viene mostrato un errore
   - **Miglioramento**: Potrebbe essere utile un messaggio più chiaro o un fallback

4. **Validazione Dati Fiscali**
   - Non c'è validazione del formato del codice fiscale
   - **Miglioramento**: Aggiungere validazione formato codice fiscale italiano

5. **Gestione Valute Multiple**
   - Il modulo supporta valute multiple ma non verifica che il provider supporti la stessa valuta
   - **Miglioramento**: Verificare compatibilità valuta provider

6. **Timeout Tesseramento Pending**
   - I tesseramenti pending non scadono mai
   - **Miglioramento**: Aggiungere cron job per annullare tesseramenti pending vecchi (es. > 30 giorni)

7. **Notifiche Email**
   - Non ci sono notifiche email quando la tessera viene creata
   - **Miglioramento**: Aggiungere template email per conferma tesseramento

8. **Report e Statistiche**
   - Non ci sono report o statistiche
   - **Miglioramento**: Aggiungere report per associazioni (tessere emesse, incassi, ecc.)

### ✅ Funzionalità Complete

- ✅ Gestione associazioni culturali
- ✅ Piani di tesseramento con due tipi
- ✅ Creazione tessere con calcolo automatico date
- ✅ Integrazione pagamenti
- ✅ Vista utente con tessere
- ✅ Estensione utente con dati fiscali
- ✅ Test unitari completi
- ✅ Sicurezza e permessi

## Configurazione Richiesta

### Prerequisiti
1. Modulo `payment` installato e configurato
2. Almeno un provider di pagamento attivo e pubblicato
3. Utenti con permessi appropriati

### Setup
1. Creare associazioni culturali
2. Creare piani di tesseramento
3. Configurare provider di pagamento
4. (Opzionale) Configurare cron job per aggiornamento stati tessere

## Note Tecniche

- Il modulo usa `mail.thread` e `mail.activity.mixin` per tracciamento
- I dati fiscali vengono salvati sia in `res.users` che in `res.partner`
- Le tessere vengono ordinate per data emissione decrescente
- Il nome tessera viene generato automaticamente al salvataggio
