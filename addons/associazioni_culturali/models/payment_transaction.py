# -*- coding: utf-8 -*-

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _finalize_post_processing(self):
        """Override per completare il tesseramento dopo il pagamento"""
        super()._finalize_post_processing()
        
        # Se la transazione è completata, verifica se è per un tesseramento.
        # Usa sudo() perché questo metodo può essere eseguito nel contesto dell'utente
        # portale (callback di pagamento), che non ha permessi su tesseramento.pending/tessera.
        if self.state == 'done':
            tesseramento_pending = self.env['tesseramento.pending'].sudo().search([
                ('transaction_id', '=', self.id),
                ('stato', 'in', ['pending', 'paid'])
            ], limit=1)
            
            if tesseramento_pending:
                tesseramento_pending.write({'stato': 'paid'})
                tessera = tesseramento_pending.action_completa_tessera()
                if tessera:
                    _logger.info(f"Tesseramento completato per transazione {self.id}, tessera creata: {tessera.id}")
                else:
                    _logger.warning(f"Tesseramento pending {tesseramento_pending.id} non completato per transazione {self.id}")
                    
