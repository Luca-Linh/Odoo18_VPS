# -*- coding: utf-8 -*-
{
    'name': 'Vietnam Address',
    'summary': """The Vietnam Address Base module is an extension for the Odoo system designed to provide a comprehensive database of addresses in Vietnam.""",
    'author': 'Vũ Tiến Linh',
    'license': 'LGPL-3',
    'category': 'Extra Tools',
    'version': '18.0.1.0',
    'support': 'vutienlinh412001@gmail.com',
    'depends': ['base','crm','contacts','sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/sale_order_team_leader_rule.xml',
        # 'data/res_country_state_data.xml',
        'data/res.country.province.csv',
        'data/res.country.district.csv',
        'data/res.country.ward.csv',
        'views/res_country_province_views.xml',
        'views/res_country_district_views.xml',
        'views/res_country_ward_views.xml',
        'views/res_partner_views.xml',
        'views/crm_lead_views.xml',
        'views/res_company_views.xml',
        'views/menu_views.xml'
    ],
    'images': ['static/description/thumbnail.png'],
    'application': True,
    'installable': True,
}
