# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PianoTesseramento(models.Model):
    _name = 'piano.tesseramento'
    _description = _('Piano Tesseramento')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nome Piano', required=True, tracking=True)
    tipo = fields.Selection([
        ('annuale_solare', 'Anno Solare (1 Gennaio - 31 Dicembre)'),
        ('calendario', 'Calendario (12 mesi dalla data di emissione)'),
    ], string='Tipo', required=True, default='annuale_solare', tracking=True)
    costo_tessera = fields.Monetary(string='Costo Tessera', required=True, 
                                     currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Valuta', 
                                   default=lambda self: self.env.company.currency_id)
    anno_riferimento = fields.Integer(string='Anno di Riferimento', 
                                       help='Anno solare di riferimento (solo per tipo annuale solare)')
    attivo = fields.Boolean(string='Attivo', default=True)
    note = fields.Text(string='Note')
    
    # Relazioni inverse
    tessere_ids = fields.One2many('tessera', 'piano_id', string='Tessere')

    @api.model
    def _get_default_anno_riferimento(self):
        return fields.Date.today().year

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('tipo') == 'annuale_solare' and not vals.get('anno_riferimento'):
                vals['anno_riferimento'] = self._get_default_anno_riferimento()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('tipo') == 'annuale_solare' and not vals.get('anno_riferimento'):
            vals['anno_riferimento'] = self._get_default_anno_riferimento()
        return super().write(vals)
