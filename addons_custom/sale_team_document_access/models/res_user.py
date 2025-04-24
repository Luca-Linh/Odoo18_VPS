from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    leader_team_ids = fields.One2many(
        'crm.team',
        'user_id',
        string='Teams Led'
    )
