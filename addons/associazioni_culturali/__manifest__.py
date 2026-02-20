# -*- coding: utf-8 -*-
{
    "name": "Associazioni",
    "version": "1.0.2",
    "category": "Services",
    "summary": "Gestione associazioni (culturali, sportive, di volontariato, ecc.)",
    "description": """
        Modulo per la gestione di associazioni di ogni tipo
        ===================================================

        Questo modulo fornisce funzionalità per:
        * Gestione associazioni (culturali, sportive, di volontariato, ecc.)
        * Gestione membri e soci
        * Gestione eventi e attività
    """,
    "author": "Vicedomini Softworks",
    "website": "https://vicedominisoftworks.com/shop/odoo-extension-associations-6",
    "icon": "static/description/icon.png",
    "images": ["static/description/icon.png"],
    "price": 250.0,
    "currency": "EUR",
    "depends": ["base", "website", "auth_signup", "payment", "mail", "mass_mailing"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/email_templates.xml",
        "data/cron_data.xml",
        "data/res.comune.csv",
        "data/website_menu.xml",
        "views/associazioni_culturali_views.xml",
        "views/piano_tesseramento_views.xml",
        "views/tessera_views.xml",
        "views/res_comune_views.xml",
        "wizard/tessera_import_wizard_views.xml",
        "views/tesseramento_website_templates.xml",
    ],
    "demo": [],
    "test": [
        "tests/test_res_users.py",
        "tests/test_tessera.py",
        "tests/test_piano_tesseramento.py",
        "tests/test_associazione_culturale.py",
        "tests/test_tesseramento_pending.py",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "Other proprietary",
}
