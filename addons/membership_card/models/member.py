# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import re


class Member(models.Model):
    _name = 'membership.member'
    _description = 'Membro dell\'Associazione'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Informazioni base
    name = fields.Char(string='Nome Completo', required=True, tracking=True)
    first_name = fields.Char(string='Nome', tracking=True)
    last_name = fields.Char(string='Cognome', tracking=True)
    
    # Nome di elezione (per persone trans)
    use_chosen_name = fields.Boolean(string='Usa Nome di Elezione', default=False,
                                    help='Seleziona se preferisci usare un nome di elezione invece del nome legale',
                                    tracking=True)
    chosen_first_name = fields.Char(string='Nome di Elezione', tracking=True,
                                   help='Nome di elezione (chosen name) per persone trans',
                                   attrs="{'invisible': [('use_chosen_name', '=', False)], 'required': [('use_chosen_name', '=', True)]}")
    chosen_last_name = fields.Char(string='Cognome di Elezione', tracking=True,
                                  help='Cognome di elezione se diverso da quello legale',
                                  attrs="{'invisible': [('use_chosen_name', '=', False)]}")
    display_name = fields.Char(string='Nome da Visualizzare', compute='_compute_display_name', store=True,
                              help='Nome che verrà visualizzato (nome di elezione se presente, altrimenti nome legale)')
    
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Telefono', tracking=True)
    mobile = fields.Char(string='Cellulare', tracking=True)
    
    # Dati anagrafici
    birth_date = fields.Date(string='Data di Nascita', tracking=True)
    birth_place = fields.Char(string='Luogo di Nascita', tracking=True)
    birth_state_id = fields.Many2one('res.country.state', string='Provincia di Nascita',
                                     domain="[('country_id', '=', country_id)]")
    birth_country_id = fields.Many2one('res.country', string='Paese di Nascita',
                                       default=lambda self: self.env.ref('base.it').id)
    gender = fields.Selection([
        ('male', 'Maschio'),
        ('female', 'Femmina'),
        ('non_binary', 'Non Binario'),
        ('trans_male', 'Trans Maschio'),
        ('trans_female', 'Trans Femmina'),
        ('other', 'Altro'),
        ('prefer_not_to_say', 'Preferisco non dirlo'),
    ], string='Genere', tracking=True,
    help='Genere di elezione della persona')
    nationality = fields.Many2one('res.country', string='Nazionalità',
                                 default=lambda self: self.env.ref('base.it').id)
    
    # Residenza (indirizzo principale)
    residence_street = fields.Char(string='Via (Residenza)', tracking=True)
    residence_street2 = fields.Char(string='Via 2 (Residenza)')
    residence_city = fields.Char(string='Città (Residenza)', tracking=True)
    residence_state_id = fields.Many2one('res.country.state', string='Provincia (Residenza)',
                                         domain="[('country_id', '=', residence_country_id)]")
    residence_zip = fields.Char(string='CAP (Residenza)', tracking=True)
    residence_country_id = fields.Many2one('res.country', string='Paese (Residenza)',
                                           default=lambda self: self.env.ref('base.it').id)
    
    # Domicilio (se diverso dalla residenza)
    domicile_different = fields.Boolean(string='Domicilio Diverso dalla Residenza', default=False)
    domicile_street = fields.Char(string='Via (Domicilio)',
                                 attrs="{'invisible': [('domicile_different', '=', False)], 'required': [('domicile_different', '=', True)]}")
    domicile_street2 = fields.Char(string='Via 2 (Domicilio)',
                                  attrs="{'invisible': [('domicile_different', '=', False)]}")
    domicile_city = fields.Char(string='Città (Domicilio)',
                               attrs="{'invisible': [('domicile_different', '=', False)], 'required': [('domicile_different', '=', True)]}")
    domicile_state_id = fields.Many2one('res.country.state', string='Provincia (Domicilio)',
                                       domain="[('country_id', '=', domicile_country_id)]",
                                       attrs="{'invisible': [('domicile_different', '=', False)]}")
    domicile_zip = fields.Char(string='CAP (Domicilio)',
                              attrs="{'invisible': [('domicile_different', '=', False)]}")
    domicile_country_id = fields.Many2one('res.country', string='Paese (Domicilio)',
                                          default=lambda self: self.env.ref('base.it').id,
                                          attrs="{'invisible': [('domicile_different', '=', False)]}")
    
    # Indirizzo (per retrocompatibilità - usa residenza)
    street = fields.Char(string='Via', compute='_compute_street', inverse='_inverse_street', store=True)
    street2 = fields.Char(string='Via 2', compute='_compute_street', inverse='_inverse_street', store=True)
    city = fields.Char(string='Città', compute='_compute_street', inverse='_inverse_street', store=True)
    state_id = fields.Many2one('res.country.state', string='Provincia',
                               compute='_compute_street', inverse='_inverse_street', store=True,
                               domain="[('country_id', '=', country_id)]")
    zip = fields.Char(string='CAP', compute='_compute_street', inverse='_inverse_street', store=True)
    country_id = fields.Many2one('res.country', string='Paese',
                                compute='_compute_street', inverse='_inverse_street', store=True,
                                default=lambda self: self.env.ref('base.it').id)
    
    # Dati fiscali italiani
    fiscal_code = fields.Char(string='Codice Fiscale', required=True, tracking=True,
                             help='Codice Fiscale italiano (obbligatorio per associazioni no profit)')
    vat = fields.Char(string='P.IVA', tracking=True,
                     help='Partita IVA (per membri aziendali)')
    is_company = fields.Boolean(string='È un\'Azienda', default=False, tracking=True)
    
    # Dati professionali
    profession = fields.Char(string='Professione', tracking=True)
    company_name = fields.Char(string='Ragione Sociale', tracking=True,
                              attrs="{'invisible': [('is_company', '=', False)], 'required': [('is_company', '=', True)]}")
    
    # Dati associazione no profit
    registration_date = fields.Date(string='Data Iscrizione', required=True,
                                  default=fields.Date.today, tracking=True,
                                  help='Data di iscrizione all\'associazione')
    role_in_association = fields.Selection([
        ('member', 'Socio'),
        ('founder', 'Socio Fondatore'),
        ('honorary', 'Socio Onorario'),
        ('board', 'Consiglio Direttivo'),
        ('president', 'Presidente'),
        ('vice_president', 'Vice Presidente'),
        ('secretary', 'Segretario'),
        ('treasurer', 'Tesoriere'),
        ('other', 'Altro'),
    ], string='Ruolo nell\'Associazione', default='member', tracking=True)
    role_other = fields.Char(string='Ruolo Altro', 
                            attrs="{'invisible': [('role_in_association', '!=', 'other')], 'required': [('role_in_association', '==', 'other')]}")
    
    # Consensi GDPR e Privacy (obbligatori per associazioni italiane)
    privacy_consent = fields.Boolean(string='Consenso Privacy', required=True, default=False,
                                    tracking=True, help='Consenso al trattamento dei dati personali (GDPR)')
    privacy_consent_date = fields.Datetime(string='Data Consenso Privacy', tracking=True)
    marketing_consent = fields.Boolean(string='Consenso Comunicazioni', default=False,
                                     tracking=True, help='Consenso a ricevere comunicazioni promozionali')
    marketing_consent_date = fields.Datetime(string='Data Consenso Comunicazioni', tracking=True)
    data_processing_consent = fields.Boolean(string='Consenso Trattamento Dati', required=True,
                                           default=False, tracking=True,
                                           help='Consenso al trattamento dei dati per finalità associative')
    data_processing_consent_date = fields.Datetime(string='Data Consenso Trattamento Dati', tracking=True)
    
    # Membership
    membership_type_id = fields.Many2one('membership.type', string='Tipo Membership',
                                         required=True, tracking=True)
    membership_start_date = fields.Date(string='Data Inizio', required=True,
                                       default=fields.Date.today, tracking=True)
    membership_end_date = fields.Date(string='Data Scadenza', compute='_compute_end_date',
                                     store=True, tracking=True)
    is_active = fields.Boolean(string='Attivo', compute='_compute_is_active', store=True)
    is_expired = fields.Boolean(string='Scaduto', compute='_compute_is_active', store=True)
    
    # Card
    card_ids = fields.One2many('membership.card', 'member_id', string='Card')
    active_card_id = fields.Many2one('membership.card', string='Card Attiva',
                                    compute='_compute_active_card', store=True)
    card_number = fields.Char(string='Numero Card', related='active_card_id.card_number', store=True)
    
    # Note
    notes = fields.Text(string='Note')
    
    # Statistiche
    total_renewals = fields.Integer(string='Rinnovi Totali', compute='_compute_renewals')
    age = fields.Integer(string='Età', compute='_compute_age')
    
    # Campi computed per nome di elezione
    @api.depends('first_name', 'last_name', 'chosen_first_name', 'chosen_last_name', 'use_chosen_name', 'name')
    def _compute_display_name(self):
        for record in self:
            if record.use_chosen_name and record.chosen_first_name:
                # Usa il nome di elezione
                chosen_name = f"{record.chosen_first_name}"
                if record.chosen_last_name:
                    chosen_name += f" {record.chosen_last_name}"
                else:
                    # Se non c'è cognome di elezione, usa quello legale
                    chosen_name += f" {record.last_name}" if record.last_name else ""
                record.display_name = chosen_name.strip()
            else:
                # Usa il nome legale o il campo name se già compilato
                if record.first_name or record.last_name:
                    legal_name = f"{record.first_name or ''} {record.last_name or ''}".strip()
                    record.display_name = legal_name
                else:
                    record.display_name = record.name or ""
    
    # Campi computed per retrocompatibilità indirizzo
    @api.depends('residence_street', 'residence_street2', 'residence_city', 
                 'residence_state_id', 'residence_zip', 'residence_country_id')
    def _compute_street(self):
        for record in self:
            record.street = record.residence_street
            record.street2 = record.residence_street2
            record.city = record.residence_city
            record.state_id = record.residence_state_id
            record.zip = record.residence_zip
            record.country_id = record.residence_country_id
    
    def _inverse_street(self):
        for record in self:
            record.residence_street = record.street
            record.residence_street2 = record.street2
            record.residence_city = record.city
            record.residence_state_id = record.state_id
            record.residence_zip = record.zip
            record.residence_country_id = record.country_id
    
    @api.depends('birth_date')
    def _compute_age(self):
        today = fields.Date.today()
        for record in self:
            if record.birth_date:
                record.age = (today - record.birth_date).days // 365
            else:
                record.age = 0
    
    @api.depends('membership_start_date', 'membership_type_id.duration_months')
    def _compute_end_date(self):
        for record in self:
            if record.membership_start_date and record.membership_type_id:
                start = fields.Date.from_string(record.membership_start_date)
                months = record.membership_type_id.duration_months
                # Calcola la data di scadenza aggiungendo i mesi
                if months:
                    year = start.year + (start.month + months - 1) // 12
                    month = ((start.month + months - 1) % 12) + 1
                    # Calcolo giorni del mese con controllo anno bisestile corretto
                    # Anno bisestile: divisibile per 4, ma non per 100, oppure divisibile per 400
                    is_leap_year = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                    days_in_month = [31, 29 if is_leap_year else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
                    day = min(start.day, days_in_month)
                    record.membership_end_date = fields.Date.to_string(datetime(year, month, day))
            else:
                record.membership_end_date = False
    
    @api.depends('membership_end_date')
    def _compute_is_active(self):
        today = fields.Date.today()
        for record in self:
            if record.membership_end_date:
                record.is_active = record.membership_end_date >= today
                record.is_expired = record.membership_end_date < today
            else:
                record.is_active = False
                record.is_expired = False
    
    @api.depends('card_ids', 'card_ids.is_active')
    def _compute_active_card(self):
        for record in self:
            active_card = record.card_ids.filtered(lambda c: c.is_active)
            record.active_card_id = active_card[0] if active_card else False
    
    def _compute_renewals(self):
        for record in self:
            # Conta quante volte è stata rinnovata la membership
            # (semplificato: conta le card emesse - 1)
            record.total_renewals = max(0, len(record.card_ids) - 1)
    
    @api.constrains('fiscal_code')
    def _check_fiscal_code(self):
        for record in self:
            if record.fiscal_code:
                cf_upper = record.fiscal_code.upper().strip()
                # Validazione codice fiscale italiano
                # Formato: 6 lettere, 2 cifre, 1 lettera, 2 cifre, 1 lettera, 3 cifre, 1 lettera
                if not re.match(r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$', cf_upper):
                    raise ValidationError(
                        'Il Codice Fiscale non è valido. '
                        'Deve essere nel formato italiano (16 caratteri alfanumerici).'
                    )
                # Verifica unicità (escludendo se stesso)
                existing = self.env['membership.member'].search([
                    ('fiscal_code', '=', cf_upper),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        f'Il Codice Fiscale {cf_upper} è già utilizzato da un altro membro.'
                    )
    
    @api.constrains('privacy_consent', 'data_processing_consent')
    def _check_consents(self):
        for record in self:
            if not record.privacy_consent:
                raise ValidationError(
                    'Il consenso al trattamento dei dati personali (Privacy) è obbligatorio per le associazioni no profit italiane.'
                )
            if not record.data_processing_consent:
                raise ValidationError(
                    'Il consenso al trattamento dei dati per finalità associative è obbligatorio.'
                )
    
    @api.model
    def create(self, vals):
        # Imposta automaticamente le date dei consensi se non specificate
        if vals.get('privacy_consent') and not vals.get('privacy_consent_date'):
            vals['privacy_consent_date'] = fields.Datetime.now()
        if vals.get('data_processing_consent') and not vals.get('data_processing_consent_date'):
            vals['data_processing_consent_date'] = fields.Datetime.now()
        if vals.get('marketing_consent') and not vals.get('marketing_consent_date'):
            vals['marketing_consent_date'] = fields.Datetime.now()
        
        # Gestisce il nome: se non specificato, genera da nome/cognome o nome di elezione
        if not vals.get('name'):
            if vals.get('use_chosen_name') and vals.get('chosen_first_name'):
                # Usa nome di elezione
                chosen_name = vals.get('chosen_first_name', '')
                if vals.get('chosen_last_name'):
                    chosen_name += f" {vals.get('chosen_last_name')}"
                elif vals.get('last_name'):
                    chosen_name += f" {vals.get('last_name')}"
                vals['name'] = chosen_name.strip()
            elif vals.get('first_name') or vals.get('last_name'):
                # Usa nome legale
                vals['name'] = f"{vals.get('first_name', '')} {vals.get('last_name', '')}".strip()
        
        return super(Member, self).create(vals)
    
    def write(self, vals):
        # Aggiorna le date dei consensi quando vengono modificati
        if 'privacy_consent' in vals and vals['privacy_consent'] and not vals.get('privacy_consent_date'):
            vals['privacy_consent_date'] = fields.Datetime.now()
        if 'data_processing_consent' in vals and vals['data_processing_consent'] and not vals.get('data_processing_consent_date'):
            vals['data_processing_consent_date'] = fields.Datetime.now()
        if 'marketing_consent' in vals and vals['marketing_consent'] and not vals.get('marketing_consent_date'):
            vals['marketing_consent_date'] = fields.Datetime.now()
        
        # Aggiorna nome solo se non è stato esplicitamente modificato dall'utente
        # e se sono stati modificati i campi che compongono il nome
        if 'name' not in vals and ('use_chosen_name' in vals or 'chosen_first_name' in vals or 'chosen_last_name' in vals or 'first_name' in vals or 'last_name' in vals):
            # Processa ogni record individualmente per gestire correttamente i batch
            for record in self:
                record_vals = {}
                use_chosen = vals.get('use_chosen_name', record.use_chosen_name)
                if use_chosen:
                    chosen_first = vals.get('chosen_first_name', record.chosen_first_name)
                    chosen_last = vals.get('chosen_last_name', record.chosen_last_name)
                    last_name = vals.get('last_name', record.last_name)
                    if chosen_first:
                        if chosen_last:
                            record_vals['name'] = f"{chosen_first} {chosen_last}".strip()
                        elif last_name:
                            record_vals['name'] = f"{chosen_first} {last_name}".strip()
                        else:
                            record_vals['name'] = chosen_first
                else:
                    first = vals.get('first_name', record.first_name)
                    last = vals.get('last_name', record.last_name)
                    if first or last:
                        record_vals['name'] = f"{first} {last}".strip()
                
                # Applica le modifiche al singolo record se necessario
                if record_vals:
                    record.write(record_vals)
        
        return super(Member, self).write(vals)
    
    @api.constrains('vat')
    def _check_vat(self):
        for record in self:
            if record.vat and record.membership_type_id.requires_vat and record.is_company:
                # Validazione base P.IVA italiana (11 cifre)
                vat_clean = record.vat.replace('IT', '').replace(' ', '')
                if not vat_clean.isdigit() or len(vat_clean) != 11:
                    raise ValidationError('La P.IVA non è valida. Deve essere un numero di 11 cifre.')
    
    def action_renew_membership(self):
        """Rinnova la membership del membro"""
        self.ensure_one()
        # Crea una nuova card per il rinnovo
        new_card = self.env['membership.card'].create({
            'member_id': self.id,
            'membership_type_id': self.membership_type_id.id,
            'issue_date': fields.Date.today(),
        })
        # Aggiorna la data di inizio
        self.membership_start_date = fields.Date.today()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Card Rinnovata',
            'res_model': 'membership.card',
            'res_id': new_card.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_generate_card(self):
        """Genera una nuova card per il membro"""
        self.ensure_one()
        if not self.active_card_id:
            card = self.env['membership.card'].create({
                'member_id': self.id,
                'membership_type_id': self.membership_type_id.id,
                'issue_date': fields.Date.today(),
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Card Generata',
                'res_model': 'membership.card',
                'res_id': card.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Attenzione',
                'message': 'Il membro ha già una card attiva.',
                'type': 'warning',
            }
        }

