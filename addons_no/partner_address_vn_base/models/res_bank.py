from odoo import api, fields, models


class Bank(models.Model):
    _inherit = 'res.bank'

    ward_id = fields.Many2one('res.ward', 'Ward')
    district_id = fields.Many2one('res.district', 'District')
    city_id = fields.Many2one('res.city', 'City ID')
