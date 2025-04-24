from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    province_id = fields.Many2one('res.country.province',
                                  string='Province/City',
                                  domain="[('country_id','=', country_id)]",
                                  related='partner_id.province_id',
                                  store=True,
                                  readonly=False
                                  )

    district_id = fields.Many2one('res.country.district',
                                  string='District',
                                  domain="[('province_id','=', province_id)]",
                                  related='partner_id.district_id',
                                  store=True,
                                  readonly=False
                                  )

    ward_id = fields.Many2one('res.country.ward',
                              string='Ward',
                              domain="[('district_id', '=', district_id)]",
                              related='partner_id.ward_id',
                              store=True,
                              readonly=False
                              )