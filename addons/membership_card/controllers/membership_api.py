# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
import json
from datetime import datetime


class MembershipAPI(http.Controller):
    """API REST per la gestione delle membership card"""

    @http.route('/api/membership/members', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_members(self, **kwargs):
        """Ottiene la lista dei membri"""
        try:
            # Verifica autenticazione (puoi implementare token-based auth)
            # Per ora permette accesso pubblico - modifica in produzione!
            
            domain = []
            if kwargs.get('active_only'):
                domain.append(('is_active', '=', True))
            if kwargs.get('membership_type_id'):
                domain.append(('membership_type_id', '=', int(kwargs['membership_type_id'])))
            
            members = request.env['membership.member'].sudo().search(domain)
            
            result = []
            for member in members:
                result.append({
                    'id': member.id,
                    'name': member.display_name or member.name,
                    'legal_name': member.name,
                    'chosen_name': member.display_name if member.use_chosen_name else None,
                    'use_chosen_name': member.use_chosen_name,
                    'email': member.email,
                    'phone': member.phone,
                    'fiscal_code': member.fiscal_code,
                    'membership_type': {
                        'id': member.membership_type_id.id,
                        'name': member.membership_type_id.name,
                        'code': member.membership_type_id.code,
                    },
                    'membership_start_date': member.membership_start_date.isoformat() if member.membership_start_date else None,
                    'membership_end_date': member.membership_end_date.isoformat() if member.membership_end_date else None,
                    'is_active': member.is_active,
                    'card_number': member.card_number,
                    'active_card': {
                        'id': member.active_card_id.id,
                        'card_number': member.active_card_id.card_number,
                        'barcode': member.active_card_id.barcode,
                        'qr_code': member.active_card_id.qr_code,
                    } if member.active_card_id else None,
                })
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'data': result,
                    'count': len(result),
                }),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e),
                }),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/membership/members/<int:member_id>', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_member(self, member_id, **kwargs):
        """Ottiene i dettagli di un membro"""
        try:
            member = request.env['membership.member'].sudo().browse(member_id)
            if not member.exists():
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Member not found',
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )
            
            result = {
                'id': member.id,
                'name': member.display_name or member.name,
                'legal_name': member.name,
                'chosen_name': member.display_name if member.use_chosen_name else None,
                'use_chosen_name': member.use_chosen_name,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'chosen_first_name': member.chosen_first_name if member.use_chosen_name else None,
                'chosen_last_name': member.chosen_last_name if member.use_chosen_name else None,
                'email': member.email,
                'phone': member.phone,
                'mobile': member.mobile,
                'address': {
                    'street': member.street,
                    'street2': member.street2,
                    'city': member.city,
                    'zip': member.zip,
                    'state': member.state_id.name if member.state_id else None,
                    'country': member.country_id.name if member.country_id else None,
                },
                'fiscal_code': member.fiscal_code,
                'vat': member.vat,
                'is_company': member.is_company,
                'membership_type': {
                    'id': member.membership_type_id.id,
                    'name': member.membership_type_id.name,
                    'code': member.membership_type_id.code,
                    'duration_months': member.membership_type_id.duration_months,
                    'price': member.membership_type_id.price,
                },
                'membership_start_date': member.membership_start_date.isoformat() if member.membership_start_date else None,
                'membership_end_date': member.membership_end_date.isoformat() if member.membership_end_date else None,
                'is_active': member.is_active,
                'is_expired': member.is_expired,
                'card_number': member.card_number,
                'active_card': {
                    'id': member.active_card_id.id,
                    'card_number': member.active_card_id.card_number,
                    'barcode': member.active_card_id.barcode,
                    'qr_code': member.active_card_id.qr_code,
                    'issue_date': member.active_card_id.issue_date.isoformat() if member.active_card_id.issue_date else None,
                    'expiry_date': member.active_card_id.expiry_date.isoformat() if member.active_card_id.expiry_date else None,
                } if member.active_card_id else None,
                'cards': [{
                    'id': card.id,
                    'card_number': card.card_number,
                    'barcode': card.barcode,
                    'issue_date': card.issue_date.isoformat() if card.issue_date else None,
                    'expiry_date': card.expiry_date.isoformat() if card.expiry_date else None,
                    'is_active': card.is_active,
                } for card in member.card_ids],
            }
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'data': result,
                }),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e),
                }),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/membership/members', auth='public', methods=['POST'], csrf=False, cors='*')
    def create_member(self, **kwargs):
        """Crea un nuovo membro"""
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            
            # Valida i dati richiesti
            required_fields = ['name', 'membership_type_id']
            for field in required_fields:
                if field not in data:
                    return request.make_response(
                        json.dumps({
                            'success': False,
                            'error': f'Missing required field: {field}',
                        }),
                        headers=[('Content-Type', 'application/json')],
                        status=400
                    )
            
            # Crea il membro
            member_vals = {
                'name': data['name'],
                'email': data.get('email'),
                'phone': data.get('phone'),
                'mobile': data.get('mobile'),
                'street': data.get('street'),
                'city': data.get('city'),
                'zip': data.get('zip'),
                'fiscal_code': data.get('fiscal_code'),
                'vat': data.get('vat'),
                'is_company': data.get('is_company', False),
                'membership_type_id': int(data['membership_type_id']),
                'membership_start_date': data.get('membership_start_date') or fields.Date.today(),
            }
            
            member = request.env['membership.member'].sudo().create(member_vals)
            
            # Genera automaticamente la card se richiesto
            if data.get('generate_card', True):
                member.action_generate_card()
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'data': {'id': member.id, 'name': member.name},
                }),
                headers=[('Content-Type', 'application/json')],
                status=201
            )
        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e),
                }),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/membership/cards/<string:card_number>', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_card_by_number(self, card_number, **kwargs):
        """Verifica una card tramite numero o barcode"""
        try:
            card = request.env['membership.card'].sudo().search([
                '|',
                ('card_number', '=', card_number),
                ('barcode', '=', card_number),
            ], limit=1)
            
            if not card.exists():
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Card not found',
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )
            
            result = {
                'id': card.id,
                'card_number': card.card_number,
                'barcode': card.barcode,
                'qr_code': card.qr_code,
                'member': {
                    'id': card.member_id.id,
                    'name': card.member_id.name,
                    'fiscal_code': card.member_id.fiscal_code,
                },
                'membership_type': {
                    'id': card.membership_type_id.id,
                    'name': card.membership_type_id.name,
                },
                'issue_date': card.issue_date.isoformat() if card.issue_date else None,
                'expiry_date': card.expiry_date.isoformat() if card.expiry_date else None,
                'is_active': card.is_active,
                'is_expired': card.is_expired,
                'is_lost': card.is_lost,
                'is_stolen': card.is_stolen,
            }
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'data': result,
                }),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e),
                }),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/membership/types', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_membership_types(self, **kwargs):
        """Ottiene la lista dei tipi di membership"""
        try:
            domain = [('active', '=', True)]
            types = request.env['membership.type'].sudo().search(domain)
            
            result = []
            for mtype in types:
                result.append({
                    'id': mtype.id,
                    'name': mtype.name,
                    'code': mtype.code,
                    'description': mtype.description,
                    'duration_months': mtype.duration_months,
                    'price': mtype.price,
                    'tax_exempt': mtype.tax_exempt,
                })
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'data': result,
                    'count': len(result),
                }),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e),
                }),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

