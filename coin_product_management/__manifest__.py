{
    'name': "Coin Product Management",
    'summary': "Numismatic coin, medal and collector-set product management for minting & trading companies",
    'description': """
Coin Product Management
========================
Extends products with numismatic technical specifications (metal, finish,
mintage, diameter, weight, issuing authority, year of issue), obverse /
reverse imagery and webshop integration fields, tailored for a
Swiss/Liechtenstein coin minting and trading company (CIT-style high-relief
coins, proof collector sets, medals and custom client tooling).

Features
--------
* Merged into Odoo's standard product views: every Products screen (Sales,
  Inventory, Purchase, ...) shows the coin columns, badges and filters.
* Obverse / reverse image management with WordPress thumbnail URL fields.
* Numismatic technical specifications, customer info and Coin Cover
  (Capsule/Box) variants on product.template.
* Stock shown as "Coins Left", highlighted red at zero.
* "Coins" home-screen app as a shortcut: In-House, Client and Medal products.
* Company-level configuration for default currency, kanban image display and
  low mintage alerting.
* CSV import compatible with standard product export/import column headers.
""",
    'version': '19.0.1.1.0',
    'category': 'Sales/Sales',
    'author': "Dunja",
    'license': 'LGPL-3',
    'depends': ['base', 'product', 'stock', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_attribute_data.xml',
        'views/coin_product_views.xml',
        'views/res_config_settings_views.xml',
        'views/coin_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'coin_product_management/static/src/css/coin_product_management.css',
        ],
    },
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
