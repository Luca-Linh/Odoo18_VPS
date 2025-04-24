from odoo import models, fields, api

class Lead(models.Model):
    _inherit = 'crm.lead'

    province_id = fields.Many2one(
        'res.country.province',
        string='Province/City'
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

    @api.onchange('province_id')
    def _onchange_province_id(self):
        self.district_id = False
        self.ward_id = False

    @api.onchange('district_id')
    def _onchange_district_id(self):
        self.ward_id = False
