{
    'name': 'Associazioni Culturali',
    'version': '1.0.0',
    'category': 'Services',
    'summary': 'Gestione associazioni culturali',
    'description': """
        Modulo per la gestione di associazioni culturali
        =================================================
        
        Questo modulo fornisce funzionalità per:
        * Gestione associazioni culturali
        * Gestione membri e soci
        * Gestione eventi e attività
    """,
    'author': 'Vicedomini Softworks',
    'website': 'https://www.vicedominisoftworks.com',
    'depends': ['base', 'website', 'auth_signup', 'payment', 'mail', 'mass_mailing'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/email_templates.xml',
        'data/cron_data.xml',
        'views/associazioni_culturali_views.xml',
        'views/piano_tesseramento_views.xml',
        'views/tessera_views.xml',
        'views/tesseramento_website_templates.xml',
    ],
    'demo': [],
    'test': [
        'tests/test_res_users.py',
        'tests/test_tessera.py',
        'tests/test_piano_tesseramento.py',
        'tests/test_associazione_culturale.py',
        'tests/test_tesseramento_pending.py',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
