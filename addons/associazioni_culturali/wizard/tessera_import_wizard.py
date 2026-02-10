# -*- coding: utf-8 -*-

import base64
import csv
import io
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError


class TesseraImportWizard(models.TransientModel):
    _name = "tessera.import.wizard"
    _description = "Importa tessere da CSV"

    associazione_id = fields.Many2one(
        "associazione.culturale",
        string="Associazione",
        required=True,
        domain=[("attivo", "=", True)],
    )
    piano_id = fields.Many2one(
        "piano.tesseramento",
        string="Piano Tesseramento",
        required=True,
        domain=[("attivo", "=", True)],
    )
    data_file = fields.Binary(string="File CSV", required=True, attachment=False)
    filename = fields.Char(string="Nome file")
    invia_email_conferma = fields.Boolean(
        string="Invia email di conferma ai soci",
        default=False,
    )
    stato_import = fields.Char(string="Esito", readonly=True)

    def _normalize_email(self, email):
        return (email or "").strip().lower() if email else ""

    def _normalize_cf(self, cf):
        if not cf or not str(cf).strip():
            return ""
        return "".join(c for c in str(cf).upper().strip() if c.isalnum())

    def _escape_ilike(self, value):
        """Escape % and _ for use in ilike so they are not treated as wildcards."""
        if not value:
            return ""
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    def _find_or_create_associato(self, row, Associato):
        email = self._normalize_email(row.get("email") or row.get("Email") or "")
        cf = self._normalize_cf(row.get("codice_fiscale") or row.get("codice fiscale") or row.get("cf") or "")
        nome = (row.get("nome_legale") or row.get("nome") or "").strip()
        cognome = (row.get("cognome_legale") or row.get("cognome") or "").strip()
        if email:
            # Match esatto case-insensitive senza wildcard: LOWER(email)=LOWER(%s) evita che
            # _ e % in ILIKE vengano interpretati come wildcard (email con underscore/percentuale sono valide RFC)
            self.env.cr.execute(
                "SELECT id FROM " + Associato._table + " WHERE LOWER(email) = LOWER(%s) LIMIT 1",
                (email,),
            )
            row = self.env.cr.fetchone()
            if row:
                associato = Associato.browse(row[0])
                if associato.exists():
                    return associato, False
        if cf:
            associato = Associato.search([("codice_fiscale", "=", cf)], limit=1)
            if associato:
                return associato, False
        if not email:
            raise ValidationError(_("Riga senza email né associato esistente."))
        vals = {"email": email, "nome_legale": nome or False, "cognome_legale": cognome or False}
        if cf:
            vals["codice_fiscale"] = cf
        return Associato.create(vals), True

    def _parse_date(self, value):
        if not value or not str(value).strip():
            return fields.Date.today()
        s = str(value).strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return fields.Date.today()

    def action_import(self):
        self.ensure_one()
        if not self.associazione_id or not self.piano_id or not self.data_file:
            raise UserError(_("Seleziona associazione, piano e carica un file CSV."))
        try:
            data = base64.b64decode(self.data_file)
        except Exception as e:
            raise UserError(_("File non valido: %s") % str(e))
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = data.decode("latin-1", errors="replace")
        reader = csv.DictReader(io.StringIO(text), delimiter=";")
        if not reader.fieldnames:
            reader = csv.DictReader(io.StringIO(text), delimiter=",")
        if not reader.fieldnames:
            raise UserError(_("CSV senza intestazioni. Colonne: email, codice_fiscale, nome_legale, cognome_legale, data_emissione."))
        Associato = self.env["associato"].sudo()
        Tessera = self.env["tessera"].sudo()
        created_associati = 0
        created_tessere = 0
        errors = []
        for i, row in enumerate(reader, start=2):
            if not any(v and str(v).strip() for v in (row or {}).values()):
                continue
            try:
                associato, is_new = self._find_or_create_associato(row, Associato)
                if is_new:
                    created_associati += 1
                data_emissione = self._parse_date(
                    row.get("data_emissione") or row.get("data emissione") or row.get("Data emissione") or ""
                )
                Tessera.create({
                    "associazione_id": self.associazione_id.id,
                    "piano_id": self.piano_id.id,
                    "associato_id": associato.id,
                    "data_emissione": data_emissione,
                    "invia_email_conferma": self.invia_email_conferma,
                })
                created_tessere += 1
            except Exception as e:
                errors.append("Riga %s: %s" % (i, str(e)))
        if errors:
            self.stato_import = _("Importate %s tessere, %s nuovi associati. Errori: ") % (created_tessere, created_associati) + "; ".join(errors[:15])
        else:
            self.stato_import = _("Importate %s tessere. Creati %s nuovi associati.") % (created_tessere, created_associati)
        return {
            "type": "ir.actions.act_window",
            "res_model": "tessera.import.wizard",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
