# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_web_menu = fields.Boolean(string='Abilita Menu Web', default=False,
                                   help='Abilita il menu web per i clienti del ristorante')
    web_menu_url = fields.Char(string='URL Menu Web', compute='_compute_web_menu_url', store=True)
    qr_code = fields.Binary(string='QR Code', readonly=True)
    qr_code_filename = fields.Char(string='Nome File QR Code')

    @api.depends('enable_web_menu', 'id')
    def _compute_web_menu_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.enable_web_menu and record.id:
                record.web_menu_url = f"{base_url}/pos/web/menu/{record.id}"
            else:
                record.web_menu_url = False

    def action_generate_qr_code(self):
        """Genera il QR code per il menu web"""
        self.ensure_one()
        if not self.enable_web_menu:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Attenzione',
                    'message': 'Devi prima abilitare il Menu Web nelle impostazioni.',
                    'type': 'warning',
                }
            }
        
        try:
            import qrcode
            from io import BytesIO
            import base64
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.web_menu_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_code_image = base64.b64encode(buffer.getvalue()).decode()
            
            self.write({
                'qr_code': qr_code_image,
                'qr_code_filename': f'qr_code_pos_{self.id}.png',
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Successo',
                    'message': 'QR Code generato con successo!',
                    'type': 'success',
                }
            }
        except ImportError:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Errore',
                    'message': 'Libreria qrcode non installata. Installa con: pip install qrcode[pil]',
                    'type': 'danger',
                }
            }

