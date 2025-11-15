# 🚀 Odoo Custom Addons Development Guide

Questa directory contiene gli addons personalizzati per Odoo Community 19.0.

## 📁 Struttura Directory

```
addons/
├── README.md                    # Questo file
├── my_custom_module/           # Esempio di modulo custom
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── my_model.py
│   ├── views/
│   │   └── my_model_views.xml
│   ├── security/
│   │   └── ir.model.access.csv
│   ├── data/
│   │   └── demo_data.xml
│   ├── static/
│   │   ├── description/
│   │   │   ├── icon.png
│   │   │   └── index.html
│   │   └── src/
│   │       ├── css/
│   │       ├── js/
│   │       └── xml/
│   └── i18n/
│       ├── it_IT.po
│       └── en_US.po
```

## 🎯 Quick Start - Creare un Nuovo Addon

### 1. Usa lo scaffold di Odoo

```bash
# Entra nel container Odoo
docker exec -it vm-odoo-odoo-web-1 bash

# Genera lo scheletro del modulo
odoo scaffold my_module_name /mnt/custom-addons

# Esci dal container
exit
```

### 2. Oppure crea manualmente la struttura

```bash
cd addons
mkdir my_module_name
cd my_module_name
touch __init__.py __manifest__.py
mkdir models views security static data
```

## 📝 File Essenziali

### `__manifest__.py` - Manifesto del modulo

```python
{
    'name': 'My Custom Module',
    'version': '19.0.1.0.0',
    'category': 'Custom',
    'summary': 'Breve descrizione del modulo',
    'description': """
        Descrizione dettagliata del modulo.
        Cosa fa, perché è utile, ecc.
    """,
    'author': 'Victorian Monkey',
    'website': 'https://victorianmonkey.org',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        # altri moduli Odoo Community da cui dipende
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module_name/static/src/js/**/*',
            'my_module_name/static/src/css/**/*',
        ],
    },
    'demo': [
        # dati demo per testing
    ],
    'installable': True,
    'application': False,  # True se è un'applicazione standalone
    'auto_install': False,
}
```

### `__init__.py` - Import dei moduli

```python
# -*- coding: utf-8 -*-
from . import models
# from . import controllers
# from . import wizards
```

### `models/__init__.py`

```python
# -*- coding: utf-8 -*-
from . import my_model
```

### `models/my_model.py` - Esempio di Model

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Custom Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # per tracking
    _order = 'create_date desc'

    # Fields
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        help='Nome del record'
    )
    
    description = fields.Text(
        string='Description',
        tracking=True
    )
    
    active = fields.Boolean(
        default=True,
        help='Disattiva invece di eliminare'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status', tracking=True)
    
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True
    )
    
    amount = fields.Float(
        string='Amount',
        digits='Product Price'
    )
    
    line_ids = fields.One2many(
        'my.model.line',
        'parent_id',
        string='Lines'
    )
    
    # Computed fields
    total_amount = fields.Float(
        string='Total',
        compute='_compute_total_amount',
        store=True
    )
    
    # Constraints
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'The name must be unique!'),
    ]
    
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError('Amount cannot be negative!')
    
    # Computed methods
    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))
    
    # CRUD Override
    @api.model_create_multi
    def create(self, vals_list):
        # Custom logic before create
        records = super().create(vals_list)
        # Custom logic after create
        return records
    
    def write(self, vals):
        # Custom logic before write
        result = super().write(vals)
        # Custom logic after write
        return result
    
    def unlink(self):
        # Custom logic before delete
        if any(record.state == 'done' for record in self):
            raise ValidationError('Cannot delete done records!')
        return super().unlink()
    
    # Action methods
    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'
    
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
    
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
    
    # Onchange methods
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            # Auto-fill based on partner
            pass


class MyModelLine(models.Model):
    _name = 'my.model.line'
    _description = 'My Model Line'
    
    parent_id = fields.Many2one(
        'my.model',
        string='Parent',
        required=True,
        ondelete='cascade'
    )
    
    name = fields.Char(string='Description', required=True)
    amount = fields.Float(string='Amount')
```

### `views/my_model_views.xml` - Esempio di Views

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    
    <!-- Tree View -->
    <record id="view_my_model_tree" model="ir.ui.view">
        <field name="name">my.model.tree</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <tree string="My Models">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="date"/>
                <field name="state" decoration-info="state == 'draft'"
                       decoration-success="state == 'done'"
                       decoration-danger="state == 'cancelled'"/>
                <field name="total_amount" sum="Total"/>
            </tree>
        </field>
    </record>
    
    <!-- Form View -->
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form string="My Model">
                <header>
                    <button name="action_confirm" string="Confirm" 
                            type="object" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_done" string="Done" 
                            type="object" class="btn-success"
                            invisible="state != 'confirmed'"/>
                    <button name="action_cancel" string="Cancel" 
                            type="object" class="btn-danger"
                            invisible="state in ('done', 'cancelled')"/>
                    <field name="state" widget="statusbar" 
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <!-- Smart buttons qui -->
                    </div>
                    <div class="oe_title">
                        <label for="name" class="oe_edit_only"/>
                        <h1><field name="name" placeholder="Name..."/></h1>
                    </div>
                    <group>
                        <group name="main_info">
                            <field name="partner_id"/>
                            <field name="date"/>
                            <field name="user_id"/>
                        </group>
                        <group name="amounts">
                            <field name="amount"/>
                            <field name="total_amount"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lines" name="lines">
                            <field name="line_ids">
                                <tree editable="bottom">
                                    <field name="name"/>
                                    <field name="amount"/>
                                </tree>
                            </field>
                        </page>
                        <page string="Description" name="description">
                            <field name="description" placeholder="Description..."/>
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>
    
    <!-- Search View -->
    <record id="view_my_model_search" model="ir.ui.view">
        <field name="name">my.model.search</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <search string="Search My Model">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="user_id"/>
                <filter string="Draft" name="draft" 
                        domain="[('state', '=', 'draft')]"/>
                <filter string="Confirmed" name="confirmed" 
                        domain="[('state', '=', 'confirmed')]"/>
                <filter string="Done" name="done" 
                        domain="[('state', '=', 'done')]"/>
                <separator/>
                <filter string="My Records" name="my_records" 
                        domain="[('user_id', '=', uid)]"/>
                <separator/>
                <filter string="Archived" name="archived" 
                        domain="[('active', '=', False)]"/>
                <group expand="0" string="Group By">
                    <filter string="Partner" name="group_partner" 
                            context="{'group_by': 'partner_id'}"/>
                    <filter string="Responsible" name="group_user" 
                            context="{'group_by': 'user_id'}"/>
                    <filter string="State" name="group_state" 
                            context="{'group_by': 'state'}"/>
                    <filter string="Date" name="group_date" 
                            context="{'group_by': 'date'}"/>
                </group>
            </search>
        </field>
    </record>
    
    <!-- Action -->
    <record id="action_my_model" model="ir.actions.act_window">
        <field name="name">My Models</field>
        <field name="res_model">my.model</field>
        <field name="view_mode">tree,form</field>
        <field name="context">{'search_default_draft': 1}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first record
            </p>
            <p>
                Click the create button to get started.
            </p>
        </field>
    </record>
    
    <!-- Menu -->
    <menuitem id="menu_my_model_root" 
              name="My Module" 
              sequence="10"/>
    
    <menuitem id="menu_my_model" 
              name="My Models" 
              parent="menu_my_model_root" 
              action="action_my_model" 
              sequence="10"/>

</odoo>
```

### `security/ir.model.access.csv` - Permessi di accesso

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
access_my_model_line_user,my.model.line.user,model_my_model_line,base.group_user,1,1,1,1
```

## 🔧 Sviluppo e Testing

### Installare/Aggiornare il modulo

```bash
# Riavvia Odoo in modalità update
docker-compose restart odoo-web

# Oppure esegui l'update dal container
docker exec -it vm-odoo-odoo-web-1 odoo \
  -u my_module_name \
  -d your_database_name \
  --stop-after-init

# Poi riavvia normalmente
docker-compose restart odoo-web
```

### Debugging

```python
# Nel tuo codice Python
import logging
_logger = logging.getLogger(__name__)

_logger.debug("Debug message")
_logger.info("Info message")
_logger.warning("Warning message")
_logger.error("Error message")

# Per debug interattivo
import pdb; pdb.set_trace()

# O meglio, usa ipdb (installa nel Dockerfile)
import ipdb; ipdb.set_trace()
```

### Visualizzare i log

```bash
# Segui i log in tempo reale
docker-compose logs -f odoo-web

# Solo errori
docker-compose logs -f odoo-web | grep ERROR
```

## 📚 Risorse Utili

### Documentazione Ufficiale
- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [Developer Tutorials](https://www.odoo.com/documentation/19.0/developer/tutorials.html)
- [ORM API](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Web Controllers](https://www.odoo.com/documentation/19.0/developer/reference/backend/http.html)

### Best Practices

1. **Naming Conventions**
   - Models: `my_module.model_name`
   - Fields: snake_case
   - Methods: snake_case
   - XML IDs: `module_name_view_model_type`

2. **Security**
   - Sempre definire ir.model.access.csv
   - Usa record rules per filtrare dati per utente/gruppo
   - Validare input utente con `@api.constrains`

3. **Performance**
   - Usa `store=True` per computed fields usati spesso
   - Limita le query con `search()` usando domini appropriati
   - Usa `read()` invece di browse per operazioni massive

4. **Translations**
   - Genera file .po: `docker exec vm-odoo-odoo-web-1 odoo --i18n-export=it_IT.po -d your_db -l it_IT --modules=my_module`
   - Update translations: `docker exec vm-odoo-odoo-web-1 odoo --i18n-import=it_IT.po -d your_db`

5. **Testing**
   - Scrivi unit tests in `tests/` directory
   - Esegui: `docker exec vm-odoo-odoo-web-1 odoo -u module_name --test-enable --stop-after-init -d your_db`

## 🎨 Moduli di Esempio Comuni

### 1. Estendere un modulo esistente

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    custom_field = fields.Char(string='Custom Field')
```

### 2. Controller per API/Web

```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):
    
    @http.route('/my/endpoint', type='json', auth='user')
    def my_endpoint(self, **kwargs):
        return {'status': 'success', 'data': []}
    
    @http.route('/my/page', type='http', auth='public', website=True)
    def my_page(self, **kwargs):
        return request.render('my_module.my_template', {})
```

### 3. Wizard (azioni temporanee)

```python
class MyWizard(models.TransientModel):
    _name = 'my.wizard'
    _description = 'My Wizard'
    
    name = fields.Char(required=True)
    
    def action_confirm(self):
        # Logica wizard
        active_id = self.env.context.get('active_id')
        record = self.env['my.model'].browse(active_id)
        # ...
```

## 🐛 Common Issues & Solutions

### Modulo non visibile dopo creazione
```bash
# Update apps list
# Settings > Apps > Update Apps List

# O riavvia con --dev=all
docker-compose down
docker-compose up -d
```

### Errori di import
```python
# Assicurati che __init__.py esista in ogni directory
# e importi correttamente i submoduli
```

### Permessi negati
```bash
# Verifica ir.model.access.csv
# Controlla che l'utente appartenga al gruppo giusto
```

## 🚢 Deploy in Produzione

1. Testa sempre in sviluppo prima
2. Backup database prima di update
3. Usa `-u module_name` per update specifici
4. Monitora i log durante il deploy
5. Test smoke dopo deploy

## 📦 Moduli Community Disponibili

Odoo Community Edition include già molti moduli utili:
- **Sales**: CRM, Vendite, Preventivi
- **Accounting**: Contabilità base, Fatturazione
- **Inventory**: Magazzino, Spedizioni
- **Manufacturing**: MRP base
- **Website**: Website builder, eCommerce, Blog
- **HR**: Dipendenti, Ferie, Presenze
- **Project**: Gestione progetti, Timesheet
- **Purchase**: Acquisti, Fornitori

Per funzionalità avanzate come contabilità completa, HR payroll, Studio, ecc., 
serve la licenza Odoo Enterprise.

---

**Happy Coding! 🎉**

Per domande o supporto: ops@victorianmonkey.org