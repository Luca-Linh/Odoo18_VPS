# -*- coding: utf-8 -*-

from . import models

from odoo import tools

def _install_init_data(cr, registry):
    tools.convert_file(cr, 'partner_address_vn_base', 'data/res.city.csv', None, mode='init', noupdate=True, kind='init')
    tools.convert_file(cr, 'partner_address_vn_base', 'data/res.district.csv', None, mode='init', noupdate=True, kind='init')
    tools.convert_file(cr, 'partner_address_vn_base', 'data/res.ward.csv', None, mode='init', noupdate=True, kind='init')