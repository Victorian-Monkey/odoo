Associazioni Culturali
========================

Panoramica
----------

Il modulo **Associazioni Culturali** per Odoo 19 fornisce una soluzione completa per la gestione del tesseramento online di associazioni di ogni tipo: culturali, sportive, di volontariato, ricreative e altre.

Funzionalità principali:

* Gestione associazioni culturali con informazioni complete
* Piani di tesseramento configurabili (annuale solare o calendario)
* Sistema di tesseramento online integrato
* Pagamento online tramite provider Odoo
* Area riservata per i soci ("Le mie tessere")
* Gestione dati fiscali e anagrafici
* Integrazione con newsletter e mailing list

Installazione
-------------

1. Copia la cartella del modulo nella directory ``addons`` della tua installazione Odoo 19
2. Aggiorna la lista delle app: ``odoo-bin -u all -d your_database``
3. Attiva la modalità sviluppatore
4. Vai su App > Aggiorna lista app
5. Cerca "Associazioni" e installa il modulo

Requisiti
---------

* Odoo 19.0
* Moduli dipendenti: ``base``, ``website``, ``auth_signup``, ``payment``, ``mail``, ``mass_mailing``

Configurazione
--------------

Prerequisiti
~~~~~~~~~~~~

1. Modulo ``payment`` installato e configurato
2. Almeno un provider di pagamento attivo e pubblicato (Stripe, PayPal, ecc.)
3. Utenti con permessi appropriati

Setup iniziale
~~~~~~~~~~~~~~

1. **Creare associazioni culturali**
   
   Vai su Associazioni > Associazioni e crea le associazioni che gestirai.

2. **Creare piani di tesseramento**
   
   Vai su Associazioni > Piani Tesseramento e crea i piani disponibili:
   
   * **Anno Solare**: Scade il 31 dicembre dell'anno di riferimento
   * **Calendario**: Scade dopo 12 mesi dalla data di emissione

3. **Configurare provider di pagamento**
   
   Vai su Website > Configuration > Payment Providers e configura almeno un provider.

4. **Configurare cron job (opzionale)**
   
   Il modulo include un cron job per aggiornare automaticamente gli stati delle tessere scadute.

Modelli Principali
------------------

Associazione Culturale
~~~~~~~~~~~~~~~~~~~~~~

Il modello ``associazione.culturale`` gestisce le informazioni delle associazioni:

* Nome e collegamento a un'azienda (``res.partner``)
* Informazioni fiscali (codice fiscale, partita IVA)
* Dati di contatto (telefono, email, sito web)
* Indirizzo completo
* Logo/icona dell'associazione
* Relazione con le tessere emesse

Piano Tesseramento
~~~~~~~~~~~~~~~~~~

Il modello ``piano.tesseramento`` definisce i piani disponibili:

* **Nome**: Nome del piano (es. "Tessera Annuale 2024")
* **Tipo**: 
  
  * ``annuale_solare``: Scade il 31 dicembre dell'anno di riferimento
  * ``calendario``: Scade dopo 12 mesi dalla data di emissione
* **Costo**: Importo della tessera
* **Anno di riferimento**: Solo per tipo annuale solare
* **Stato attivo**: Se il piano è disponibile per nuovi tesseramenti

Tessera
~~~~~~~

Il modello ``tessera`` rappresenta una tessera emessa:

* **Numero tessera**: Generato automaticamente (formato: ASSOCIAZIONE-USER-ANNO-NUMERO)
* **Associato**: Collegamento al profilo associato
* **Associazione**: Associazione di riferimento
* **Piano**: Piano di tesseramento utilizzato
* **Date**: Data emissione e data scadenza (calcolata automaticamente)
* **Stato**: 
  
  * ``attiva``: Tessera valida e non scaduta
  * ``scaduta``: Data scadenza passata
  * ``annullata``: Tessera annullata manualmente
* **Importo pagato**: Importo versato per la tessera

Associato
~~~~~~~~~

Il modello ``associato`` rappresenta un socio:

* Dati anagrafici (nome legale, cognome legale, nome di elezione)
* Email (chiave univoca)
* Codice fiscale (con opzione "non ho codice fiscale")
* Data e luogo di nascita
* Indirizzo completo
* Telefono
* Collegamento a ``res.users`` (se l'utente ha reclamato il profilo)

Flusso di Tesseramento
----------------------

1. Form di Tesseramento (``/tesseramento``)
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   L'utente deve essere autenticato e compila:
   
   * Associazione
   * Piano di tesseramento
   * Dati fiscali completi (obbligatori)
   
   I dati fiscali vengono salvati nell'utente (``res.users``).

2. Creazione Tesseramento Pending
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Viene creato un record ``tesseramento.pending`` con stato ``pending`` e una transazione di pagamento. L'utente viene reindirizzato alla pagina di pagamento.

3. Pagamento
   ~~~~~~~~~~

   L'utente completa il pagamento tramite il provider configurato. Il provider gestisce il pagamento e chiama il callback.

4. Callback Pagamento
   ~~~~~~~~~~~~~~~~~~~

   Route: ``/tesseramento/payment/return``
   
   Se il pagamento è completato:
   
   * Aggiorna ``tesseramento.pending`` a stato ``paid``
   * Chiama ``action_completa_tessera()`` che crea la tessera
   * Aggiorna lo stato a ``completed``
   * Reindirizza a ``/tesseramento/success``

5. Pagina Successo
   ~~~~~~~~~~~~~~~~

   Mostra i dettagli della tessera creata: numero tessera, associazione, piano, date, importo.

Area Riservata Utente
---------------------

Vista "Le mie tessere" (``/my/tessere``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Funzionalità disponibili:

* **Tessera Attuale**: Mostra la tessera attiva con avviso se in scadenza (entro 30 giorni)
* **Form Rinnovo**: Permette di rinnovare la tessera selezionando un nuovo piano
* **Tessere Passate**: Tabella con tutte le tessere scadute o annullate
* **Reclama Profilo**: Permette di collegare un profilo associato esistente al proprio account utente

Calcolo Date Scadenza
---------------------

Piano Annuale Solare
~~~~~~~~~~~~~~~~~~~~

La tessera scade sempre il **31 dicembre** dell'anno di riferimento, indipendentemente dalla data di emissione.

Esempio:
  
  * Emissione: 15/06/2024
  * Anno riferimento: 2024
  * Scadenza: 31/12/2024

Piano Calendario
~~~~~~~~~~~~~~~~

La tessera scade dopo **365 giorni** dalla data di emissione.

Esempio:
  
  * Emissione: 15/06/2024
  * Scadenza: 15/06/2025

Stati Tessera
-------------

Calcolo Automatico
~~~~~~~~~~~~~~~~~

Lo stato viene calcolato automaticamente in base alla data di scadenza:

* Se ``data_scadenza < oggi`` → ``scaduta``
* Se ``data_scadenza >= oggi`` → ``attiva``
* Se stato = ``annullata``, non viene modificato automaticamente

Cron Job
~~~~~~~~

Il modulo include un cron job (``_cron_aggiorna_stati``) che aggiorna automaticamente le tessere scadute. Configurare come azione schedulata in Odoo.

Integrazione Pagamenti
----------------------

Provider Supportati
~~~~~~~~~~~~~~~~~~~

Qualsiasi provider configurato in Odoo che supporta la valuta del piano:

* Stripe
* PayPal
* Altri provider compatibili con Odoo Payment

Il primo provider attivo e pubblicato viene utilizzato automaticamente.

Flusso Pagamento
~~~~~~~~~~~~~~~

1. Creazione transazione con riferimento ``TESS-{pending_id}``
2. Redirect alla pagina di pagamento del provider
3. Callback automatico dopo il pagamento
4. Completamento automatico del tesseramento

Gestione Errori
~~~~~~~~~~~~~~

Se il pagamento fallisce o viene annullato:

* ``tesseramento.pending`` viene marcato come ``cancelled``
* L'utente vede un messaggio di errore
* Può riprovare il tesseramento

Integrazione Newsletter
------------------------

Durante il processo di tesseramento, l'utente può selezionare le mailing list a cui iscriversi. Le liste selezionate vengono associate automaticamente al contatto mailing.

Permessi e Sicurezza
--------------------

Il modulo include:

* Gruppi di sicurezza per gestire i permessi
* Accesso controllato ai dati degli associati
* Protezione dei dati fiscali
* Permessi differenziati per backend e frontend

Supporto e Assistenza
---------------------

Per supporto tecnico o domande:

* Website: https://www.vicedominisoftworks.com
* Email: Contattare tramite il sito web

Licenza
-------

Other proprietary

Autore
------

Vicedomini Softworks
