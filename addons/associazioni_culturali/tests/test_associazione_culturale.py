# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError
from datetime import date


class TestAssociazioneCulturale(TransactionCase):

    def setUp(self):
        super(TestAssociazioneCulturale, self).setUp()
        self.Associazione = self.env['associazione.culturale']
        self.Partner = self.env['res.partner']
        self.Tessera = self.env['tessera']
        self.Associato = self.env['associato']
        self.User = self.env['res.users']
        self.Piano = self.env['piano.tesseramento']
        
        # Crea un'azienda partner
        self.company = self.Partner.create({
            'name': 'Test Company',
            'is_company': True,
        })
        
        # Crea utente e associato
        self.user = self.User.create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@example.com',
        })
        self.associato = self.Associato.create({
            'email': 'test@example.com',
            'user_id': self.user.id,
        })
        
        # Crea un piano
        self.piano = self.Piano.create({
            'name': 'Piano Test',
            'tipo': 'annuale_solare',
            'costo_tessera': 50.0,
            'anno_riferimento': 2024,
            'attivo': True,
        })

    def test_associazione_creation(self):
        """Test creazione associazione base"""
        associazione = self.Associazione.create({
            'name': 'Test Associazione',
            'company_id': self.company.id,
            'codice_fiscale': '12345678901',
            'attivo': True,
        })
        
        self.assertEqual(associazione.name, 'Test Associazione')
        self.assertEqual(associazione.company_id, self.company)
        self.assertEqual(associazione.codice_fiscale, '12345678901')
        self.assertTrue(associazione.attivo)

    def test_codice_fiscale_unique(self):
        """Test che codice_fiscale sia unico"""
        # Crea un'altra azienda per la seconda associazione
        company2 = self.Partner.create({
            'name': 'Test Company 2',
            'is_company': True,
        })
        
        associazione1 = self.Associazione.create({
            'name': 'Associazione 1',
            'company_id': self.company.id,
            'codice_fiscale': '12345678901',
        })
        
        # Tentativo di creare un'altra associazione con lo stesso CF
        # SQL constraint solleva IntegrityError
        with self.assertRaises(IntegrityError):
            self.Associazione.create({
                'name': 'Associazione 2',
                'company_id': company2.id,
                'codice_fiscale': '12345678901',
            })
            self.env.cr.commit()  # Force commit per triggerare il constraint

    def test_tessere_ids_relation(self):
        """Test relazione One2many tessere_ids"""
        associazione = self.Associazione.create({
            'name': 'Test Associazione',
            'company_id': self.company.id,
            'attivo': True,
        })
        
        tessera1 = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano.id,
            'associazione_id': associazione.id,
            'data_emissione': date.today(),
        })
        
        tessera2 = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano.id,
            'associazione_id': associazione.id,
            'data_emissione': date.today(),
        })
        
        self.assertIn(tessera1, associazione.tessere_ids)
        self.assertIn(tessera2, associazione.tessere_ids)
        self.assertEqual(len(associazione.tessere_ids), 2)

    def test_associazione_fields(self):
        """Test tutti i campi dell'associazione"""
        associazione = self.Associazione.create({
            'name': 'Test Associazione',
            'company_id': self.company.id,
            'codice_fiscale': '12345678901',
            'partita_iva': 'IT12345678901',
            'indirizzo': 'Via Test 123',
            'telefono': '1234567890',
            'email': 'test@associazione.it',
            'sito_web': 'https://www.test.it',
            'data_costituzione': date(2020, 1, 1),
            'note': 'Note di test',
        })
        
        self.assertEqual(associazione.partita_iva, 'IT12345678901')
        self.assertEqual(associazione.indirizzo, 'Via Test 123')
        self.assertEqual(associazione.telefono, '1234567890')
        self.assertEqual(associazione.email, 'test@associazione.it')
        self.assertEqual(associazione.sito_web, 'https://www.test.it')
        self.assertEqual(associazione.data_costituzione, date(2020, 1, 1))
        self.assertEqual(associazione.note, 'Note di test')
