# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta


class TestAssociato(TransactionCase):

    def setUp(self):
        super(TestAssociato, self).setUp()
        self.Associato = self.env['associato']
        self.Tessera = self.env['tessera']
        self.User = self.env['res.users']
        self.Associazione = self.env['associazione.culturale']
        self.Piano = self.env['piano.tesseramento']

        self.company = self.env['res.partner'].create({
            'name': 'Test Company',
            'is_company': True,
        })
        self.associazione = self.Associazione.create({
            'name': 'Test Associazione',
            'company_id': self.company.id,
            'attivo': True,
        })
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
        self.user = self.User.create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@example.com',
        })
        self.associato = self.Associato.create({
            'email': 'test@example.com',
            'user_id': self.user.id,
            'cognome_legale': 'Rossi',
            'nome_legale': 'Mario',
            'codice_fiscale': 'RSSMRA80A01H501U',  # Rossi Mario 01/01/1980, carattere di controllo corretto
            'data_nascita': date(1980, 1, 1),
            'luogo_nascita': 'Roma',
            'street': 'Via Test 123',
            'city': 'Roma',
            'zip': '00100',
            'country_id': self.env.ref('base.it').id,
            'phone': '1234567890',
        })

    def test_associato_fields(self):
        """Campi anagrafici salvati sull'associato"""
        self.assertEqual(self.associato.email, 'test@example.com')
        self.assertEqual(self.associato.user_id, self.user)
        self.assertEqual(self.associato.codice_fiscale, 'RSSMRA80A01H501U')
        self.assertEqual(self.associato.data_nascita, date(1980, 1, 1))
        self.assertEqual(self.associato.city, 'Roma')

    def test_tessera_attuale_compute(self):
        """Calcolo tessera attuale sull'associato"""
        tessera_attiva = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
            'stato': 'attiva',
        })
        self.associato._compute_tessera_attuale()
        self.assertEqual(self.associato.tessera_attuale_id, tessera_attiva)
        self.assertFalse(self.associato.tessera_in_scadenza)

    def test_tessera_in_scadenza(self):
        """Tessera in scadenza"""
        tessera = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today() - timedelta(days=350),
            'data_scadenza': date.today() + timedelta(days=15),
            'stato': 'attiva',
        })
        self.associato._compute_tessera_attuale()
        self.assertEqual(self.associato.tessera_attuale_id, tessera)
        self.assertTrue(self.associato.tessera_in_scadenza)

    def test_get_tessere_passate(self):
        """Recupero tessere passate"""
        tessera_scaduta = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date(2023, 1, 1),
            'data_scadenza': date(2023, 12, 31),
            'stato': 'scaduta',
        })
        tessera_annullata = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
            'stato': 'annullata',
        })
        tessera_attiva = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_calendario.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
            'data_scadenza': date.today() + timedelta(days=365),
            'stato': 'attiva',
        })
        tessere_passate = self.associato.get_tessere_passate()
        self.assertIn(tessera_scaduta, tessere_passate)
        self.assertIn(tessera_annullata, tessere_passate)
        self.assertNotIn(tessera_attiva, tessere_passate)

    def test_tessere_ids_relation(self):
        """Relazione One2many tessere_ids sull'associato"""
        t1 = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_annuale.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
        })
        t2 = self.Tessera.create({
            'associato_id': self.associato.id,
            'piano_id': self.piano_calendario.id,
            'associazione_id': self.associazione.id,
            'data_emissione': date.today(),
        })
        self.assertIn(t1, self.associato.tessere_ids)
        self.assertIn(t2, self.associato.tessere_ids)
        self.assertEqual(len(self.associato.tessere_ids), 2)

    def test_codice_fiscale_validation_valid(self):
        """Codice fiscale italiano valido (carattere di controllo corretto)"""
        a = self.Associato.create({
            'email': 'cf@test.com',
            'codice_fiscale': 'RSSMRA80A01H501U',
            'country_id': self.env.ref('base.it').id,
        })
        self.assertEqual(a.codice_fiscale, 'RSSMRA80A01H501U')

    def test_codice_fiscale_validation_invalid(self):
        """Codice fiscale non valido"""
        with self.assertRaises(ValidationError):
            self.Associato.create({
                'email': 'cf2@test.com',
                'codice_fiscale': 'INVALID123',
                'country_id': self.env.ref('base.it').id,
            })

    def test_no_codice_fiscale_optional(self):
        """Con no_codice_fiscale il CF non è obbligatorio e la validazione viene saltata"""
        a = self.Associato.create({
            'email': 'nocf@test.com',
            'no_codice_fiscale': True,
            'codice_fiscale': False,
            'country_id': self.env.ref('base.it').id,
        })
        self.assertTrue(a.no_codice_fiscale)
        self.assertFalse(a.codice_fiscale)

    def test_codice_fiscale_coerenza_data_nascita(self):
        """CF incoerente con data di nascita solleva ValidationError"""
        with self.assertRaises(ValidationError):
            self.Associato.create({
                'email': 'cfdate@test.com',
                'codice_fiscale': 'RSSMRA80A01H501U',  # 01/01/1980
                'data_nascita': date(1985, 6, 15),
                'country_id': self.env.ref('base.it').id,
            })

    def test_codice_fiscale_obbligatorio_se_no_flag(self):
        """Se no_codice_fiscale non è segnato, il CF vuoto solleva ValidationError"""
        with self.assertRaises(ValidationError):
            self.Associato.create({
                'email': 'nocf@test.com',
                'codice_fiscale': '',
                'country_id': self.env.ref('base.it').id,
            })

    def test_codice_fiscale_carattere_controllo_errato(self):
        """CF con carattere di controllo errato solleva ValidationError"""
        with self.assertRaises(ValidationError):
            self.Associato.create({
                'email': 'cfctrl@test.com',
                'codice_fiscale': 'RSSMRA80A01H501X',  # X errato, corretto sarebbe U
                'country_id': self.env.ref('base.it').id,
            })

    def test_codice_fiscale_match_cognome(self):
        """CF con parti cognome non coerenti con cognome_legale solleva ValidationError"""
        with self.assertRaises(ValidationError):
            self.Associato.create({
                'email': 'cognome@test.com',
                'cognome_legale': 'Bianchi',
                'codice_fiscale': 'RSSMRA80A01H501U',  # RSS = Rossi, non Bianchi (BNC)
                'country_id': self.env.ref('base.it').id,
            })

    def test_codice_fiscale_match_nome(self):
        """CF con parti nome non coerenti con nome_legale solleva ValidationError"""
        with self.assertRaises(ValidationError):
            self.Associato.create({
                'email': 'nome@test.com',
                'nome_legale': 'Giuseppe',
                'codice_fiscale': 'RSSMRA80A01H501U',  # MRA = Mario, non Giuseppe (GSP)
                'country_id': self.env.ref('base.it').id,
            })

    def test_codice_fiscale_senza_nome_cognome_ok(self):
        """Se nome/cognome legale sono vuoti, il match viene saltato e il CF valido è accettato"""
        a = self.Associato.create({
            'email': 'solo@test.com',
            'codice_fiscale': 'RSSMRA80A01H501U',
            'country_id': self.env.ref('base.it').id,
        })
        self.assertEqual(a.codice_fiscale, 'RSSMRA80A01H501U')

    def test_codice_fiscale_to_birth_date_19xx(self):
        """_codice_fiscale_to_birth_date: due cifre 30-99 -> 19XX (1980, 1930)"""
        Associato = self.env['associato']
        # Anno 80 -> 1980
        self.assertEqual(
            Associato._codice_fiscale_to_birth_date('RSSMRA80A01H501U'),
            date(1980, 1, 1),
        )
        # Anno 30 -> 1930
        self.assertEqual(
            Associato._codice_fiscale_to_birth_date('XXXXXX30A01XXXXX'),
            date(1930, 1, 1),
        )

    def test_codice_fiscale_to_birth_date_20xx(self):
        """_codice_fiscale_to_birth_date: due cifre 00-29 -> 20XX (2003, 2000)"""
        Associato = self.env['associato']
        # Anno 03 -> 2003
        self.assertEqual(
            Associato._codice_fiscale_to_birth_date('XXXXXX03A01XXXXX'),
            date(2003, 1, 1),
        )
        # Anno 00 -> 2000
        self.assertEqual(
            Associato._codice_fiscale_to_birth_date('XXXXXX00A01XXXXX'),
            date(2000, 1, 1),
        )

    def test_codice_fiscale_coerenza_data_nascita_2003(self):
        """Associato nato nel 2003 con CF anno 03 passa la validazione (coerenza CF / data)"""
        a = self.Associato.create({
            'email': 'cf2003@test.com',
            'codice_fiscale': 'RSSMRA03A01H501F',  # 01/01/2003, check digit corretto
            'data_nascita': date(2003, 1, 1),
            'country_id': self.env.ref('base.it').id,
        })
        self.assertEqual(a.codice_fiscale, 'RSSMRA03A01H501F')
        self.assertEqual(a.data_nascita, date(2003, 1, 1))

    def test_action_reclama(self):
        """Reclamo profilo: utente con stessa email può associare"""
        associato_senza_user = self.Associato.create({
            'email': 'test@example.com',
            'user_id': False,
            'no_codice_fiscale': True,
        })
        associato_senza_user.with_user(self.user).action_reclama()
        self.assertEqual(associato_senza_user.user_id, self.user)

    def test_action_reclama_wrong_email(self):
        """Reclamo con email diversa non consentito"""
        other_user = self.User.create({
            'name': 'Other',
            'login': 'other_user',
            'email': 'other@example.com',
        })
        associato = self.Associato.create({
            'email': 'test@example.com',
            'user_id': False,
            'no_codice_fiscale': True,
        })
        with self.assertRaises(UserError):
            associato.with_user(other_user).action_reclama()
        self.assertFalse(associato.user_id)
