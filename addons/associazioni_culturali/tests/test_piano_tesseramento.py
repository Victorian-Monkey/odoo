# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from datetime import date


class TestPianoTesseramento(TransactionCase):

    def setUp(self):
        super(TestPianoTesseramento, self).setUp()
        self.Piano = self.env['piano.tesseramento']
        self.Tessera = self.env['tessera']
        self.Associato = self.env['associato']
        self.User = self.env['res.users']
        self.Associazione = self.env['associazione.culturale']
        
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

    def test_piano_creation_annuale_solare(self):
        """Test creazione piano annuale solare"""
        piano = self.Piano.create({
            'name': 'Piano Annuale 2024',
            'tipo': 'annuale_solare',
            'costo_tessera': 50.0,
            'anno_riferimento': 2024,
            'attivo': True,
        })
        
        self.assertEqual(piano.tipo, 'annuale_solare')
        self.assertEqual(piano.anno_riferimento, 2024)
        self.assertEqual(piano.costo_tessera, 50.0)
        self.assertTrue(piano.attivo)

    def test_piano_creation_calendario(self):
        """Test creazione piano calendario"""
        piano = self.Piano.create({
            'name': 'Piano Calendario',
            'tipo': 'calendario',
            'costo_tessera': 60.0,
            'attivo': True,
        })
        
        self.assertEqual(piano.tipo, 'calendario')
        self.assertFalse(piano.anno_riferimento)
        self.assertEqual(piano.costo_tessera, 60.0)

    def test_anno_riferimento_auto_annuale_solare(self):
        """Test che anno_riferimento sia impostato automaticamente per annuale_solare"""
        anno_corrente = date.today().year
        piano = self.Piano.create({
            'name': 'Piano Annuale',
            'tipo': 'annuale_solare',
            'costo_tessera': 50.0,
        })
        
        self.assertEqual(piano.anno_riferimento, anno_corrente)

    def test_anno_riferimento_not_required_calendario(self):
        """Test che anno_riferimento non sia richiesto per calendario"""
        piano = self.Piano.create({
            'name': 'Piano Calendario',
            'tipo': 'calendario',
            'costo_tessera': 60.0,
        })
        
        # Per calendario, anno_riferimento può essere vuoto
        self.assertFalse(piano.anno_riferimento)

    def test_tessere_ids_relation(self):
        """Test relazione One2many tessere_ids"""
        piano = self.Piano.create({
            'name': 'Piano Test',
            'tipo': 'annuale_solare',
            'costo_tessera': 50.0,
            'anno_riferimento': 2024,
        })
        
        tessera1 = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': piano.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
        })
        
        tessera2 = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': piano.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
        })
        
        self.assertIn(tessera1, piano.tessere_ids)
        self.assertIn(tessera2, piano.tessere_ids)
        self.assertEqual(len(piano.tessere_ids), 2)

    def test_piano_update_anno_riferimento(self):
        """Test aggiornamento anno_riferimento quando si cambia tipo"""
        piano = self.Piano.create({
            'name': 'Piano Test',
            'tipo': 'calendario',
            'costo_tessera': 50.0,
        })
        
        # Cambia a annuale_solare
        piano.write({'tipo': 'annuale_solare'})
        
        # Dovrebbe avere l'anno corrente
        self.assertEqual(piano.anno_riferimento, date.today().year)
