from odoo import models, fields


class Province(models.Model):
    _name = 'res.country.province'
    _description = 'Province'
    _order = 'code'

    code = fields.Char(string='Mã Tỉnh/TP', required=True)
    name = fields.Char(string='Tên Tỉnh/TP')
    state_id = fields.Many2one('res.country.state', string='Tỉnh/TP')
    country_id = fields.Many2one('res.country', string='Quốc Gia', required=True)
    district_ids = fields.One2many('res.country.district', 'province_id')
