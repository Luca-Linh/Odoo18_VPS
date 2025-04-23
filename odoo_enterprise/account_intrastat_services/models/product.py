# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # remove in master
    def _get_valid_intrastat_code_ids(self, valid_intrastat_codes):
        self.ensure_one()
        if 'service' in valid_intrastat_codes and self.type == 'service':
            return valid_intrastat_codes['service']
        return super()._get_valid_intrastat_code_ids(valid_intrastat_codes)

    def _get_valid_intrastat_code_domain(self):
        self.ensure_one()
        country_id = self.env.company.account_fiscal_country_id.id
        if self.type == 'service' and self.env["account.intrastat.code"].search_count([("country_id", "in", (country_id, False)), ("type", "=", "service")], limit=1):
            return ["type", "=", "service"]
        return super()._get_valid_intrastat_code_domain()
