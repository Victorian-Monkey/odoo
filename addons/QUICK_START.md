# 🚀 Quick Start - Aggiungi Addons a Odoo

Guida rapida per aggiungere moduli alla directory `addons/`.

## 📦 Tipi di Addons

### 1️⃣ Moduli Custom Sviluppati da Te
### 2️⃣ Moduli Open Source dalla Community (OCA)
### 3️⃣ Moduli di Terze Parti

---

## 1️⃣ Creare un Modulo Custom (da Zero)

### Metodo A: Usa lo Scaffold di Odoo (Consigliato)

```bash
# Entra nel container Odoo
docker exec -it vm-odoo-odoo-web-1 bash

# Genera lo scheletro del modulo
odoo scaffold my_custom_module /mnt/custom-addons

# Esci dal container
exit

# Il tuo modulo è ora in addons/my_custom_module/
```

### Metodo B: Crea Manualmente

```bash
# Vai nella directory addons
cd addons

# Crea la struttura del modulo
mkdir my_custom_module
cd my_custom_module

# Crea i file base
touch __init__.py __manifest__.py

# Crea le directory
mkdir models views security static data i18n
```

Poi crea il contenuto minimo:

**`__init__.py`:**
```python
# -*- coding: utf-8 -*-
from . import models
```

**`__manifest__.py`:**
```python
# -*- coding: utf-8 -*-
{
    'name': 'My Custom Module',
    'version': '19.0.1.0.0',
    'category': 'Custom',
    'summary': 'Breve descrizione',
    'author': 'Victorian Monkey',
    'website': 'https://victorianmonkey.org',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

**`models/__init__.py`:**
```python
# -*- coding: utf-8 -*-
# from . import my_model
```

---

## 2️⃣ Installare Moduli dalla Community (OCA)

### Esempio: Installare moduli OCA (Odoo Community Association)

```bash
# Vai nella directory addons
cd addons

# Clone un modulo specifico da GitHub
git clone --depth 1 --branch 19.0 \
  https://github.com/OCA/server-tools.git oca-server-tools

# Oppure scarica come ZIP ed estrai
wget https://github.com/OCA/server-tools/archive/refs/heads/19.0.zip
unzip 19.0.zip
mv server-tools-19.0/* .
rm -rf server-tools-19.0 19.0.zip
```

### Repository OCA Popolari per Odoo 19.0:

```bash
# Server Tools
git clone --depth 1 --branch 19.0 https://github.com/OCA/server-tools.git

# Web Utilities
git clone --depth 1 --branch 19.0 https://github.com/OCA/web.git

# Reporting
git clone --depth 1 --branch 19.0 https://github.com/OCA/reporting-engine.git

# REST API
git clone --depth 1 --branch 19.0 https://github.com/OCA/rest-framework.git

# Account (Accounting extensions)
git clone --depth 1 --branch 19.0 https://github.com/OCA/account-financial-tools.git
```

⚠️ **Nota**: Verifica sempre che il modulo sia compatibile con Odoo 19.0!

---

## 3️⃣ Installare Moduli da Odoo Apps Store

### Metodo A: Download Manuale

1. Vai su https://apps.odoo.com/apps/modules/19.0/
2. Cerca il modulo che ti serve
3. Scarica il file ZIP
4. Estrai nella directory `addons/`

```bash
# Esempio
cd addons
unzip ~/Downloads/module_name.zip
```

### Metodo B: Direttamente da Odoo Interface

Alcuni moduli possono essere installati direttamente dall'interfaccia Odoo:
1. Settings > Apps > Upload
2. Seleziona il file ZIP
3. Click "Upload"

---

## 🔄 Dopo Aver Aggiunto un Addon

### 1. Riavvia Odoo

```bash
# Dalla directory principale vm-odoo/
docker compose restart odoo-web odoo-cron
```

### 2. Aggiorna la Lista Moduli

Dall'interfaccia Odoo:
1. Vai in **Settings** > **Apps**
2. Click sul menu ⋮ (tre puntini)
3. Click su **"Update Apps List"**
4. Conferma

### 3. Installa il Modulo

1. Nella lista Apps, rimuovi il filtro "Apps" per vedere tutti i moduli
2. Cerca il tuo modulo per nome
3. Click **"Install"** o **"Activate"**

### Oppure via Command Line:

```bash
# Installa modulo
docker exec -it vm-odoo-odoo-web-1 odoo \
  -d your_database_name \
  -i module_name \
  --stop-after-init

# Poi riavvia
docker compose restart odoo-web
```

---

## 📂 Struttura Directory Addons

Dopo aver aggiunto vari moduli:

```
addons/
├── README.md                      # Guida completa sviluppo
├── QUICK_START.md                 # Questa guida
│
├── my_custom_module_1/           # Tuo modulo custom
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   ├── views/
│   └── ...
│
├── my_custom_module_2/           # Altro tuo modulo
│   └── ...
│
├── oca-server-tools/             # Moduli OCA
│   ├── module_auto_update/
│   ├── base_technical_user/
│   └── ...
│
└── third_party_module/           # Modulo da Apps Store
    └── ...
```

---

## ✅ Checklist Addon Funzionante

Un addon Odoo valido **DEVE** avere:

- ✅ `__init__.py` (anche vuoto va bene)
- ✅ `__manifest__.py` con almeno `name`, `version`, `depends`
- ✅ Struttura corretta delle directory (models, views, security, etc.)

---

## 🔍 Verifica Addon Installato

### Via Interface:

1. Settings > Technical > Modules > Modules
2. Cerca il nome del tuo modulo
3. Verifica lo stato (Installed / To Install / Not Installed)

### Via Command Line:

```bash
# Lista tutti i moduli nel database
docker exec -it vm-odoo-odoo-web-1 odoo shell -d your_database << EOF
self.env['ir.module.module'].search([('name', '=', 'module_name')])
EOF
```

---

## 🐛 Troubleshooting

### Modulo non appare nella lista

```bash
# 1. Verifica che sia in addons/
ls -la addons/module_name

# 2. Verifica __manifest__.py
cat addons/module_name/__manifest__.py

# 3. Riavvia e aggiorna lista
docker compose restart odoo-web
# Poi: Settings > Apps > Update Apps List
```

### Errore durante installazione

```bash
# Guarda i log per dettagli
docker compose logs -f odoo-web

# Errori comuni:
# - Dipendenze mancanti: installa prima i moduli da cui dipende
# - Syntax error: controlla Python syntax
# - Permission denied: verifica permessi file
```

### Dipendenze mancanti

Se il modulo dipende da altri moduli non installati:

1. Leggi il `__manifest__.py` del modulo
2. Guarda la lista `depends`
3. Installa prima quei moduli
4. Poi installa il tuo modulo

---

## 🎓 Esempi Pratici

### Esempio 1: Aggiungere modulo OCA "Date Range"

```bash
cd addons

# Download modulo specifico
git clone --depth 1 --branch 19.0 \
  https://github.com/OCA/server-tools.git oca-temp

# Copia solo il modulo che serve
cp -r oca-temp/date_range .

# Pulisci
rm -rf oca-temp

# Riavvia
cd ..
docker compose restart odoo-web

# Poi installa da UI
```

### Esempio 2: Creare modulo "Hello World"

```bash
cd addons
mkdir hello_world
cd hello_world

# Crea __init__.py
echo "# -*- coding: utf-8 -*-" > __init__.py

# Crea __manifest__.py
cat > __manifest__.py << 'EOF'
{
    'name': 'Hello World',
    'version': '19.0.1.0.0',
    'category': 'Custom',
    'summary': 'My first Odoo module',
    'author': 'Victorian Monkey',
    'depends': ['base'],
    'data': [],
    'installable': True,
}
EOF

cd ../..
docker compose restart odoo-web
```

---

## 📚 Risorse Utili

### Repository OCA Principali:
- https://github.com/OCA - Tutti i repository OCA
- https://odoo-community.org/ - Documentazione OCA

### Odoo Apps Store:
- https://apps.odoo.com/apps/modules/19.0/ - Moduli ufficiali e community

### Documentazione:
- https://www.odoo.com/documentation/19.0/developer/tutorials.html - Tutorial sviluppo

---

## 💡 Best Practices

1. **Versioning**: Usa sempre versione compatibile (19.0.x.x.x)
2. **Dependencies**: Dichiara sempre tutte le dipendenze in `depends`
3. **Testing**: Testa in ambiente di sviluppo prima di produzione
4. **Backup**: Backup del database prima di installare nuovi moduli
5. **Git**: Usa `.gitignore` per escludere moduli di terze parti se usi git
6. **Aggiornamenti**: Tieni aggiornati i moduli della community

---

## 🔐 Sicurezza

- ⚠️ **NON installare moduli da fonti non affidabili**
- ⚠️ **Verifica sempre il codice di moduli di terze parti**
- ⚠️ **Fai backup prima di installare nuovi moduli**
- ⚠️ **Usa solo moduli con licenza compatibile (LGPL-3 per Community)**

---

**Hai bisogno di aiuto?** Vedi `README.md` completo per guida dettagliata allo sviluppo!

🐒 Happy Coding!