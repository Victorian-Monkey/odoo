# -*- coding: utf-8 -*-

import base64
import csv
import io

from odoo.tests.common import TransactionCase
from datetime import date


class TestTesseraImportWizard(TransactionCase):

    def setUp(self):
        super(TestTesseraImportWizard, self).setUp()
        self.Wizard = self.env["tessera.import.wizard"]
        self.Associato = self.env["associato"]
        self.Tessera = self.env["tessera"]
        self.Associazione = self.env["associazione.culturale"]
        self.Piano = self.env["piano.tesseramento"]

        self.company = self.env["res.partner"].create({
            "name": "Test Company",
            "is_company": True,
        })
        self.associazione = self.Associazione.create({
            "name": "Test Associazione",
            "company_id": self.company.id,
            "attivo": True,
        })
        self.piano = self.Piano.create({
            "name": "Piano 2024",
            "tipo": "annuale_solare",
            "costo_tessera": 50.0,
            "anno_riferimento": 2024,
            "attivo": True,
        })

    def _make_csv(self, rows, delimiter=";"):
        """Build CSV bytes with header email;codice_fiscale;nome_legale;cognome_legale;data_emissione."""
        out = io.StringIO()
        writer = csv.DictWriter(
            out,
            fieldnames=["email", "codice_fiscale", "nome_legale", "cognome_legale", "data_emissione"],
            delimiter=delimiter,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return base64.b64encode(out.getvalue().encode("utf-8"))

    def test_import_finds_associato_with_underscore_email(self):
        """Import con email contenente underscore trova l'associato esistente (nessun duplicato)."""
        associato = self.Associato.create({
            "email": "john_doe@test.com",
            "nome_legale": "John",
            "cognome_legale": "Doe",
            "no_codice_fiscale": True,
            "country_id": self.env.ref("base.it").id,
        })
        csv_data = self._make_csv([{
            "email": "john_doe@test.com",
            "codice_fiscale": "",
            "nome_legale": "John",
            "cognome_legale": "Doe",
            "data_emissione": "01/01/2024",
        }])
        wizard = self.Wizard.create({
            "associazione_id": self.associazione.id,
            "piano_id": self.piano.id,
            "data_file": csv_data,
            "filename": "test.csv",
        })
        wizard.action_import()
        self.assertIn("0 nuovi associati", wizard.stato_import)
        tessere = self.Tessera.search([
            ("associato_id", "=", associato.id),
            ("associazione_id", "=", self.associazione.id),
        ])
        self.assertEqual(len(tessere), 1)
        self.assertEqual(tessere.associato_id, associato)

    def test_import_underscore_email_does_not_match_similar_without_underscore(self):
        """Import con john_doe@test.com non deve matchare johnaoe@test.com (match esatto, non wildcard)."""
        associato_underscore = self.Associato.create({
            "email": "john_doe@test.com",
            "nome_legale": "John",
            "cognome_legale": "Doe",
            "no_codice_fiscale": True,
            "country_id": self.env.ref("base.it").id,
        })
        associato_no_underscore = self.Associato.create({
            "email": "johnaoe@test.com",
            "nome_legale": "Johna",
            "cognome_legale": "Oe",
            "no_codice_fiscale": True,
            "country_id": self.env.ref("base.it").id,
        })
        csv_data = self._make_csv([{
            "email": "john_doe@test.com",
            "codice_fiscale": "",
            "nome_legale": "John",
            "cognome_legale": "Doe",
            "data_emissione": "01/01/2024",
        }])
        wizard = self.Wizard.create({
            "associazione_id": self.associazione.id,
            "piano_id": self.piano.id,
            "data_file": csv_data,
            "filename": "test.csv",
        })
        wizard.action_import()
        tessere_underscore = self.Tessera.search([
            ("associato_id", "=", associato_underscore.id),
            ("associazione_id", "=", self.associazione.id),
        ])
        tessere_no_underscore = self.Tessera.search([
            ("associato_id", "=", associato_no_underscore.id),
            ("associazione_id", "=", self.associazione.id),
        ])
        self.assertEqual(len(tessere_underscore), 1)
        self.assertEqual(len(tessere_no_underscore), 0)
