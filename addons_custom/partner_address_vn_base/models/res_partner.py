from odoo import api, fields, models, _
from odoo import exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ward_id = fields.Many2one('res.ward', 'Ward')
    district_id = fields.Many2one('res.district', 'District')
    city_id = fields.Many2one('res.city', 'City ID')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',
        default=lambda self: self.env.ref('base.vn'))
    partner_address = fields.Char('Address', compute='_compute_partner_address')


    @api.depends('is_company', 'name', 'parent_id.display_name', 'type', 'company_name')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None, html_format=None, show_vat=None, show_partner_address=None, show_phone=None,show_mobile=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    def _get_name(self):
        res = super(ResPartner, self)._get_name()
        if self._context.get('show_partner_address') and self.partner_address:
            res = "%s\n %s" % (res, self.partner_address)
        if self._context.get('show_phone') and self.phone:
            res = "%s\n %s" % (res, self.phone)
        if self._context.get('show_mobile') and self.mobile:
            res = "%s - %s" % (res, self.mobile)
        return res

    def _compute_partner_address(self):
        for p in self:
            street = p.street or ''
            ward = p.ward_id.name or ''
            district = p.district_id.name or ''
            city = p.city_id.name or ''
            country = p.country_id.name or ''
            p.partner_address = ', '.join([el for el in [street, ward, district, city, country] if el != ''])
