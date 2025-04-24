from odoo import models, fields


class Province(models.Model):
    _name = 'res.country.province'
    _description = 'Province'
    _order = 'code'

    code = fields.Char(string='Province Code', required=True)
    name = fields.Char(string='Province Name')
    country_id = fields.Many2one('res.country', string='Country', required=True)
    state_id = fields.Many2one('res.country.state',string='State',required=True)
    district_ids = fields.One2many('res.country.district', 'province_id')
    ward_ids = fields.One2many('res.country.ward','province_id')
