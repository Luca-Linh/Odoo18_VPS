from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    province_id = fields.Many2one('res.country.province',
                                  string='Province/City',
                                  )

    district_id = fields.Many2one(
        comodel_name='res.country.district',
        string='District',
        domain="[('province_id', '=', province_id)]"
    )
    ward_id = fields.Many2one(
        comodel_name='res.country.ward',
        string='Ward',
        domain="[('district_id', '=', district_id)]"
    )
