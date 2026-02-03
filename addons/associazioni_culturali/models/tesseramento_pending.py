# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class TesseramentoPending(models.Model):
    _name = 'tesseramento.pending'
    _description = _('Tesseramento in Attesa di Pagamento')
    _order = 'create_date desc'

    name = fields.Char(string='Riferimento', compute='_compute_name', store=True)
    associato_id = fields.Many2one('associato', string='Associato', required=True, ondelete='cascade')
    associazione_id = fields.Many2one('associazione.culturale', string='Associazione', required=True)
    piano_id = fields.Many2one('piano.tesseramento', string='Piano Tesseramento', required=True)
    importo = fields.Monetary(string='Importo', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Valuta', 
                                   default=lambda self: self.env.company.currency_id)
    transaction_id = fields.Many2one('payment.transaction', string='Transazione Pagamento', ondelete='set null')
    tessera_id = fields.Many2one('tessera', string='Tessera Creata', readonly=True)
    stato = fields.Selection([
        ('pending', 'In Attesa di Pagamento'),
        ('paid', 'Pagato'),
        ('completed', 'Completato'),
        ('cancelled', 'Annullato'),
    ], string='Stato', default='pending', tracking=True)
    note = fields.Text(string='Note')
    create_date = fields.Datetime(string='Data Creazione', readonly=True)

    @api.depends('associato_id', 'associazione_id', 'piano_id', 'create_date')
    def _compute_name(self):
        for record in self:
            if record.associato_id and record.associazione_id and record.piano_id:
                data_str = record.create_date.strftime('%Y%m%d') if record.create_date else ''
                record.name = f"TESS-{record.associato_id.id}-{record.associazione_id.id}-{data_str}"
            else:
                record.name = 'Nuovo Tesseramento'

    def action_completa_tessera(self):
        """Completa la creazione della tessera dopo il pagamento"""
        for record in self:
            if record.stato == 'paid' and not record.tessera_id:
                tessera = self.env['tessera'].create({
                    'associato_id': record.associato_id.id,
                    'piano_id': record.piano_id.id,
                    'associazione_id': record.associazione_id.id,
                    'importo_pagato': record.importo,
                    'note': record.note,
                })
                record.write({
                    'tessera_id': tessera.id,
                    'stato': 'completed',
                })
                
                # Invia email di conferma
                self._send_email_conferma(tessera)
                
                return tessera
        return False

    def _send_email_conferma(self, tessera):
        """Invia email di conferma tesseramento"""
        try:
            template = self.env.ref('associazioni_culturali.email_template_tessera_creata', False)
            if template and tessera.associato_id.email:
                template.send_mail(tessera.id, force_send=True)
        except Exception as e:
            # Se il template non esiste o c'è un errore, logga ma non blocca
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f"Impossibile inviare email di conferma tessera {tessera.id}: {str(e)}")

    @api.model
    def _cron_annulla_pending_scaduti(self):
        """Cron job per annullare tesseramenti pending vecchi (> 30 giorni)"""
        cutoff_date = datetime.now() - timedelta(days=30)
        pending_scaduti = self.search([
            ('stato', '=', 'pending'),
            ('create_date', '<', cutoff_date),
        ])
        
        if pending_scaduti:
            pending_scaduti.write({'stato': 'cancelled'})
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info(f"Annullati {len(pending_scaduti)} tesseramenti pending scaduti")
