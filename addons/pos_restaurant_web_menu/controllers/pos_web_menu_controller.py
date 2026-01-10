# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class PosWebMenuController(http.Controller):

    @http.route('/pos/web/menu/<int:pos_config_id>', type='http', auth='public', website=True, csrf=False)
    def pos_web_menu(self, pos_config_id, **kwargs):
        """Pagina web del menu POS"""
        pos_config = request.env['pos.config'].sudo().browse(pos_config_id)
        
        if not pos_config.exists() or not pos_config.enable_web_menu:
            return request.not_found()
        
        # Ottieni i prodotti disponibili nel POS
        products = request.env['product.product'].sudo().search([
            ('available_in_pos', '=', True),
            ('sale_ok', '=', True),
        ])
        
        # Raggruppa per categorie
        categories = {}
        for product in products:
            category = product.pos_categ_ids[0] if product.pos_categ_ids else request.env['pos.category'].sudo()
            if category:
                if category.id not in categories:
                    categories[category.id] = {
                        'id': category.id,
                        'name': category.name,
                        'products': [],
                    }
                categories[category.id]['products'].append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.list_price,
                    'image': f'/web/image/product.product/{product.id}/image_128' if product.image_128 else False,
                    'description': product.description_sale or '',
                })
        
        values = {
            'pos_config': pos_config,
            'categories': list(categories.values()),
            'tables': request.env['restaurant.table'].sudo().search([
                ('floor_id.pos_config_id', '=', pos_config_id),
            ]),
        }
        
        return request.render('pos_restaurant_web_menu.web_menu_page', values)

    @http.route('/pos/web/menu/add_to_cart', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def add_to_cart(self, pos_config_id, product_id, quantity=1, **kwargs):
        """Aggiunge un prodotto al carrello"""
        try:
            pos_config = request.env['pos.config'].sudo().browse(pos_config_id)
            product = request.env['product.product'].sudo().browse(product_id)
            
            if not pos_config.exists() or not product.exists():
                return {'success': False, 'error': 'Prodotto o configurazione POS non trovata'}
            
            return {
                'success': True,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.list_price,
                    'quantity': quantity,
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/pos/web/menu/create_order', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def create_order(self, pos_config_id, table_id, customer_id=None, products=None, **kwargs):
        """Crea un ordine POS dal web menu"""
        try:
            pos_config = request.env['pos.config'].sudo().browse(pos_config_id)
            table = request.env['restaurant.table'].sudo().browse(table_id)
            
            if not pos_config.exists() or not table.exists():
                return {'success': False, 'error': 'Configurazione POS o tavolo non trovato'}
            
            # Verifica se esiste già un ordine per questo tavolo
            existing_order = request.env['pos.order'].sudo().search([
                ('table_id', '=', table_id),
                ('state', 'in', ['draft', 'paid']),
            ], limit=1, order='create_date desc')
            
            if existing_order:
                # Aggiungi prodotti all'ordine esistente
                order = existing_order
            else:
                # Trova o crea una sessione POS attiva
                session = pos_config.current_session_id
                if not session or session.state != 'opened':
                    return {'success': False, 'error': 'Nessuna sessione POS attiva. Apri una sessione POS prima di creare ordini dal web.'}
                
                # Crea un nuovo ordine
                order = request.env['pos.order'].sudo().create({
                    'session_id': session.id,
                    'config_id': pos_config_id,
                    'table_id': table_id,
                    'partner_id': customer_id if customer_id else False,
                    'state': 'draft',
                })
            
            # Aggiungi prodotti all'ordine
            if products:
                for product_data in products:
                    product = request.env['product.product'].sudo().browse(product_data['id'])
                    if product.exists():
                        request.env['pos.order.line'].sudo().create({
                            'order_id': order.id,
                            'product_id': product.id,
                            'qty': product_data.get('quantity', 1),
                            'price_unit': product.list_price,
                        })
            
            return {
                'success': True,
                'order_id': order.id,
                'order_name': order.name,
                'message': 'Ordine creato con successo!' if not existing_order else 'Prodotti aggiunti all\'ordine esistente!',
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/pos/web/menu/get_tables', type='json', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_tables(self, pos_config_id, **kwargs):
        """Ottiene la lista dei tavoli disponibili"""
        try:
            pos_config = request.env['pos.config'].sudo().browse(pos_config_id)
            tables = request.env['restaurant.table'].sudo().search([
                ('floor_id.pos_config_id', '=', pos_config_id),
            ])
            
            return {
                'success': True,
                'tables': [{
                    'id': table.id,
                    'name': table.name,
                    'floor': table.floor_id.name if table.floor_id else '',
                } for table in tables],
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

