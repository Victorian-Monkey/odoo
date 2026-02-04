# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AssociazioneCulturale(models.Model):
    _name = 'associazione.culturale'
    _description = _('Associazione')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nome', required=True, tracking=True)
    image_128 = fields.Image(string='Logo', max_width=128, max_height=128)
    company_id = fields.Many2one('res.partner', string='Azienda', required=True, 
                                  domain="[('is_company', '=', True)]", tracking=True)
    codice_fiscale = fields.Char(string='Codice Fiscale', tracking=True)
    partita_iva = fields.Char(string='Partita IVA', tracking=True)
    indirizzo = fields.Text(string='Indirizzo')
    telefono = fields.Char(string='Telefono')
    email = fields.Char(string='Email')
    sito_web = fields.Char(string='Sito Web')
    data_costituzione = fields.Date(string='Data Costituzione')
    attivo = fields.Boolean(string='Attivo', default=True)
    consenti_registrazione_pubblica = fields.Boolean(
        string='Consenti Registrazione Pubblica',
        default=True,
        help='Se attivo, questa associazione sarà disponibile nella select del form di tesseramento pubblico',
        tracking=True
    )
    note = fields.Text(string='Note')
    
    # Relazioni inverse
    tessere_ids = fields.One2many('tessera', 'associazione_id', string='Tessere')

    _sql_constraints = [
        ('codice_fiscale_unique', 'unique(codice_fiscale)', _('Il codice fiscale deve essere unico!')),
    ]
