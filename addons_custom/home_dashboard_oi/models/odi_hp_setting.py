# -*- coding: utf-8 -*-
import logging
from random import randint
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

class OdiHpSetting(models.Model):
    _name = "odi.hp.setting"
    _description = "Page Setting"

    # Define the selection list for button styles
    BUTTON_STYLES = [
        ('btn-primary', 'Primary'),
        ('btn-secondary', 'Secondary'),
        ('btn-success', 'Success'),
        ('btn-danger', 'Danger'),
        ('btn-warning', 'Warning'),
        ('btn-info', 'Info'),
        ('btn-light', 'Light'),
        ('btn-dark', 'Dark'),
        ('btn-teal', 'Teal'),
    ]

    TARGET_ATTRIBUTES = [
        ('_self', 'Same Tab'),
        ('_blank', 'New Tab'),
    ]

    name = fields.Char(string="Name", readonly=True, default="Settings")
    active = fields.Boolean(default=True, help="If you uncheck the active field, it will disable the record rule without deleting.")
    graph_layout = fields.Selection(
        selection=[('2', 'Two'),('3', 'Three'),('4', 'Four'),('6', 'Six')],
        string='Graph', index=True, required=True, tracking=True, default='3'
    )
    list_layout = fields.Selection(
        selection=[('2', 'Two'),('3', 'Three'),('4', 'Four'),('6', 'Six')],
        string='List', index=True, required=True, tracking=True, default='3'
    )
    card = fields.Selection(
        selection=[('1', 'S'), ('2', 'M'),
        ('3', 'X'), ('4', 'XL')],
        string='Card Size', index=True, required=True, 
        tracking=True, default='1'
    )
    card_style = fields.Selection(
        selection=BUTTON_STYLES,
        string='Card Style', index=True, required=True, 
        tracking=True, default='btn-info'
    )
    company_id = fields.Many2one('res.company', string='Company', index=True, 
        default=False, help="Company related Config")
    user_id = fields.Many2one('res.users', string="User", index=True, 
        default=lambda self: self.env.user, help="User related Config")
    theme = fields.Selection(
        selection=BUTTON_STYLES,
        string='Theme', index=True, required=True, 
        tracking=True, default='btn-info'
    )
    date_slicer = fields.Selection(
        selection=[('cy', 'CY'), ('cm', 'CM'),
        ('lm', 'LM'), ('ly', 'LY'),
        ('wk', 'Week'),('td', 'Today')],
        string='Date Slicer', index=True, required=True, 
        tracking=True, default='cy'
    )

    # Add fav fields with names, icons, and styles
    for i in range(1, 9):
        locals()[f'fav{i}_url'] = fields.Char(string=f"Favourite {i} URL", default="/odoo")
        locals()[f'fav{i}_name'] = fields.Char(string=f"Favourite {i} Name", default="Favorite")
        locals()[f'fav{i}_icon'] = fields.Char(string=f"Favourite {i} Icon", default="fa fa-star")
        locals()[f'fav{i}_style'] = fields.Selection(selection=BUTTON_STYLES, 
            string=f"Favourite {i} Style", default='btn-info')
        locals()[f'fav{i}_tab'] = fields.Selection(selection=TARGET_ATTRIBUTES, 
            string=f"Favourite {i} Target", default='_self')

    def get_settings_data(self, user, company):
        # Define prioritized domain conditions
        domain_list = [
            [('active', '=', True), ('user_id', '=', user.id), ('company_id', '=', company.id)],  # Most specific
            [('active', '=', True), ('company_id', '=', company.id)],  # Less specific
            [('active', '=', True)]  # Least specific (fallback)
        ]

        settings = None
        for domain in domain_list:
            settings = self.search(domain, order="id DESC", limit=1)
            if settings:
                break  # Stop searching if we find a record

        if settings:
            silicer = settings.date_slicer
            # Correctly reference the OdiUserSetting model
            user_silicer = self.env['odi.user.setting'].sudo().get_user_setting(user, company)
            if user_silicer is not None:
                silicer = user_silicer

            return {
                'theme': settings.theme,
                'graph_layout': settings.graph_layout,
                'list_layout': settings.list_layout,
                'card': settings.card,
                'card_style': settings.card_style,
                'user_slicer': silicer,
                'favourites': [
                    {
                        'url': getattr(settings, f'fav{i}_url'),
                        'name': getattr(settings, f'fav{i}_name'),
                        'icon': getattr(settings, f'fav{i}_icon'),
                        'style': getattr(settings, f'fav{i}_style'),
                        'tab': getattr(settings, f'fav{i}_tab') 
                    }
                    for i in range(1, 9)
                ]
            }
        
        # Default settings if no settings found
        return {
            'theme': 'btn-info',  # Default theme
            'graph_layout': '4',  # Default graph layout
            'list_layout': '3',  # Default graph layout
            'card': '2',  # Default card size
            'card_style': 'btn-info',  # Default card Style
            'user_slicer': 'cy',
            'favourites': [
                {
                    'url': '/', 
                    'name': f'Favourite {i}', 
                    'icon': 'fa fa-star',  # FontAwesome default icon
                    'style': 'btn-info',
                    'tab': '_self'
                } 
                for i in range(1, 9)
            ]  # Default favourites
        }


class OdiUserSetting(models.Model):
    _name = "odi.user.setting"
    _description = "User Setting"

    name = fields.Char(string="Name", readonly=True, default="User Settings")
    key = fields.Char(string="Key", required=True, default="Key")
    val = fields.Char(string="Value", required=True, default="Value")
    active = fields.Boolean(default=True, help="If you uncheck the active field, it will disable the record rule without deleting.")
    company_id = fields.Many2one('res.company', string='Company', index=True, 
        help="Company related Config")
    user_id = fields.Many2one('res.users', string="User", index=True, 
         help="Company related Config")

    def get_user_setting(self, user, company):
        # Define prioritized domain conditions
        domain_list = [
            # Most specific: User + Company + Setting ID
            [('active', '=', True), ('user_id', '=', user.id), ('company_id', '=', company.id)],  

            # Fallback: User's settings in any company
            [('active', '=', True), ('user_id', '=', user.id)]  
        ]

        # Iterate through each domain and return the first found setting
        for domain in domain_list:
            user_setting = self.search(domain, limit=1)
            if user_setting:
                return user_setting.val  # Return the value if found
        
        return None  # Return None if no setting is found