# POS Restaurant Web Menu

Modulo Odoo 19 per creare un menu web per ristoranti POS che permette ai clienti di visualizzare il menu sui loro smartphone tramite QR code.

## Funzionalità

- **Menu Web**: Visualizza tutti i prodotti POS organizzati per categoria
- **Immagini e Prezzi**: Mostra immagini e prezzi dei prodotti
- **Carrello Interattivo**: Aggiungi/rimuovi prodotti dal carrello
- **Selezione Tavolo**: Seleziona il tavolo per l'ordine
- **Creazione Ordini**: Crea ordini POS direttamente dal web
- **Aggiunta a Ordini Esistenti**: Se un tavolo ha già un ordine, i prodotti vengono aggiunti all'ordine esistente
- **QR Code**: Genera QR code per accesso rapido al menu
- **Design Responsive**: Ottimizzato per dispositivi mobili

## Installazione

1. Copia il modulo nella cartella `addons/` di Odoo
2. Installa la dipendenza Python: `pip install qrcode[pil]`
3. Aggiorna la lista delle app: `Apps > Update Apps List`
4. Cerca "POS Restaurant Web Menu" e installa
5. Assicurati che il modulo `pos_restaurant` sia installato

## Configurazione

1. Vai su **Punto Vendita > Configurazione > Bar/Ristorante**
2. Seleziona la configurazione POS del tuo ristorante
3. Abilita l'opzione **"Abilita Menu Web"**
4. Viene generato automaticamente l'URL del menu web
5. Clicca su **"Genera QR Code"** per creare il codice QR da stampare e posizionare sui tavoli

## Utilizzo

### Per i Clienti

1. Scansiona il QR code sul tavolo con il tuo smartphone
2. Visualizza il menu organizzato per categorie
3. Aggiungi prodotti al carrello cliccando su "Aggiungi"
4. Seleziona il tavolo dal menu a tendina
5. Clicca su "Ordina" per creare l'ordine

### Per il Ristorante

- Gli ordini creati dal web appaiono nella sessione POS attiva
- Se un tavolo ha già un ordine, i nuovi prodotti vengono aggiunti all'ordine esistente
- Gli ordini possono essere gestiti normalmente dal POS

## Requisiti

- Odoo 19.0
- Modulo `point_of_sale` installato
- Modulo `pos_restaurant` installato
- Modulo `website` installato
- Python package: `qrcode[pil]`

## Note

- È necessario avere una sessione POS attiva per creare ordini dal web
- Il modulo funziona solo con configurazioni POS che hanno il modulo ristorante abilitato
- I prodotti devono essere configurati come disponibili nel POS

## Licenza

LGPL-3

## Autore

Victorian Monkey

