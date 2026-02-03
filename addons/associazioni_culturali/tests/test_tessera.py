# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TestTessera(TransactionCase):

    def setUp(self):
        super(TestTessera, self).setUp()
        self.Tessera = self.env['tessera']
        self.Associato = self.env['associato']
        self.User = self.env['res.users']
        self.Associazione = self.env['associazione.culturale']
        self.Piano = self.env['piano.tesseramento']
        
        # Crea un'azienda partner
        self.company = self.env['res.partner'].create({
            'name': 'Test Company',
            'is_company': True,
        })
        
        # Crea un'associazione
        self.associazione = self.Associazione.create({
            'name': 'Test Associazione',
            'company_id': self.company.id,
            'attivo': True,
        })
        
        # Crea piani di tesseramento
        self.piano_annuale = self.Piano.create({
            'name': 'Piano Annuale 2024',
            'tipo': 'annuale_solare',
            'costo_tessera': 50.0,
            'anno_riferimento': 2024,
            'attivo': True,
        })
        
        self.piano_calendario = self.Piano.create({
            'name': 'Piano Calendario',
            'tipo': 'calendario',
            'costo_tessera': 60.0,
            'attivo': True,
        })
        
        # Crea un utente
        self.user = self.User.create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@example.com',
        })

    def test_tessera_creation(self):
        """Test creazione tessera base"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
            'importo_pagato': 50.0,
        })
        
        self.assertTrue(tessera)
        self.assertEqual(tessera.associato_id, self.associato)
        self.assertEqual(tessera.piano_id, self.piano_annuale)
        self.assertEqual(tessera.associazione_id, self.associazione)
        self.assertEqual(tessera.importo_pagato, 50.0)

    def test_tessera_name_compute_annuale(self):
        """Test calcolo nome tessera per piano annuale"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date(2024, 1, 15),
        })
        
        # Il nome dovrebbe essere nel formato: ASSOCIAZIONE-USER-ANNO-NUMERO
        self.assertTrue(tessera.name)
        self.assertIn('TEST', tessera.name.upper())
        self.assertIn(str(self.associato.id), tessera.name)
        self.assertIn('2024', tessera.name)

    def test_tessera_name_compute_calendario(self):
        """Test calcolo nome tessera per piano calendario"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_calendario.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
        })
        
        self.assertTrue(tessera.name)
        self.assertIn('TEST', tessera.name.upper())
        self.assertIn(str(self.associato.id), tessera.name)

    def test_data_scadenza_annuale_solare(self):
        """Test calcolo data scadenza per piano annuale solare"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date(2024, 6, 15),
        })
        
        # Dovrebbe scadere il 31 dicembre 2024
        self.assertEqual(tessera.data_scadenza, date(2024, 12, 31))

    def test_data_scadenza_calendario(self):
        """Test calcolo data scadenza per piano calendario"""
        data_emissione = date(2024, 3, 15)
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_calendario.id,
            'associazione_id': self.associazione.id,
            'data_emissione': data_emissione,
        })
        
        # Dovrebbe scadere dopo 365 giorni
        expected_scadenza = data_emissione + timedelta(days=365)
        self.assertEqual(tessera.data_scadenza, expected_scadenza)

    def test_stato_attiva(self):
        """Test stato tessera attiva"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
            'data_scadenza': date.today() + timedelta(days=100),
        })
        
        self.assertEqual(tessera.stato, 'attiva')

    def test_stato_scaduta(self):
        """Test stato tessera scaduta"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date(2023, 1, 1),
            'data_scadenza': date(2023, 12, 31),
        })
        
        # Forza il calcolo dello stato
        tessera._compute_stato()
        
        self.assertEqual(tessera.stato, 'scaduta')

    def test_action_annulla(self):
        """Test azione annulla tessera"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
            'stato': 'attiva',
        })
        
        tessera.action_annulla()
        
        self.assertEqual(tessera.stato, 'annullata')

    def test_action_riattiva_scaduta(self):
        """Test riattivazione tessera scaduta"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date(2023, 1, 1),
            'data_scadenza': date(2023, 12, 31),
            'stato': 'annullata',
        })
        
        tessera.action_riattiva()
        
        # Dovrebbe diventare scaduta, non attiva
        self.assertEqual(tessera.stato, 'scaduta')

    def test_action_riattiva_attiva(self):
        """Test riattivazione tessera ancora valida"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
            'data_scadenza': date.today() + timedelta(days=100),
            'stato': 'annullata',
        })
        
        tessera.action_riattiva()
        
        self.assertEqual(tessera.stato, 'attiva')

    def test_stato_non_cambia_se_annullata(self):
        """Test che lo stato non cambi se già annullata"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date(2023, 1, 1),
            'data_scadenza': date(2023, 12, 31),
            'stato': 'annullata',
        })
        
        # Anche se scaduta, se è annullata non deve cambiare
        tessera._compute_stato()
        
        self.assertEqual(tessera.stato, 'annullata')

    def test_cron_aggiorna_stati(self):
        """Test cron job per aggiornare stati tessere scadute"""
        # Crea tessera attiva ma scaduta
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date(2023, 1, 1),
            'data_scadenza': date(2023, 12, 31),
            'stato': 'attiva',
        })
        
        # Esegui il cron
        self.Tessera._cron_aggiorna_stati()
        
        # Ricarica la tessera
        tessera.invalidate_recordset()
        self.assertEqual(tessera.stato, 'scaduta')
