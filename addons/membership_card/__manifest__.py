{
    'name': 'Gestione Membership Card',
    'version': '19.0.1.0.0',
    'category': 'Membership',
    'summary': 'Gestione completa delle membership card per associazioni italiane',
    'description': """
Gestione Membership Card
========================
Modulo completo per la gestione delle membership card di un'associazione.

Funzionalità:
-------------
* Gestione membri con dati italiani (CF, P.IVA)
* Tipi di membership configurabili
* Generazione e stampa card
* Scadenze e rinnovi automatici
* API REST per integrazione frontend
* Reportistica completa
* Supporto per associazioni italiane
    """,
    'author': 'Victorian Monkey',
    'website': 'https://www.victorianmonkey.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'contacts',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/membership_security.xml',
        'data/membership_type_data.xml',
        'views/membership_type_views.xml',
        'views/member_views.xml',
        'views/membership_card_views.xml',
        'views/menu_views.xml',
        'reports/membership_card_report.xml',
        'reports/membership_card_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'membership_card/static/src/css/membership_card.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}

