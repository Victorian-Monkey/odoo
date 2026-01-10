# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import secrets
import string


class MembershipCard(models.Model):
    _name = 'membership.card'
    _description = 'Card di Membership'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'issue_date desc, card_number'

    # Informazioni card
    card_number = fields.Char(string='Numero Card', required=True, readonly=True,
                             default=lambda self: self._generate_card_number(),
                             copy=False, index=True)
    barcode = fields.Char(string='Barcode', compute='_compute_barcode', store=True)
    qr_code = fields.Char(string='QR Code', compute='_compute_qr_code')
    
    # Membri e membership
    member_id = fields.Many2one('membership.member', string='Membro', required=True,
                               ondelete='cascade', tracking=True)
    membership_type_id = fields.Many2one('membership.type', string='Tipo Membership',
                                        related='member_id.membership_type_id', store=True)
    
    # Date
    issue_date = fields.Date(string='Data Emissione', required=True,
                            default=fields.Date.today, tracking=True)
    expiry_date = fields.Date(string='Data Scadenza', related='member_id.membership_end_date',
                            store=True, tracking=True)
    
    # Stato
    is_active = fields.Boolean(string='Attiva', compute='_compute_is_active', store=True)
    is_expired = fields.Boolean(string='Scaduta', compute='_compute_is_active', store=True)
    is_lost = fields.Boolean(string='Persa', default=False, tracking=True)
    is_stolen = fields.Boolean(string='Rubata', default=False, tracking=True)
    is_replaced = fields.Boolean(string='Sostituita', default=False)
    replaced_by_id = fields.Many2one('membership.card', string='Sostituita da')
    
    # Note
    notes = fields.Text(string='Note')
    
    @api.model
    def _generate_card_number(self):
        """Genera un numero di card univoco"""
        # Formato: ASS-YYYYMMDD-XXXXXX (es: ASS-20240115-ABC123)
        prefix = 'ASS'
        date_str = datetime.now().strftime('%Y%m%d')
        random_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        card_number = f"{prefix}-{date_str}-{random_suffix}"
        
        # Verifica unicità
        while self.env['membership.card'].search([('card_number', '=', card_number)], limit=1):
            random_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            card_number = f"{prefix}-{date_str}-{random_suffix}"
        
        return card_number
    
    @api.depends('card_number')
    def _compute_barcode(self):
        for record in self:
            if record.card_number:
                # Genera un barcode EAN-13 semplificato (solo numeri)
                card_clean = record.card_number.replace('-', '').replace('ASS', '')
                # Prendi solo i numeri e completa a 13 cifre
                numbers = ''.join(filter(str.isdigit, card_clean))
                if len(numbers) < 13:
                    numbers = numbers.ljust(13, '0')
                record.barcode = numbers[:13]
            else:
                record.barcode = False
    
    @api.depends('card_number', 'member_id')
    def _compute_qr_code(self):
        for record in self:
            if record.card_number and record.member_id:
                # QR code contiene: card_number|member_id|expiry_date
                data = f"{record.card_number}|{record.member_id.id}|{record.expiry_date or ''}"
                record.qr_code = data
            else:
                record.qr_code = False
    
    @api.depends('expiry_date', 'is_lost', 'is_stolen', 'is_replaced')
    def _compute_is_active(self):
        today = fields.Date.today()
        for record in self:
            if record.is_lost or record.is_stolen or record.is_replaced:
                record.is_active = False
                record.is_expired = False
            elif record.expiry_date:
                record.is_active = record.expiry_date >= today
                record.is_expired = record.expiry_date < today
            else:
                record.is_active = True
                record.is_expired = False
    
    def action_replace_card(self):
        """Sostituisce la card (per card perse/rubate)"""
        self.ensure_one()
        # Marca questa card come sostituita
        self.is_replaced = True
        
        # Crea una nuova card
        new_card = self.env['membership.card'].create({
            'member_id': self.member_id.id,
            'membership_type_id': self.membership_type_id.id,
            'issue_date': fields.Date.today(),
        })
        
        # Collega la nuova card alla vecchia
        self.replaced_by_id = new_card.id
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Card Sostituita',
            'res_model': 'membership.card',
            'res_id': new_card.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_print_card(self):
        """Stampa la card"""
        self.ensure_one()
        return self.env.ref('membership_card.action_report_membership_card').report_action(self)
    
    _sql_constraints = [
        ('card_number_unique', 'unique(card_number)', 'Il numero della card deve essere univoco!'),
    ]

