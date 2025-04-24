from odoo import api, fields, models


class Ward(models.Model):
    _name = 'res.ward'
    _description = "Wards"

    name = fields.Char('Name')
    code = fields.Char('Code')
    district_id = fields.Many2one('res.district', 'District')
