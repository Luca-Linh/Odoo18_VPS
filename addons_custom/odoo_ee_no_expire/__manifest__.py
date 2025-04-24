
{
    "name": "Odoo EE No Expiration",
    "version": "18.0.1.0",
    "author": "Justin Le Anh Tuan <justin.le.1105@gmail.comm>",
    "category": "Tools",
    "license": "LGPL-3",
    "sequence": 2,
    "summary": """
    Database no expired with enterprise edition.
    """,
    "description": """
    Database no expired with enterprise edition.
    """,
    "depends": ["base", "mail"],
    "data": [],
    "qweb": ["static/src/xml/*.xml", ],
    "demo": [],
    "test": [],
    "css": [],
    "js": [],
    "installable": True,
    "application": True,
    "auto_install": True,
    "post_init_hook": 'update_database_expire',
}
