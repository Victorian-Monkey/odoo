{
    'name': 'POS Restaurant Web Menu',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Menu Web per Ristoranti POS con QR Code',
    'description': """
POS Restaurant Web Menu
========================
Questo modulo crea un menu web per ristoranti POS che permette ai clienti di:
* Visualizzare il menu sui loro smartphone tramite QR code
* Vedere prodotti per categoria con prezzi e immagini
* Aggiungere prodotti al carrello
* Creare ordini selezionando il tavolo
* Aggiungere prodotti a ordini esistenti se il tavolo ha già un ordine

Funzionalità:
-------------
* Configurazione menu dal dashboard POS
* Visualizzazione prezzi e immagini dei prodotti
* Carrello con possibilità di aggiungere/rimuovere prodotti
* Selezione tavolo e cliente
* Generazione QR code per accesso rapido al menu
* Design responsive per mobile
* Integrazione con POS Restaurant
    """,
    'author': 'Victorian Monkey',
    'website': 'https://www.victorianmonkey.com',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'pos_restaurant',
        'website',
        'mail',
        'stock',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
        'views/pos_restaurant_web_menu_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pos_restaurant_web_menu/static/src/css/pos_web_menu.css',
            'pos_restaurant_web_menu/static/src/js/pos_web_menu.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}

