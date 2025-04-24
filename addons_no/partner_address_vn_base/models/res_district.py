from odoo import api, fields, models, _


class District(models.Model):
    _name = 'res.district'
    _description = "Districts"

    name = fields.Char('Name')
    code = fields.Char('Code')
    city_id = fields.Many2one('res.city', 'City')
    transfer_fee = fields.Float('Transfer Fee')

    @api.model
    def get_transfer_fee(self, data):
        district = self.search([('code', '=', data.get('district_code', False))])
        if district:
            return {'transfer_fee': district[0].transfer_fee}
        else:
            return {'err': "District Code is not exist"}
