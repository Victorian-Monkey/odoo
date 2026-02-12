# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResComune(models.Model):
    _name = "res.comune"
    _description = "Comune"
    _order = "name"

    name = fields.Char(string="Nome", required=True, index=True)
    codice_catastale = fields.Char(string="Codice Catastale", required=True, index=True)
    provincia = fields.Char(string="Provincia", size=2)
    codice_istat = fields.Char(string="Codice ISTAT")
    cap = fields.Char(string="CAP")
    active = fields.Boolean(default=True, string="Attivo")

    _sql_constraints = [
        (
            "codice_catastale_uniq",
            "unique(codice_catastale)",
            "Il Codice Catastale deve essere univoco!",
        ),
    ]

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                ("name", operator, name),
                ("codice_catastale", operator, name),
            ]
        return self._search(domain + args, limit=limit)  # Restituisce una lista di ID

    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.provincia:
                name = f"{name} ({record.provincia})"
            result.append((record.id, name))
        return result
