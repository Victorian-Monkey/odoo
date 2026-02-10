# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class Tessera(models.Model):
    _name = 'tessera'
    _description = _('Tessera')
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'data_emissione desc, id desc'

    name = fields.Char(string='Numero Tessera', compute='_compute_name', store=True)
    piano_id = fields.Many2one('piano.tesseramento', string='Piano Tesseramento', 
                                required=True, tracking=True)
    associato_id = fields.Many2one('associato', string='Associato', 
                                   required=True, tracking=True, ondelete='cascade')
    associazione_id = fields.Many2one('associazione.culturale', string='Associazione', 
                                       required=True, tracking=True)
    data_emissione = fields.Date(string='Data Emissione', required=True, 
                                   default=fields.Date.today, tracking=True)
    data_scadenza = fields.Date(string='Data Scadenza', compute='_compute_data_scadenza', 
                                 store=True, tracking=True)
    stato = fields.Selection([
        ('attiva', 'Attiva'),
        ('scaduta', 'Scaduta'),
        ('annullata', 'Annullata'),
    ], string='Stato', compute='_compute_stato', store=True, readonly=False, default='attiva')
    importo_pagato = fields.Monetary(string='Importo Pagato', 
                                      currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Valuta', 
                                   default=lambda self: self.env.company.currency_id)
    note = fields.Text(string='Note')
    invia_email_conferma = fields.Boolean(
        string='Invia email di conferma al socio',
        default=True,
        help='Se attivo, alla creazione della tessera viene inviata un\'email al socio con i dettagli. Disattivare solo in creazione da backend se non si desidera inviare.',
    )

    @api.depends('piano_id', 'associato_id', 'associazione_id', 'data_emissione')
    def _compute_name(self):
        for record in self:
            if record.piano_id and record.associato_id and record.associazione_id:
                # Formato: ASSOCIAZIONE-ASSOCIATO-ANNO-NUMERO (id usato solo se già salvato)
                anno = record.data_emissione.year if record.data_emissione else fields.Date.today().year
                nome_associazione = record.associazione_id.name[:3].upper() if len(record.associazione_id.name) >= 3 else record.associazione_id.name.upper()
                associato_id = record.associato_id.id if record.associato_id else 'N/A'
                tessera_id = record.id if record.id else 'NEW'
                record.name = f"{nome_associazione}-{associato_id}-{anno}-{tessera_id}"
            else:
                record.name = 'Nuova Tessera'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Ricalcola il nome ora che i record hanno id (non si può usare id in @api.depends)
        records._compute_name()
        # Flush tutti i campi (nome e campi computati data_scadenza, stato) prima dell'invio email
        records.flush_recordset()
        # Invia email di conferma per le tessere con invia_email_conferma=True
        for record in records:
            if record.invia_email_conferma and record.associato_id.email:
                record._send_email_conferma_tessera()
        return records

    def _send_email_conferma_tessera(self):
        """Invia email di conferma al socio: tessera generata."""
        self.ensure_one()
        try:
            template = self.env.ref('associazioni_culturali.email_template_tessera_creata', False)
            if template and self.associato_id.email:
                template.send_mail(self.id, force_send=True)
        except Exception as e:
            _logger.warning(
                'Impossibile inviare email di conferma tessera %s: %s',
                self.id, str(e)
            )

    def action_reinvia_email_conferma(self):
        """Reinvia l'email di conferma tessera al socio (da backend)."""
        self.ensure_one()
        if not self.associato_id.email:
            raise UserError(_('Impossibile inviare: l\'associato non ha un indirizzo email.'))
        self._send_email_conferma_tessera()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Email inviata'),
                'message': _('Email di conferma tessera inviata a %s') % self.associato_id.email,
                'type': 'success',
                'sticky': False,
            },
        }

    @api.depends('piano_id', 'data_emissione', 'piano_id.tipo', 'piano_id.anno_riferimento')
    def _compute_data_scadenza(self):
        for record in self:
            if not record.piano_id or not record.data_emissione:
                record.data_scadenza = False
                continue
            
            if record.piano_id.tipo == 'annuale_solare':
                # Scade il 31 dicembre dell'anno di riferimento
                anno = record.piano_id.anno_riferimento or record.data_emissione.year
                record.data_scadenza = fields.Date.to_date(f'{anno}-12-31')
            elif record.piano_id.tipo == 'calendario':
                # Scade dopo 12 mesi dalla data di emissione
                data_emissione = fields.Date.to_date(record.data_emissione)
                record.data_scadenza = data_emissione + timedelta(days=365)
            else:
                record.data_scadenza = False

    @api.depends('data_scadenza')
    def _compute_stato(self):
        today = fields.Date.today()
        for record in self:
            # Se lo stato è già annullata, non cambiarlo
            if record.stato == 'annullata':
                continue
            if record.data_scadenza and record.data_scadenza < today:
                record.stato = 'scaduta'
            elif record.data_scadenza:
                record.stato = 'attiva'
            else:
                record.stato = 'attiva'

    def action_annulla(self):
        """Azione per annullare una tessera"""
        self.write({'stato': 'annullata'})
        return True

    def action_riattiva(self):
        """Azione per riattivare una tessera annullata"""
        today = fields.Date.today()
        for record in self:
            if record.data_scadenza and record.data_scadenza < today:
                record.stato = 'scaduta'
            else:
                record.stato = 'attiva'
        return True

    @api.model
    def _cron_aggiorna_stati(self):
        """Cron job per aggiornare gli stati delle tessere scadute"""
        today = fields.Date.today()
        tessere_scadute = self.search([
            ('stato', '=', 'attiva'),
            ('data_scadenza', '<', today)
        ])
        tessere_scadute.write({'stato': 'scaduta'})
