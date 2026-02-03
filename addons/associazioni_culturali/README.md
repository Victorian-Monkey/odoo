# Associazioni Culturali - Odoo 19 Module

Modulo Odoo 19 per la gestione di associazioni culturali.

## Descrizione

Questo modulo fornisce funzionalità per la gestione di associazioni culturali, inclusa la gestione di:
- Associazioni culturali
- Informazioni anagrafiche e fiscali
- Contatti e comunicazioni

## Installazione

1. Copia la cartella del modulo nella directory `addons` della tua installazione Odoo
2. Aggiorna la lista delle app: `odoo-bin -u all -d your_database`
3. Attiva la modalità sviluppatore
4. Vai su App > Aggiorna lista app
5. Cerca "Associazioni Culturali" e installa il modulo

## Requisiti

- Odoo 19.0

## Dipendenze

- `base`

## Struttura del Modulo

```
associazioni-culturali/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── associazione_culturale.py
├── views/
│   └── associazioni_culturali_views.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── controllers/
│   └── __init__.py
├── data/
├── demo/
├── wizard/
│   └── __init__.py
├── report/
│   └── __init__.py
└── static/
    └── description/
        └── index.html
```

## Funzionalità

- Gestione associazioni culturali con informazioni complete
- Tracciamento delle attività e comunicazioni
- Ricerca e filtri avanzati
- Interfaccia utente intuitiva

## Sviluppo

Per contribuire al modulo:

1. Clona il repository
2. Crea un branch per le tue modifiche
3. Fai le modifiche necessarie
4. Testa le modifiche
5. Crea una merge request

## Licenza

LGPL-3

## Autore

Your Company
