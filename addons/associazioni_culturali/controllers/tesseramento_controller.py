# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
import logging
from types import SimpleNamespace

_logger = logging.getLogger(__name__)


def _mailing_lists_safe(env):
    """Restituisce liste mailing come oggetti con id, name e description (description vuoto se il modello non ce l'ha)."""
    if 'mailing.list' not in env:
        return []
    records = env['mailing.list'].sudo().search([
        ('active', '=', True),
        ('is_public', '=', True),
    ])
    return [
        SimpleNamespace(
            id=m.id,
            name=m.name,
            description=getattr(m, 'description', None) or '',
        )
        for m in records
    ]


class TesseramentoController(http.Controller):

    @http.route('/tesseramento', type='http', auth='public', website=True, methods=['GET'])
    def tesseramento_form(self, **kw):
        """Mostra il form di tesseramento"""
        # Verifica se l'utente è loggato (non guest)
        user = request.env.user
        is_logged_in = user and not user._is_public() and user.id != request.website.user_id.id
        
        # Ottieni associazioni attive
        associazioni = request.env['associazione.culturale'].sudo().search([
            ('attivo', '=', True)
        ])
        
        # Ottieni piani di tesseramento attivi
        piani = request.env['piano.tesseramento'].sudo().search([
            ('attivo', '=', True)
        ])
        
        # Liste mailing con solo id/name (compatibile con versioni senza campo description)
        mailing_lists = _mailing_lists_safe(request.env)
        
        values = {
            'associazioni': associazioni,
            'piani': piani,
            'is_logged_in': is_logged_in,
            'user': user if is_logged_in else None,
            'mailing_lists': mailing_lists,
        }
        
        return request.render('associazioni_culturali.tesseramento_form', values)

    @http.route('/tesseramento/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def tesseramento_submit(self, **post):
        """Gestisce l'invio del form di tesseramento"""
        try:
            # Verifica se l'utente è loggato (non guest)
            user = request.env.user
            is_logged_in = user and not user._is_public() and user.id != request.website.user_id.id
            
            # Se non è loggato, richiedi login/registrazione
            if not is_logged_in:
                # Salva i dati del form in sessione per recuperarli dopo il login
                request.session['tesseramento_data'] = post
                return request.redirect('/web/login?redirect=/tesseramento')
            
            # Recupera i dati del form
            associazione_id = post.get('associazione_id')
            piano_id = post.get('piano_id')
            codice_fiscale = post.get('codice_fiscale', '').strip()
            data_nascita = post.get('data_nascita', '').strip()
            luogo_nascita = post.get('luogo_nascita', '').strip()
            street = post.get('street', '').strip()
            street2 = post.get('street2', '').strip()
            city = post.get('city', '').strip()
            zip_code = post.get('zip', '').strip()
            state_id = post.get('state_id', '').strip()
            country_id = post.get('country_id', '').strip() or False
            telefono = post.get('telefono', '').strip()
            note = post.get('note', '').strip()
            
            # Validazione
            if not associazione_id:
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Seleziona un\'associazione')
                })
            
            if not piano_id:
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Seleziona un piano di tesseramento')
                })
            
            # Verifica che associazione e piano esistano e siano attivi
            associazione = request.env['associazione.culturale'].sudo().browse(int(associazione_id))
            piano = request.env['piano.tesseramento'].sudo().browse(int(piano_id))
            
            if not associazione.exists() or not associazione.attivo:
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Associazione non valida o non attiva')
                })
            
            if not piano.exists() or not piano.attivo:
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Piano di tesseramento non valido o non attivo')
                })

            # Trova o crea l'associato con l'email dell'utente e collegalo (reclama)
            user_email = (user.partner_id.email or user.login or '').strip().lower()
            if not user_email:
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Il tuo account non ha un\'email. Aggiungila al profilo prima di richiedere la tessera.')
                })
            Associato = request.env['associato'].sudo()
            associato = Associato.search([('email', '=', user_email)], limit=1)
            associato_vals = {
                'email': user_email,
                'user_id': user.id,
                'codice_fiscale': codice_fiscale or (associato.codice_fiscale if associato else False),
                'data_nascita': data_nascita or (associato.data_nascita if associato else False),
                'luogo_nascita': luogo_nascita or (associato.luogo_nascita if associato else False),
                'street': street or (associato.street if associato else False),
                'street2': street2 or (associato.street2 if associato else False),
                'city': city or (associato.city if associato else False),
                'zip': zip_code or (associato.zip if associato else False),
                'state_id': int(state_id) if state_id else (associato.state_id.id if associato else False),
                'country_id': int(country_id) if country_id else (associato.country_id.id if associato else False),
                'phone': telefono or (associato.phone if associato else False),
            }
            if associato:
                associato.write(associato_vals)
            else:
                associato = Associato.create(associato_vals)

            # Aggiorna anche il partner per indirizzo/telefono
            if user.partner_id:
                partner_vals = {}
                if street:
                    partner_vals['street'] = street
                if street2:
                    partner_vals['street2'] = street2
                if city:
                    partner_vals['city'] = city
                if zip_code:
                    partner_vals['zip'] = zip_code
                if state_id:
                    partner_vals['state_id'] = int(state_id)
                if country_id:
                    partner_vals['country_id'] = int(country_id)
                if telefono:
                    partner_vals['phone'] = telefono
                if partner_vals:
                    user.partner_id.sudo().write(partner_vals)

            # Gestisci iscrizioni alle newsletter (se il modulo mass_mailing è installato)
            if 'mailing.list' in request.env and user.partner_id and user.partner_id.email:
                mailing_list_ids = post.getlist('mailing_list_ids')  # getlist per checkbox multiple
                
                # Normalizza l'email per la ricerca
                email_normalized = user.partner_id.email.lower().strip() if user.partner_id.email else None
                
                if email_normalized:
                    # Cerca un contatto mailing esistente con questa email
                    existing_contact = request.env['mailing.contact'].sudo().search([
                        ('email_normalized', '=', email_normalized),
                    ], limit=1)
                    
                    if mailing_list_ids:
                        # Lista di ID delle liste selezionate
                        list_ids = [int(list_id) for list_id in mailing_list_ids]
                        
                        # Verifica che le liste esistano e siano attive
                        valid_lists = request.env['mailing.list'].sudo().browse(list_ids).filtered(
                            lambda l: l.exists() and l.active and l.is_public
                        )
                        
                        if valid_lists:
                            if existing_contact:
                                # Aggiungi le liste al contatto esistente (senza rimuovere quelle già presenti)
                                current_lists = existing_contact.list_ids.ids
                                new_lists = [lid for lid in valid_lists.ids if lid not in current_lists]
                                if new_lists:
                                    existing_contact.write({
                                        'list_ids': [(4, lid) for lid in new_lists],
                                    })
                            else:
                                # Crea nuovo contatto mailing con tutte le liste selezionate
                                request.env['mailing.contact'].sudo().create({
                                    'name': user.partner_id.name or user.name,
                                    'email': user.partner_id.email,
                                    'list_ids': [(6, 0, valid_lists.ids)],
                                })
            
            # Crea un record tesseramento pending
            tesseramento_pending = request.env['tesseramento.pending'].sudo().create({
                'associato_id': associato.id,
                'associazione_id': int(associazione_id),
                'piano_id': int(piano_id),
                'importo': piano.costo_tessera,
                'note': note,
                'stato': 'pending',
            })
            
            # Crea una transazione di pagamento
            # Ottieni il provider di pagamento attivo che supporta la valuta del piano
            providers = request.env['payment.provider'].sudo().search([
                ('state', '=', 'enabled'),
                ('is_published', '=', True),
            ])
            
            # Filtra provider che supportano la valuta del piano
            provider = None
            for p in providers:
                if not p.available_currency_ids or piano.currency_id.id in p.available_currency_ids.ids:
                    provider = p
                    break
            
            if not provider:
                # Se nessun provider disponibile, mostra messaggio più chiaro
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Nessun metodo di pagamento disponibile per questa valuta. '
                              'Contatta l\'amministratore per configurare un provider di pagamento.')
                })
            
            # Crea la transazione
            reference = f"TESS-{tesseramento_pending.id}"
            tx_values = {
                'amount': piano.costo_tessera,
                'currency_id': piano.currency_id.id,
                'partner_id': user.partner_id.id,
                'provider_id': provider.id,
                'reference': reference,
                'company_id': request.env.company.id,
            }
            
            tx = request.env['payment.transaction'].sudo().create(tx_values)
            
            # Collega la transazione al tesseramento pending
            tesseramento_pending.write({'transaction_id': tx.id})
            
            # Genera il link di pagamento usando payment.link.wizard se disponibile
            # Altrimenti usa il metodo standard del provider
            try:
                # Prova con payment.link.wizard
                if 'payment.link.wizard' in request.env:
                    payment_link_wizard = request.env['payment.link.wizard'].sudo().create({
                        'res_id': tx.id,
                        'res_model': 'payment.transaction',
                        'amount': piano.costo_tessera,
                        'currency_id': piano.currency_id.id,
                        'partner_id': user.partner_id.id,
                        'description': f'Tesseramento - {associazione.name} - {piano.name}',
                    })
                    if payment_link_wizard.link:
                        tx.return_url = f'/tesseramento/payment/return?reference={tx.reference}'
                        return request.redirect(payment_link_wizard.link)
            except:
                pass
            
            # Fallback: usa il metodo del provider per ottenere il link
            try:
                # Imposta il return_url per il callback
                tx.return_url = f'/tesseramento/payment/return?reference={tx.reference}'
                # Il provider dovrebbe avere un metodo per ottenere il link
                payment_link = provider._get_landing_route(tx) if hasattr(provider, '_get_landing_route') else None
                if payment_link:
                    return request.redirect(payment_link)
            except:
                pass
            
            # Ultimo fallback: usa la route standard (se esiste)
            # In Odoo 19, questa route potrebbe non esistere, quindi proviamo anche con il metodo render del provider
            try:
                # Alcuni provider hanno un metodo render che restituisce il form HTML
                if hasattr(provider, 'render'):
                    return provider.render(tx.id, {
                        'return_url': f'/tesseramento/payment/return?reference={tx.reference}',
                    })
            except:
                pass
            
            # Se tutto fallisce, mostra errore
            return request.render('associazioni_culturali.tesseramento_error', {
                'error': _('Impossibile generare il link di pagamento. Contatta l\'amministratore.')
            })
            
        except Exception as e:
            _logger.error("Errore durante la creazione della tessera: %s", str(e))
            return request.render('associazioni_culturali.tesseramento_error', {
                'error': f'Si è verificato un errore: {str(e)}'
            })

    @http.route('/tesseramento/success', type='http', auth='user', website=True, methods=['GET'])
    def tesseramento_success_page(self, **kw):
        """Pagina di successo dopo il tesseramento"""
        user = request.env.user
        tesseramento = request.env['tesseramento.pending'].sudo().search([
            ('associato_id.user_id', '=', user.id),
            ('stato', '=', 'completed'),
            ('tessera_id', '!=', False),
        ], order='create_date desc', limit=1)
        
        if tesseramento and tesseramento.tessera_id:
            return request.render('associazioni_culturali.tesseramento_success', {
                'tessera': tesseramento.tessera_id,
                'associazione': tesseramento.associazione_id,
                'piano': tesseramento.piano_id,
            })
        
        return request.render('associazioni_culturali.tesseramento_success', {})
    
    @http.route('/tesseramento/payment/return', type='http', auth='public', website=True, methods=['GET', 'POST'], csrf=False)
    def tesseramento_payment_return(self, **kw):
        """Callback dopo il pagamento"""
        tx_reference = request.params.get('reference') or request.params.get('tx_reference')
        if not tx_reference:
            return request.redirect('/tesseramento')
        
        # Cerca la transazione
        tx = request.env['payment.transaction'].sudo().search([
            ('reference', '=', tx_reference)
        ], limit=1)
        
        if not tx:
            return request.redirect('/tesseramento')
        
        # Cerca il tesseramento pending
        tesseramento = request.env['tesseramento.pending'].sudo().search([
            ('transaction_id', '=', tx.id)
        ], limit=1)
        
        if tx.state == 'done' and tesseramento:
            # Completa il tesseramento se non già fatto
            if tesseramento.stato == 'paid' and not tesseramento.tessera_id:
                tessera = tesseramento.action_completa_tessera()
            
            # Reindirizza alla pagina di successo
            return request.redirect('/tesseramento/success')
        elif tx.state in ('cancel', 'error'):
            # Pagamento fallito o annullato
            if tesseramento:
                tesseramento.write({'stato': 'cancelled'})
            return request.render('associazioni_culturali.tesseramento_error', {
                'error': _('Il pagamento è stato annullato o è fallito. Riprova.')
            })
        
        return request.redirect('/tesseramento')

    @http.route('/my/tessere', type='http', auth='user', website=True, methods=['GET'])
    def my_tessere(self, **kw):
        """Vista utente con le tessere dei profili associato collegati"""
        user = request.env.user
        if user._is_public():
            return request.redirect('/web/login?redirect=/my/tessere')

        associati = user.associato_ids
        tessere_passate = request.env['tessera']
        tessera_attuale_id = False
        tessera_in_scadenza = False
        for ass in associati:
            ass._compute_tessera_attuale()
            tessere_passate |= ass.get_tessere_passate()
            if ass.tessera_attuale_id and not tessera_attuale_id:
                tessera_attuale_id = ass.tessera_attuale_id
                tessera_in_scadenza = ass.tessera_in_scadenza
        tessere_passate = tessere_passate.sorted('data_scadenza', reverse=True)

        piani = request.env['piano.tesseramento'].sudo().search([('attivo', '=', True)])
        associazioni = request.env['associazione.culturale'].sudo().search([('attivo', '=', True)])

        values = {
            'user': user,
            'associati': associati,
            'tessera_attuale_id': tessera_attuale_id,
            'tessera_in_scadenza': tessera_in_scadenza,
            'tessere_passate': tessere_passate,
            'piani': piani,
            'associazioni': associazioni,
        }
        return request.render('associazioni_culturali.my_tessere', values)

    @http.route('/my/associato/reclama', type='http', auth='user', website=True, methods=['GET'])
    def associato_reclama_page(self, **kw):
        """Elenco profili associato con stessa email dell'utente non ancora reclamati; permette di associarli."""
        user = request.env.user
        if user._is_public():
            return request.redirect('/web/login?redirect=/my/associato/reclama')
        user_email = (user.partner_id.email or user.login or '').strip().lower()
        if not user_email:
            return request.render('associazioni_culturali.associato_reclama', {
                'error': _('Il tuo account non ha un\'email. Aggiungila al profilo.'),
                'associati_da_reclamare': request.env['associato'],
            })
        associati_da_reclamare = request.env['associato'].sudo().search([
            ('email', '=', user_email),
            ('user_id', '=', False),
        ])
        redirect_url = kw.get('redirect') or '/my/tessere'
        return request.render('associazioni_culturali.associato_reclama', {
            'associati_da_reclamare': associati_da_reclamare,
            'redirect': redirect_url,
        })

    @http.route('/my/associato/reclama/<int:associato_id>', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def associato_reclama_do(self, associato_id, **kw):
        """Reclama un profilo associato (collega all'utente corrente)."""
        user = request.env.user
        if user._is_public():
            return request.redirect('/web/login?redirect=/my/associato/reclama')
        associato = request.env['associato'].sudo().browse(associato_id)
        if not associato.exists():
            return request.redirect('/my/associato/reclama')
        try:
            associato.action_reclama()
        except Exception as e:
            return request.render('associazioni_culturali.tesseramento_error', {
                'error': str(e),
            })
        redirect = kw.get('redirect') or '/my/tessere'
        return request.redirect(redirect)

    @http.route('/my/tessere/rinnova', type='http', auth='user', website=True, methods=['GET'], csrf=False)
    def rinnova_tessera_form(self, **kw):
        """Mostra il form di rinnovo tessera con dati precompilati"""
        user = request.env.user
        if user._is_public():
            return request.redirect('/web/login?redirect=/my/tessere/rinnova')

        # Usa il primo profilo associato collegato; se nessuno, redirect a reclama o tesseramento
        associati = user.associato_ids
        if not associati:
            return request.redirect('/my/associato/reclama?redirect=/my/tessere/rinnova')
        associato = associati[0]

        associazione_id = kw.get('associazione_id')
        piano_id = kw.get('piano_id')
        if not associazione_id and associato.tessera_attuale_id:
            associazione_id = associato.tessera_attuale_id.associazione_id.id
        if not piano_id and associato.tessera_attuale_id:
            piano_id = associato.tessera_attuale_id.piano_id.id
        
        # Ottieni associazioni attive
        associazioni = request.env['associazione.culturale'].sudo().search([
            ('attivo', '=', True)
        ])
        
        # Ottieni piani attivi
        piani = request.env['piano.tesseramento'].sudo().search([
            ('attivo', '=', True)
        ])
        
        # Liste mailing con solo id/name (compatibile con versioni senza campo description)
        mailing_lists = _mailing_lists_safe(request.env)
        
        # Ottieni stati e paesi per i campi indirizzo
        states = request.env['res.country.state'].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        
        values = {
            'user': user,
            'associato': associato,
            'associazioni': associazioni,
            'piani': piani,
            'mailing_lists': mailing_lists,
            'states': states,
            'countries': countries,
            'associazione_id': int(associazione_id) if associazione_id else None,
            'piano_id': int(piano_id) if piano_id else None,
        }
        return request.render('associazioni_culturali.rinnova_tessera_form', values)

    @http.route('/my/tessere/rinnova', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def rinnova_tessera(self, **post):
        """Gestisce il rinnovo della tessera con pagamento"""
        try:
            user = request.env.user
            if user._is_public():
                return request.redirect('/web/login?redirect=/my/tessere')
            
            associazione_id = post.get('associazione_id')
            piano_id = post.get('piano_id')
            
            if not associazione_id or not piano_id:
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Seleziona associazione e piano')
                })
            
            associazione = request.env['associazione.culturale'].sudo().browse(int(associazione_id))
            piano = request.env['piano.tesseramento'].sudo().browse(int(piano_id))
            
            if not associazione.exists() or not associazione.attivo:
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Associazione non valida')
                })
            
            if not piano.exists() or not piano.attivo:
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Piano non valido')
                })
            
            associati = user.associato_ids
            if not associati:
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Nessun profilo associato collegato. Reclama un profilo dalla tua email.')
                })
            associato = associati[0]

            codice_fiscale = post.get('codice_fiscale', '').strip()
            data_nascita = post.get('data_nascita', '').strip()
            luogo_nascita = post.get('luogo_nascita', '').strip()
            street = post.get('street', '').strip()
            street2 = post.get('street2', '').strip()
            city = post.get('city', '').strip()
            zip_code = post.get('zip', '').strip()
            state_id = post.get('state_id', '').strip() or False
            country_id = post.get('country_id', '').strip() or False
            telefono = post.get('telefono', '').strip()
            note = post.get('note', '').strip()

            associato_vals = {}
            if codice_fiscale:
                associato_vals['codice_fiscale'] = codice_fiscale
            if data_nascita:
                associato_vals['data_nascita'] = data_nascita
            if luogo_nascita:
                associato_vals['luogo_nascita'] = luogo_nascita
            if street:
                associato_vals['street'] = street
            if street2:
                associato_vals['street2'] = street2
            if city:
                associato_vals['city'] = city
            if zip_code:
                associato_vals['zip'] = zip_code
            if state_id:
                associato_vals['state_id'] = int(state_id)
            if country_id:
                associato_vals['country_id'] = int(country_id)
            if telefono:
                associato_vals['phone'] = telefono
            if associato_vals:
                associato.sudo().write(associato_vals)

            if user.partner_id:
                partner_vals = {}
                if street:
                    partner_vals['street'] = street
                if street2:
                    partner_vals['street2'] = street2
                if city:
                    partner_vals['city'] = city
                if zip_code:
                    partner_vals['zip'] = zip_code
                if state_id:
                    partner_vals['state_id'] = int(state_id)
                if country_id:
                    partner_vals['country_id'] = int(country_id)
                if telefono:
                    partner_vals['phone'] = telefono
                if partner_vals:
                    user.partner_id.sudo().write(partner_vals)

            if 'mailing.list' in request.env and user.partner_id and user.partner_id.email:
                mailing_list_ids = post.getlist('mailing_list_ids')
                email_normalized = user.partner_id.email.lower().strip() if user.partner_id.email else None
                if email_normalized:
                    existing_contact = request.env['mailing.contact'].sudo().search([
                        ('email_normalized', '=', email_normalized),
                    ], limit=1)
                    if mailing_list_ids:
                        list_ids = [int(list_id) for list_id in mailing_list_ids]
                        valid_lists = request.env['mailing.list'].sudo().browse(list_ids).filtered(
                            lambda l: l.exists() and l.active and l.is_public
                        )
                        if valid_lists:
                            if existing_contact:
                                current_lists = existing_contact.list_ids.ids
                                new_lists = [lid for lid in valid_lists.ids if lid not in current_lists]
                                if new_lists:
                                    existing_contact.write({
                                        'list_ids': [(4, lid) for lid in new_lists],
                                    })
                            else:
                                request.env['mailing.contact'].sudo().create({
                                    'name': user.partner_id.name or user.name,
                                    'email': user.partner_id.email,
                                    'list_ids': [(6, 0, valid_lists.ids)],
                                })

            tesseramento_pending = request.env['tesseramento.pending'].sudo().create({
                'associato_id': associato.id,
                'associazione_id': int(associazione_id),
                'piano_id': int(piano_id),
                'importo': piano.costo_tessera,
                'stato': 'pending',
            })
            
            # Crea transazione pagamento
            providers = request.env['payment.provider'].sudo().search([
                ('state', '=', 'enabled'),
                ('is_published', '=', True),
            ])
            
            provider = None
            for p in providers:
                if not p.available_currency_ids or piano.currency_id.id in p.available_currency_ids.ids:
                    provider = p
                    break
            
            if not provider:
                return request.render('associazioni_culturali.tesseramento_error', {
                    'error': _('Nessun metodo di pagamento disponibile per questa valuta.')
                })
            
            reference = f"TESS-RINN-{tesseramento_pending.id}"
            tx = request.env['payment.transaction'].sudo().create({
                'amount': piano.costo_tessera,
                'currency_id': piano.currency_id.id,
                'partner_id': user.partner_id.id,
                'provider_id': provider.id,
                'reference': reference,
                'company_id': request.env.company.id,
            })
            
            tesseramento_pending.write({'transaction_id': tx.id})
            tx.return_url = f'/tesseramento/payment/return?reference={tx.reference}'
            
            # Genera link pagamento
            try:
                if 'payment.link.wizard' in request.env:
                    payment_link_wizard = request.env['payment.link.wizard'].sudo().create({
                        'res_id': tx.id,
                        'res_model': 'payment.transaction',
                        'amount': piano.costo_tessera,
                        'currency_id': piano.currency_id.id,
                        'partner_id': user.partner_id.id,
                        'description': f'Rinnovo Tessera - {associazione.name}',
                    })
                    if payment_link_wizard.link:
                        return request.redirect(payment_link_wizard.link)
            except:
                pass
            
            return request.redirect(f'/payment/process?tx_id={tx.id}')
            
        except Exception as e:
            _logger.error("Errore durante il rinnovo della tessera: %s", str(e))
            return request.render('associazioni_culturali.tesseramento_error', {
                'error': f'Si è verificato un errore: {str(e)}'
            })
