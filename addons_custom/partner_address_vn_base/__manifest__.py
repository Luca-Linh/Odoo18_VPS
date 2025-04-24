# -*- coding: utf-8 -*-
##############################################################################
{
    'name': 'Vietnam Address - Địa chỉ Việt Nam',
    'summary': """
Adding and manage address infomation in Vietnam 
""",
    'description': """
- Địa chỉ 3 cấp Việt Nam
- Địa chỉ Việt Nam theo xã/phường, quận/huyện, Tỉnh/Thành phố
    """,
    'author': 'NOS Erp Consulting',
    'version': '18.0.1.0',
    'license': 'OPL-1',
    'currency': 'USD',
    'support': 'odoo@nostech.vn',
    'images': [
        'static/description/cover.png'
    ],
    'depends': ['base', 'contacts'],
    'data': [
        # View
        'views/res_bank.xml',
        'views/res_city.xml',
        'views/res_company.xml',
        'views/res_district.xml',
        'views/res_partner.xml',
        'views/res_ward.xml',
        # Menu
        'menu/menu.xml',
        # Security
        'security/ir.model.access.csv',
    ],
    'post_init_hook': '_install_init_data',
    'auto_install': False,
    'installable': True,
    'category': 'Sales/CRM',
    'application': True,
    'sequence': 10,
}
