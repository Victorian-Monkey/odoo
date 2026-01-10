# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MembershipType(models.Model):
    _name = 'membership.type'
    _description = 'Tipo di Membership'
    _order = 'sequence, name'

    name = fields.Char(string='Nome', required=True, translate=True)
    code = fields.Char(string='Codice', required=True, help='Codice univoco per il tipo di membership')
    description = fields.Text(string='Descrizione', translate=True)
    duration_months = fields.Integer(string='Durata (mesi)', required=True, default=12,
                                     help='Durata della membership in mesi')
    price = fields.Float(string='Prezzo', required=True, digits=(16, 2),
                        help='Prezzo della membership')
    active = fields.Boolean(string='Attivo', default=True)
    sequence = fields.Integer(string='Sequenza', default=10,
                              help='Ordine di visualizzazione')
    color = fields.Integer(string='Colore', default=0)
    
    # Campi per associazioni italiane
    tax_exempt = fields.Boolean(string='Esente IVA', default=True,
                               help='Se selezionato, la membership è esente IVA')
    requires_fiscal_code = fields.Boolean(string='Richiede Codice Fiscale', default=True)
    requires_vat = fields.Boolean(string='Richiede P.IVA', default=False,
                                 help='Richiede P.IVA per membri aziendali')
    
    # Relazioni
    member_ids = fields.One2many('membership.member', 'membership_type_id', string='Membri')
    member_count = fields.Integer(string='Numero Membri', compute='_compute_member_count', store=True)
    
    @api.depends('member_ids')
    def _compute_member_count(self):
        for record in self:
            record.member_count = len(record.member_ids)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Il codice del tipo di membership deve essere univoco!'),
    ]

