# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re


class Associato(models.Model):
    _name = 'associato'
    _description = _('Associato')
    _order = 'email, id'

    name = fields.Char(string='Nome', compute='_compute_name', store=True, readonly=True)
    email = fields.Char(string='Email', required=True, index=True, tracking=True)
    user_id = fields.Many2one(
        'res.users',
        string='Utente collegato',
        ondelete='set null',
        help='Utente che ha reclamato questo profilo (stessa email). Vuoto se non ancora associato.',
    )
    codice_fiscale = fields.Char(string='Codice Fiscale', tracking=True)
    data_nascita = fields.Date(string='Data di Nascita', tracking=True)
    luogo_nascita = fields.Char(string='Luogo di Nascita', tracking=True)
    street = fields.Char(string='Via', tracking=True)
    street2 = fields.Char(string='Via 2', tracking=True)
    city = fields.Char(string='Città', tracking=True)
    zip = fields.Char(string='CAP', tracking=True)
    state_id = fields.Many2one('res.country.state', string='Provincia', tracking=True)
    country_id = fields.Many2one(
        'res.country',
        string='Paese',
        default=lambda self: self.env.ref('base.it', raise_if_not_found=False),
        tracking=True,
    )
    phone = fields.Char(string='Telefono', tracking=True)

    tessere_ids = fields.One2many('tessera', 'associato_id', string='Tessere', readonly=True)

    tessera_attuale_id = fields.Many2one(
        'tessera',
        string='Tessera Attuale',
        compute='_compute_tessera_attuale',
        store=False,
    )
    tessera_in_scadenza = fields.Boolean(
        string='Tessera in Scadenza',
        compute='_compute_tessera_attuale',
        store=False,
    )

    @api.depends('email', 'user_id', 'user_id.name')
    def _compute_name(self):
        for record in self:
            if record.user_id:
                record.name = f"{record.email} ({record.user_id.name})"
            else:
                record.name = record.email or _('Nuovo Associato')

    @api.constrains('codice_fiscale')
    def _check_codice_fiscale(self):
        """Valida il formato del codice fiscale italiano"""
        for record in self:
            if record.codice_fiscale and record.country_id and record.country_id.code == 'IT':
                cf = record.codice_fiscale.upper().strip()
                if not re.match(
                    r'^[A-Z]{6}[0-9LMNPQRSTUV]{2}[ABCDEHLMPRST][0-9LMNPQRSTUV]{2}[A-Z][0-9LMNPQRSTUV]{3}[A-Z]$',
                    cf,
                ):
                    raise ValidationError(
                        _(
                            'Il codice fiscale non è valido. '
                            'Il codice fiscale italiano deve essere di 16 caratteri alfanumerici nel formato corretto.'
                        )
                    )

    @api.depends('tessere_ids', 'tessere_ids.stato', 'tessere_ids.data_scadenza')
    def _compute_tessera_attuale(self):
        """Calcola la tessera attuale (attiva e non scaduta)"""
        today = fields.Date.today()
        for record in self:
            tessera_attuale = record.tessere_ids.filtered(
                lambda t: t.stato == 'attiva'
                and t.data_scadenza
                and t.data_scadenza >= today
            ).sorted('data_scadenza', reverse=True)
            if tessera_attuale:
                record.tessera_attuale_id = tessera_attuale[0]
                giorni_alla_scadenza = (tessera_attuale[0].data_scadenza - today).days
                record.tessera_in_scadenza = 0 <= giorni_alla_scadenza <= 30
            else:
                record.tessera_attuale_id = False
                record.tessera_in_scadenza = False

    def get_tessere_passate(self):
        """Restituisce le tessere passate (scadute o annullate)"""
        today = fields.Date.today()
        return self.tessere_ids.filtered(
            lambda t: t.stato in ('scaduta', 'annullata')
            or (t.data_scadenza and t.data_scadenza < today)
        ).sorted('data_scadenza', reverse=True)

    def action_reclama(self):
        """Associa questo profilo all'utente corrente se l'email coincide."""
        self.ensure_one()
        user = self.env.user
        if user._is_public():
            raise UserError(_('Devi effettuare l\'accesso per reclamare un profilo.'))
        email_user = (user.partner_id.email or user.login or '').strip().lower()
        email_associato = (self.email or '').strip().lower()
        if not email_user or email_user != email_associato:
            raise UserError(
                _(
                    'Puoi reclamare solo un profilo associato con la stessa email del tuo account (%s).',
                    user.partner_id.email or user.login,
                )
            )
        if self.user_id and self.user_id != user:
            raise UserError(_('Questo profilo è già associato a un altro utente.'))
        self.write({'user_id': user.id})
        return True
