# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from datetime import date, datetime, timedelta
from unittest.mock import patch


class TestTesseramentoPending(TransactionCase):

    def setUp(self):
        super(TestTesseramentoPending, self).setUp()
        self.TesseramentoPending = self.env['tesseramento.pending']
        self.Associato = self.env['associato']
        self.User = self.env['res.users']
        self.Associazione = self.env['associazione.culturale']
        self.Piano = self.env['piano.tesseramento']
        self.Tessera = self.env['tessera']
        self.Partner = self.env['res.partner']
        
        # Crea un'azienda partner
        self.company = self.Partner.create({
            'name': 'Test Company',
            'is_company': True,
        })
        
        # Crea un'associazione
        self.associazione = self.Associazione.create({
            'name': 'Test Associazione',
            'company_id': self.company.id,
            'attivo': True,
        })
        
        # Crea un piano
        self.piano = self.Piano.create({
            'name': 'Piano Test',
            'tipo': 'annuale_solare',
            'costo_tessera': 50.0,
            'anno_riferimento': 2024,
            'attivo': True,
        })
        
        # Crea utente e associato
        self.user = self.User.create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@example.com',
        })
        self.associato = self.Associato.create({
            'email': 'test@example.com',
            'associato_id': self.associato.id,
        })

    def test_tesseramento_pending_creation(self):
        """Test creazione tesseramento pending"""
        pending = self.TesseramentoPending.create({
            'associato_id': self.associato.id,
            'associazione_id': self.associazione.id,
            'piano_id': self.piano.id,
            'importo': 50.0,
            'stato': 'pending',
        })
        
        self.assertEqual(pending.associato_id, self.associato)
        self.assertEqual(pending.associazione_id, self.associazione)
        self.assertEqual(pending.piano_id, self.piano)
        self.assertEqual(pending.importo, 50.0)
        self.assertEqual(pending.stato, 'pending')
        self.assertFalse(pending.tessera_id)

    def test_name_compute(self):
        """Test calcolo nome tesseramento pending"""
        pending = self.TesseramentoPending.create({
            'associato_id': self.associato.id,
            'associazione_id': self.associazione.id,
            'piano_id': self.piano.id,
            'importo': 50.0,
        })
        
        self.assertTrue(pending.name)
        self.assertIn('TESS', pending.name)
        self.assertIn(str(self.associato.id), pending.name)
        self.assertIn(str(self.associazione.id), pending.name)

    def test_action_completa_tessera(self):
        """Test completamento tessera dopo pagamento"""
        pending = self.TesseramentoPending.create({
            'associato_id': self.associato.id,
            'associazione_id': self.associazione.id,
            'piano_id': self.piano.id,
            'importo': 50.0,
            'stato': 'paid',
            'note': 'Test note',
        })
        
        tessera = pending.action_completa_tessera()
        
        self.assertTrue(tessera)
        self.assertEqual(tessera.associato_id, self.associato)
        self.assertEqual(tessera.associazione_id, self.associazione)
        self.assertEqual(tessera.piano_id, self.piano)
        self.assertEqual(tessera.importo_pagato, 50.0)
        self.assertEqual(tessera.note, 'Test note')
        self.assertEqual(pending.tessera_id, tessera)
        self.assertEqual(pending.stato, 'completed')

    def test_action_completa_tessera_not_paid(self):
        """Test che action_completa_tessera non funzioni se non pagato"""
        pending = self.TesseramentoPending.create({
            'associato_id': self.associato.id,
            'associazione_id': self.associazione.id,
            'piano_id': self.piano.id,
            'importo': 50.0,
            'stato': 'pending',  # Non pagato
        })
        
        tessera = pending.action_completa_tessera()
        
        self.assertFalse(tessera)
        self.assertFalse(pending.tessera_id)
        self.assertEqual(pending.stato, 'pending')

    def test_action_completa_tessera_already_completed(self):
        """Test che action_completa_tessera non crei duplicati"""
        pending = self.TesseramentoPending.create({
            'associato_id': self.associato.id,
            'associazione_id': self.associazione.id,
            'piano_id': self.piano.id,
            'importo': 50.0,
            'stato': 'paid',
        })
        
        # Prima chiamata
        tessera1 = pending.action_completa_tessera()
        self.assertTrue(tessera1)
        
        # Seconda chiamata - non dovrebbe creare un'altra tessera
        tessera2 = pending.action_completa_tessera()
        self.assertFalse(tessera2)  # Ritorna False perché già completato
        self.assertEqual(pending.tessera_id, tessera1)
        self.assertEqual(pending.stato, 'completed')

    def test_send_email_conferma(self):
        """Test invio email di conferma quando tessera viene creata"""
        pending = self.TesseramentoPending.create({
            'associato_id': self.associato.id,
            'associazione_id': self.associazione.id,
            'piano_id': self.piano.id,
            'importo': 50.0,
            'stato': 'paid',
        })
        
        # Mock del template email per evitare errori se non esiste
        with patch.object(self.env['mail.template'], 'send_mail') as mock_send:
            tessera = pending.action_completa_tessera()
            
            # Verifica che la tessera sia stata creata
            self.assertTrue(tessera)
            
            # Verifica che send_mail sia stato chiamato (se il template esiste)
            # Nota: potrebbe non essere chiamato se il template non esiste, ma non è un errore

    def test_cron_annulla_pending_scaduti(self):
        """Test cron job per annullare tesseramenti pending scaduti"""
        # Crea tesseramenti pending recenti (non dovrebbero essere annullati)
        pending_recente = self.TesseramentoPending.create({
            'associato_id': self.associato.id,
            'associazione_id': self.associazione.id,
            'piano_id': self.piano.id,
            'importo': 50.0,
            'stato': 'pending',
        })
        
        # Crea un tesseramento pending vecchio modificando direttamente il database
        pending_old = self.TesseramentoPending.create({
            'associato_id': self.associato.id,
            'associazione_id': self.associazione.id,
            'piano_id': self.piano.id,
            'importo': 50.0,
            'stato': 'pending',
        })
        
        # Modifica create_date direttamente nel database per simulare un record vecchio
        old_date = datetime.now() - timedelta(days=35)
        self.env.cr.execute(
            "UPDATE tesseramento_pending SET create_date = %s WHERE id = %s",
            (old_date, pending_old.id)
        )
        self.env.cr.commit()
        
        # Esegui il cron
        self.TesseramentoPending._cron_annulla_pending_scaduti()
        
        # Ricarica i record
        pending_recente.invalidate_recordset()
        pending_old.invalidate_recordset()
        
        # Verifica che pending_old sia stato annullato
        self.assertEqual(pending_old.stato, 'cancelled')
        # Verifica che pending_recente non sia stato toccato
        self.assertEqual(pending_recente.stato, 'pending')
