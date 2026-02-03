# -*- coding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Relazione inversa: profili associato reclamati da questo utente (stessa email)
    associato_ids = fields.One2many(
        'associato',
        'user_id',
        string='Profili Associato',
    )
