# -*- coding: utf-8 -*-

import re
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

# Tabelle per il carattere di controllo del codice fiscale italiano
# Secondo l'algoritmo ufficiale: https://www.alus.it/pubs/CodiceFiscale/index.php?lang=it
# Valori per caratteri in posizione DISPARI (1, 3, 5, 7, 9, 11, 13, 15)
    "0": 1,
    "1": 0,
    "2": 5,
    "3": 7,
    "4": 9,
    "5": 13,
    "6": 15,
    "7": 17,
    "8": 19,
    "9": 21,
    "A": 1,
    "B": 0,
    "C": 5,
    "D": 7,
    "E": 9,
    "F": 13,
    "G": 15,
    "H": 17,
    "I": 19,
    "J": 21,
    "K": 2,
    "L": 4,
    "M": 18,
    "N": 20,
    "O": 11,
    "P": 3,
    "Q": 6,
    "R": 8,
    "S": 12,
    "T": 14,
    "U": 16,
    "V": 10,
    "W": 22,
    "X": 25,
    "Y": 24,
    "Z": 23,
}
# Valori per caratteri in posizione PARI (2, 4, 6, 8, 10, 12, 14) - doc: 0-25
_CF_EVEN = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 4,
    "F": 5,
    "G": 6,
    "H": 7,
    "I": 8,
    "J": 9,
    "K": 10,
    "L": 11,
    "M": 12,
    "N": 13,
    "O": 14,
    "P": 15,
    "Q": 16,
    "R": 17,
    "S": 18,
    "T": 19,
    "U": 20,
    "V": 21,
    "W": 22,
    "X": 23,
    "Y": 24,
    "Z": 25,
}
_CF_CONTROL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_CF_MONTH = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "H": 6,
    "L": 7,
    "M": 8,
    "P": 9,
    "R": 10,
    "S": 11,
    "T": 12,
}
_CF_YEAR_LETTER = {
    "0": 1900,
    "1": 1901,
    "2": 1902,
    "3": 1903,
    "4": 1904,
    "5": 1905,
    "6": 1906,
    "7": 1907,
    "8": 1908,
    "9": 1909,
    "L": 2000,
    "M": 2001,
    "N": 2002,
    "P": 2003,
    "Q": 2004,
    "R": 2005,
    "S": 2006,
    "T": 2007,
    "U": 2008,
    "V": 2009,
}

# Sostituzione caratteri accentati per il calcolo CF (solo lettere A-Z)
_CF_ACCENT_MAP = {
    "À": "A",
    "Á": "A",
    "Â": "A",
    "Ä": "A",
    "È": "E",
    "É": "E",
    "Ê": "E",
    "Ë": "E",
    "Ì": "I",
    "Í": "I",
    "Î": "I",
    "Ï": "I",
    "Ò": "O",
    "Ó": "O",
    "Ô": "O",
    "Ö": "O",
    "Ù": "U",
    "Ú": "U",
    "Û": "U",
    "Ü": "U",
}
_CF_VOWELS = set("AEIOU")


def _normalize_cf_string(s):
    """Normalizza una stringa per il confronto con le parti nome/cognome del CF: maiuscolo, solo A-Z."""
    if not s or not s.strip():
        return ""
    s = s.upper().strip()
    # Un solo spazio tra parole (cognomi composti), poi rimuovi spazi
    s = " ".join(s.split())
    result = []
    for c in s:
        if c in _CF_ACCENT_MAP:
            result.append(_CF_ACCENT_MAP[c])
        elif "A" <= c <= "Z":
            result.append(c)
    return "".join(result).replace(" ", "")


def _cf_letters_from_surname(surname):
    """
    Ricava le 3 lettere del cognome per il codice fiscale: 1ª, 2ª, 3ª consonante;
    se non bastano, vocali in ordine; se ancora non bastano, padding con X.
    Cognomi composti: considerati come una sola parola (spazi rimossi).
    """
    letters = _normalize_cf_string(surname)
    if not letters:
        return ""
    consonants = [c for c in letters if c not in _CF_VOWELS]
    vowels = [c for c in letters if c in _CF_VOWELS]
    combined = consonants + vowels
    result = (combined + ["X", "X", "X"])[:3]
    return "".join(result)


def _cf_letters_from_name(name):
    """
    Ricava le 3 lettere del nome per il codice fiscale: 1ª, 3ª e 4ª consonante;
    se le consonanti sono meno di 4, si prendono le prime 3; se meno di 3,
    stesso criterio del cognome (consonanti + vocali + X).
    """
    letters = _normalize_cf_string(name)
    if not letters:
        return ""
    consonants = [c for c in letters if c not in _CF_VOWELS]
    vowels = [c for c in letters if c in _CF_VOWELS]
    if len(consonants) >= 4:
        result = [consonants[0], consonants[2], consonants[3]]
    elif len(consonants) >= 3:
        result = consonants[:3]
    else:
        combined = consonants + vowels
        result = (combined + ["X", "X", "X"])[:3]
    return "".join(result)


class Associato(models.Model):
    _name = "associato"
    _description = _("Associato")
    _order = "email, id"

    name = fields.Char(
        string="Nome", compute="_compute_name", store=True, readonly=True
    )
    email = fields.Char(string="Email", required=True, index=True)
    nome_legale = fields.Char(string="Nome legale")
    cognome_legale = fields.Char(string="Cognome legale")
    nome_elezione = fields.Char(
        string="Nome di elezione",
        help="Nome con cui la persona desidera essere indicata (es. nome d'arte, nome scelto).",
    )
    user_id = fields.Many2one(
        "res.users",
        string="Utente collegato",
        ondelete="set null",
        help="Utente che ha reclamato questo profilo (stessa email). Vuoto se non ancora associato.",
    )
    codice_fiscale = fields.Char(string="Codice Fiscale")
    no_codice_fiscale = fields.Boolean(
        string="Non ho residenza italiana / codice fiscale",
        default=False,
        help="Spuntare se non si possiede codice fiscale italiano (es. non residenti in Italia).",
    )
    data_nascita = fields.Date(string="Data di Nascita")
    luogo_nascita = fields.Char(string="Luogo di Nascita")
    comune_nascita_id = fields.Many2one("res.comune", string="Comune di Nascita")
    street = fields.Char(string="Via")
    street2 = fields.Char(string="Via 2")
    city = fields.Char(string="Città")
    zip = fields.Char(string="CAP")
    state_id = fields.Many2one("res.country.state", string="Provincia")
    country_id = fields.Many2one(
        "res.country",
        string="Paese",
        default=lambda self: self.env.ref("base.it", raise_if_not_found=False),
    )
    phone = fields.Char(string="Telefono")

    tessere_ids = fields.One2many(
        "tessera", "associato_id", string="Tessere", readonly=True
    )

    tessera_attuale_id = fields.Many2one(
        "tessera",
        string="Tessera Attuale",
        compute="_compute_tessera_attuale",
        store=False,
    )
    tessera_in_scadenza = fields.Boolean(
        string="Tessera in Scadenza",
        compute="_compute_tessera_attuale",
        store=False,
    )

    @api.depends("email", "nome_elezione", "cognome_legale")
    def _compute_name(self):
        for record in self:
            parts = []
            if record.nome_elezione:
                parts.append(record.nome_elezione.strip())
            if record.cognome_legale:
                parts.append(record.cognome_legale.strip())
            display = " ".join(parts) if parts else ""
            email = (record.email or "").strip()
            if display and email:
                record.name = f"{display} ({email})"
            elif email:
                record.name = email
            else:
                record.name = _("Nuovo Associato")

    @api.onchange("codice_fiscale")
    def _onchange_codice_fiscale(self):
        """Pulisce il codice fiscale rimuovendo spazi e caratteri non validi."""
        if self.codice_fiscale:
            # Pulisci il codice fiscale: rimuovi spazi, trattini e altri caratteri non validi
            cf_raw = self.codice_fiscale.upper().strip()
            # Rimuovi tutti i caratteri non alfanumerici
            cf_clean = "".join(c for c in cf_raw if c.isalnum())
            if cf_clean != cf_raw:
                self.codice_fiscale = cf_clean

    @api.onchange("comune_nascita_id")
    def _onchange_comune_nascita_id(self):
        if self.comune_nascita_id:
            self.luogo_nascita = self.comune_nascita_id.name

    @api.constrains(
        "codice_fiscale",
        "no_codice_fiscale",
        "data_nascita",
        "nome_legale",
        "cognome_legale",
        "comune_nascita_id",
    )
    def _check_codice_fiscale(self):
        """Valida formato, carattere di controllo, coerenza con data di nascita e match con cognome/nome."""
        for record in self:
            # Se ha segnato "non ho codice fiscale", il CF non è obbligatorio e non si valida
            if record.no_codice_fiscale:
                continue
            # Se non ha segnato "non ho codice fiscale" ma il CF è vuoto -> errore
            if not record.codice_fiscale or not record.codice_fiscale.strip():
                raise ValidationError(
                    _(
                        'Il codice fiscale è obbligatorio. Se non sei residente in Italia, spunta "Non ho residenza italiana / codice fiscale".'
                    )
                )
            # Pulizia CF
            cf = record.codice_fiscale.upper().strip()
            cf = "".join(c for c in cf if c.isalnum())
            if len(cf) != 16:
                raise ValidationError(
                    _("Il codice fiscale deve essere esattamente di 16 caratteri.")
                )
            if not re.match(
                r"^[A-Z]{6}[0-9LMNPQRSTUV]{2}[ABCDEHLMPRST][0-9LMNPQRSTUV]{2}[A-Z][0-9LMNPQRSTUV]{3}[A-Z]$",
                cf,
            ):
                raise ValidationError(
                    _(
                        "Il codice fiscale non è valido: formato non corretto. "
                        "Verifica i 16 caratteri (lettere e numeri secondo lo standard italiano)."
                    )
                )
            # Carattere di controllo (posizioni 1-15: dispari usano _CF_ODD, pari usano _CF_EVEN)
            total = 0
            for i, c in enumerate(cf[:15]):
                total += _CF_EVEN.get(c, 0) if (i + 1) % 2 == 0 else _CF_ODD.get(c, 0)
            expected_control = _CF_CONTROL[total % 26]
            if cf[15] != expected_control:
                raise ValidationError(
                    _("Il codice fiscale non è valido: carattere di controllo errato.")
                )
            # Coerenza con data di nascita se presente
            if record.data_nascita:
                try:
                    cf_date = self._codice_fiscale_to_birth_date(cf)
                    if cf_date != record.data_nascita:
                        raise ValidationError(
                            _(
                                "Il codice fiscale non è coerente con la data di nascita indicata. "
                                "Data nel CF: %s; data indicata: %s."
                            )
                            % (
                                cf_date.strftime("%d/%m/%Y"),
                                record.data_nascita.strftime("%d/%m/%Y"),
                            )
                        )
                except (ValueError, KeyError) as e:
                    raise ValidationError(
                        _(
                            "Impossibile verificare la data di nascita nel codice fiscale: %s"
                        )
                        % str(e)
                    )
            # Match con cognome legale (pos. 1-3 del CF)
            if record.cognome_legale and record.cognome_legale.strip():
                expected_surname = _cf_letters_from_surname(record.cognome_legale)
                if expected_surname and cf[0:3] != expected_surname:
                    raise ValidationError(
                        _(
                            "Il codice fiscale non è coerente con il cognome indicato: "
                            'le prime tre lettere del CF (%s) non corrispondono al cognome "%s".'
                        )
                        % (cf[0:3], record.cognome_legale.strip())
                    )
            # Match con nome legale (pos. 4-6 del CF)
            if record.nome_legale and record.nome_legale.strip():
                expected_name = _cf_letters_from_name(record.nome_legale)
                if expected_name and cf[3:6] != expected_name:
                    raise ValidationError(
                        _(
                            "Il codice fiscale non è coerente con il nome indicato: "
                            'le lettere del nome nel CF (%s) non corrispondono al nome "%s".'
                        )
                        % (cf[3:6], record.nome_legale.strip())
                    )

            if record.comune_nascita_id:
                if record.comune_nascita_id.name == "Estero":
                    if cf[11] != "Z":
                        raise ValidationError(
                            _(
                                "Il codice fiscale non sembra appartenere a una persona nata all'estero (deve contenere la 'Z' nel codice luogo)."
                            )
                        )
                elif record.comune_nascita_id.codice_catastale:
                    expected_code = record.comune_nascita_id.codice_catastale.upper()
                    if cf[11:15] != expected_code:
                        raise ValidationError(
                            _(
                                "Il codice fiscale non corrisponde al comune di nascita indicato (%s). "
                                "Codice nel CF: %s. Codice atteso: %s."
                            )
                            % (
                                record.comune_nascita_id.name,
                                cf[11:15],
                                expected_code,
                            )
                        )

    @api.model
    def _codice_fiscale_to_birth_date(self, cf):
        """Estrae la data di nascita dal codice fiscale (16 caratteri, maiuscolo)."""
        cf = cf.upper().strip()
        if len(cf) < 11:
            raise ValueError(_("Codice fiscale troppo corto"))
        # Anno: pos 7-8. Due cifre: 00-29 -> 2000-2029, 30-99 -> 1930-1999; lettera L-V + cifra -> 2000-2009
        if cf[6].isdigit() and cf[7].isdigit():
            yy = int(cf[6]) * 10 + int(cf[7])
            year = 2000 + yy if yy <= 29 else 1900 + yy
        elif cf[6] in "LMNPQRSTUV" and cf[7].isdigit():
            year = 2000 + int(cf[7])
        else:
            raise ValueError(_("Anno non valido nel CF"))
        month = _CF_MONTH.get(cf[8])
        if not month:
            raise ValueError(_("Mese non valido nel CF"))
        if not (cf[9].isdigit() and cf[10].isdigit()):
            raise ValueError(_("Giorno non valido nel CF"))
        day = int(cf[9]) * 10 + int(cf[10])
        if day > 40:
            day -= 40  # donne: 41-71 -> 1-31
        if day < 1 or day > 31:
            raise ValueError(_("Giorno non valido nel CF"))
        return date(year, month, day)

    @api.depends("tessere_ids", "tessere_ids.stato", "tessere_ids.data_scadenza")
    def _compute_tessera_attuale(self):
        """Calcola la tessera attuale (attiva e non scaduta)"""
        today = fields.Date.today()
        for record in self:
            tessera_attuale = record.tessere_ids.filtered(
                lambda t: (
                    t.stato == "attiva" and t.data_scadenza and t.data_scadenza >= today
                )
            ).sorted("data_scadenza", reverse=True)
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
            lambda t: (
                t.stato in ("scaduta", "annullata")
                or (t.data_scadenza and t.data_scadenza < today)
            )
        ).sorted("data_scadenza", reverse=True)

    def action_reclama(self):
        """Associa questo profilo all'utente corrente se l'email coincide."""
        self.ensure_one()
        user = self.env.user
        if user._is_public():
            raise UserError(_("Devi effettuare l'accesso per reclamare un profilo."))
        email_user = (user.partner_id.email or user.login or "").strip().lower()
        email_associato = (self.email or "").strip().lower()
        if not email_user or email_user != email_associato:
            raise UserError(
                _(
                    "Puoi reclamare solo un profilo associato con la stessa email del tuo account (%s).",
                    user.partner_id.email or user.login,
                )
            )
        if self.user_id and self.user_id != user:
            raise UserError(_("Questo profilo è già associato a un altro utente."))
        self.write({"user_id": user.id})
        return True

    def action_invita_utente(self):
        """
        Crea l'utente (portale) se non esiste, invia l'email di invito e associa l'utente al membro.
        Se l'utente esiste già (stessa email), lo associa e invia comunque l'email di reset password come invito.
        """
        self.ensure_one()
        email = (self.email or "").strip().lower()
        if not email:
            raise UserError(
                _(
                    "Impossibile inviare l'invito: l'associato non ha un indirizzo email."
                )
            )
        if self.user_id:
            # Già collegato: invia di nuovo l'email di reset come "invito a accedere"
            self.user_id.sudo().action_reset_password()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Invito inviato"),
                    "message": _(
                        "È stata inviata un'email a %s con il link per accedere."
                    )
                    % self.email,
                    "type": "success",
                    "sticky": False,
                },
            }
        User = self.env["res.users"].sudo()
        partner_obj = self.env["res.partner"].sudo()
        # Cerca utente esistente con stessa email (login o partner)
        existing = User.search(
            [
                "|",
                ("login", "=", email),
                ("partner_id.email", "=", email),
            ],
            limit=1,
        )
        if existing:
            self.sudo().write({"user_id": existing.id})
            existing.action_reset_password()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Invito inviato"),
                    "message": _(
                        "Utente esistente collegato. È stata inviata un'email a %s con il link per accedere."
                    )
                    % self.email,
                    "type": "success",
                    "sticky": False,
                },
            }
        # Crea nuovo utente portale
        group_portal = self.env.ref("base.group_portal")
        name = (
            " ".join(filter(None, [self.nome_legale, self.cognome_legale])).strip()
            or self.name
            or email
        )
        partner = partner_obj.search([("email", "=", email)], limit=1)
        if not partner:
            partner = partner_obj.create(
                {
                    "name": name,
                    "email": email,
                }
            )
        existing_user = User.search([("partner_id", "=", partner.id)], limit=1)
        if existing_user:
            # Il partner ha già un utente: usalo e collega
            self.sudo().write({"user_id": existing_user.id})
            existing_user.action_reset_password()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Invito inviato"),
                    "message": _("Utente collegato. È stata inviata un'email a %s.")
                    % self.email,
                    "type": "success",
                    "sticky": False,
                },
            }
        # Login deve essere univoco: usa email come login
        user = User.with_context(no_reset_password=False).create(
            {
                "name": name,
                "login": email,
                "partner_id": partner.id,
                "groups_id": [(6, 0, [group_portal.id])],
            }
        )
        self.sudo().write({"user_id": user.id})
        # Invio esplicito email invito (reset password): in alcune versioni non parte in create
        user.action_reset_password()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Invito inviato"),
                "message": _(
                    "È stato creato un utente e inviata un'email a %s con il link per impostare la password e accedere."
                )
                % self.email,
                "type": "success",
                "sticky": False,
                'sticky': False,
            },
        }
