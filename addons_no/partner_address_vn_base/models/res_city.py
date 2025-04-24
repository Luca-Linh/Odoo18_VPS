from odoo import api, fields, models


class City(models.Model):
    _inherit = 'res.city'
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    code = fields.Char('Code')
