# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
from datetime import date

# Tabelle per il carattere di controllo del codice fiscale italiano
_CF_ODD = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
    'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18,
    'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25,
}
_CF_EVEN = {
    '0': 0, '1': 2, '2': 4, '3': 6, '4': 8, '5': 10, '6': 12, '7': 14, '8': 16, '9': 18,
    'A': 0, 'B': 2, 'C': 4, 'D': 6, 'E': 8, 'F': 10, 'G': 12, 'H': 14, 'I': 16, 'J': 18,
    'K': 20, 'L': 22, 'M': 24, 'N': 26, 'O': 28, 'P': 30, 'Q': 32, 'R': 34, 'S': 36,
    'T': 38, 'U': 40, 'V': 42, 'W': 44, 'X': 46, 'Y': 48, 'Z': 50,
}
_CF_CONTROL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
_CF_MONTH = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'H': 6, 'L': 7, 'M': 8, 'P': 9, 'R': 10, 'S': 11, 'T': 12,
}
_CF_YEAR_LETTER = {
    '0': 1900, '1': 1901, '2': 1902, '3': 1903, '4': 1904, '5': 1905, '6': 1906, '7': 1907, '8': 1908, '9': 1909,
    'L': 2000, 'M': 2001, 'N': 2002, 'P': 2003, 'Q': 2004, 'R': 2005, 'S': 2006, 'T': 2007, 'U': 2008, 'V': 2009,
}


class Associato(models.Model):
    _name = 'associato'
    _description = _('Associato')
    _order = 'email, id'

    name = fields.Char(string='Nome', compute='_compute_name', store=True, readonly=True)
    email = fields.Char(string='Email', required=True, index=True, tracking=True)
    nome_legale = fields.Char(string='Nome legale', tracking=True)
    cognome_legale = fields.Char(string='Cognome legale', tracking=True)
    nome_elezione = fields.Char(
        string='Nome di elezione',
        tracking=True,
        help='Nome con cui la persona desidera essere indicata (es. nome d\'arte, nome scelto).',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Utente collegato',
        ondelete='set null',
        help='Utente che ha reclamato questo profilo (stessa email). Vuoto se non ancora associato.',
    )
    codice_fiscale = fields.Char(string='Codice Fiscale', tracking=True)
    no_codice_fiscale = fields.Boolean(
        string='Non ho residenza italiana / codice fiscale',
        default=False,
        tracking=True,
        help='Spuntare se non si possiede codice fiscale italiano (es. non residenti in Italia).',
    )
    data_nascita = fields.Date(string='Data di Nascita', tracking=True)
    luogo_nascita = fields.Char(string='Luogo di Nascita', tracking=True)
    street = fields.Char(string='Via', tracking=True)
    street2 = fields.Char(string='Via 2', tracking=True)
    city = fields.Char(string='Città', tracking=True)
    zip = fields.Char(string='CAP', tracking=True)
    state_id = fields.Many2one('res.country.state', string='Provincia', tracking=True)
    country_id = fields.Many2one(
        'res.country',
        string='Paese',
        default=lambda self: self.env.ref('base.it', raise_if_not_found=False),
        tracking=True,
    )
    phone = fields.Char(string='Telefono', tracking=True)

    tessere_ids = fields.One2many('tessera', 'associato_id', string='Tessere', readonly=True)

    tessera_attuale_id = fields.Many2one(
        'tessera',
        string='Tessera Attuale',
        compute='_compute_tessera_attuale',
        store=False,
    )
    tessera_in_scadenza = fields.Boolean(
        string='Tessera in Scadenza',
        compute='_compute_tessera_attuale',
        store=False,
    )

    @api.depends('email', 'nome_elezione', 'cognome_legale')
    def _compute_name(self):
        for record in self:
            parts = []
            if record.nome_elezione:
                parts.append(record.nome_elezione.strip())
            if record.cognome_legale:
                parts.append(record.cognome_legale.strip())
            display = ' '.join(parts) if parts else ''
            email = (record.email or '').strip()
            if display and email:
                record.name = f"{display} ({email})"
            elif email:
                record.name = email
            else:
                record.name = _('Nuovo Associato')

    @api.constrains('codice_fiscale', 'no_codice_fiscale', 'data_nascita')
    def _check_codice_fiscale(self):
        """Valida formato, carattere di controllo e coerenza con data di nascita."""
        for record in self:
            if record.no_codice_fiscale or not record.codice_fiscale:
                continue
            cf = record.codice_fiscale.upper().strip()
            if len(cf) != 16:
                raise ValidationError(
                    _('Il codice fiscale deve essere esattamente di 16 caratteri.')
                )
            if not re.match(
                r'^[A-Z]{6}[0-9LMNPQRSTUV]{2}[ABCDEHLMPRST][0-9LMNPQRSTUV]{2}[A-Z][0-9LMNPQRSTUV]{3}[A-Z]$',
                cf,
            ):
                raise ValidationError(
                    _(
                        'Il codice fiscale non è valido: formato non corretto. '
                        'Verifica i 16 caratteri (lettere e numeri secondo lo standard italiano).'
                    )
                )
            # Carattere di controllo (posizione 16, indice 15)
            total = 0
            for i, c in enumerate(cf[:15]):
                total += _CF_EVEN.get(c, 0) if (i + 1) % 2 == 0 else _CF_ODD.get(c, 0)
            expected_control = _CF_CONTROL[total % 26]
            if cf[15] != expected_control:
                raise ValidationError(
                    _('Il codice fiscale non è valido: carattere di controllo errato.')
                )
            # Coerenza con data di nascita se presente
            if record.data_nascita:
                try:
                    cf_date = self._codice_fiscale_to_birth_date(cf)
                    if cf_date != record.data_nascita:
                        raise ValidationError(
                            _(
                                'Il codice fiscale non è coerente con la data di nascita indicata. '
                                'Data nel CF: %s; data indicata: %s.'
                            )
                            % (record.data_nascita.strftime('%d/%m/%Y'), cf_date.strftime('%d/%m/%Y'))
                        )
                except (ValueError, KeyError) as e:
                    raise ValidationError(
                        _('Impossibile verificare la data di nascita nel codice fiscale: %s') % str(e)
                    )

    @api.model
    def _codice_fiscale_to_birth_date(self, cf):
        """Estrae la data di nascita dal codice fiscale (16 caratteri, maiuscolo)."""
        cf = cf.upper().strip()
        if len(cf) < 11:
            raise ValueError('Codice fiscale troppo corto')
        # Anno: pos 7-8. Cifre 00-99 -> 1900-1999; lettera L-V + cifra -> 2000-2009
        if cf[6].isdigit() and cf[7].isdigit():
            year = 1900 + int(cf[6]) * 10 + int(cf[7])
        elif cf[6] in 'LMNPQRSTUV' and cf[7].isdigit():
            year = 2000 + int(cf[7])
        else:
            raise ValueError('Anno non valido nel CF')
        month = _CF_MONTH.get(cf[8])
        if not month:
            raise ValueError('Mese non valido nel CF')
        if not (cf[9].isdigit() and cf[10].isdigit()):
            raise ValueError('Giorno non valido nel CF')
        day = int(cf[9]) * 10 + int(cf[10])
        if day > 40:
            day -= 40  # donne: 41-71 -> 1-31
        if day < 1 or day > 31:
            raise ValueError('Giorno non valido nel CF')
        return date(year, month, day)

    @api.depends('tessere_ids', 'tessere_ids.stato', 'tessere_ids.data_scadenza')
    def _compute_tessera_attuale(self):
        """Calcola la tessera attuale (attiva e non scaduta)"""
        today = fields.Date.today()
        for record in self:
            tessera_attuale = record.tessere_ids.filtered(
                lambda t: t.stato == 'attiva'
                and t.data_scadenza
                and t.data_scadenza >= today
            ).sorted('data_scadenza', reverse=True)
            if tessera_attuale:
                record.tessera_attuale_id = tessera_attuale[0]
                giorni_alla_scadenza = (tessera_attuale[0].data_scadenza - today).days
                record.tessera_in_scadenza = 0 <= giorni_alla_scadenza <= 30
            else:
                record.tessera_attuale_id = False
                record.tessera_in_scadenza = False

    def get_tessere_passate(self):
        """Restituisce le tessere passate (scadute o annullate)"""
        today = fields.Date.today()
        return self.tessere_ids.filtered(
            lambda t: t.stato in ('scaduta', 'annullata')
            or (t.data_scadenza and t.data_scadenza < today)
        ).sorted('data_scadenza', reverse=True)

    def action_reclama(self):
        """Associa questo profilo all'utente corrente se l'email coincide."""
        self.ensure_one()
        user = self.env.user
        if user._is_public():
            raise UserError(_('Devi effettuare l\'accesso per reclamare un profilo.'))
        email_user = (user.partner_id.email or user.login or '').strip().lower()
        email_associato = (self.email or '').strip().lower()
        if not email_user or email_user != email_associato:
            raise UserError(
                _(
                    'Puoi reclamare solo un profilo associato con la stessa email del tuo account (%s).',
                    user.partner_id.email or user.login,
                )
            )
        if self.user_id and self.user_id != user:
            raise UserError(_('Questo profilo è già associato a un altro utente.'))
        self.write({'user_id': user.id})
        return True
