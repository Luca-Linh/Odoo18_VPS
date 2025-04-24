from odoo import api, SUPERUSER_ID

def _post_init_hook(env):
    """Set user_ids to all active users in odi.hp.config and create odi.hp.setting per user with favorites."""
    
    # Fetch all active users
    active_users = env['res.users'].search([('active', '=', True)])
    
    if not active_users:
        return  # No active users, exit

    # Update all odi.hp.config records to include all active users
    # config_records = env['odi.hp.config'].search([])
    # for config in config_records:
    #     config.write({'user_ids': [(6, 0, active_users.ids)]})  # Correct Many2many update

    # Create a separate odi.hp.setting record for each active user (if not exists)
    for user in active_users:
        existing_setting = env['odi.hp.setting'].search([('user_id', '=', user.id)], limit=1)
        if not existing_setting:
            env['odi.hp.setting'].create({
                'user_id': user.id,
                'graph_layout': '4',
                'list_layout': '3',
                'card': '1',
                'company_id': False,
                'theme': 'btn-info',
                'date_slicer': 'cy',
                # Default Favorite Buttons
                'fav1_url': '/',
                'fav1_name': 'Home',
                'fav1_icon': 'fa fa-home',
                'fav1_style': 'btn-info',
                'fav1_tab': '_self',
                
                'fav2_url': 'https://www.odoo.com/',
                'fav2_name': 'Odoo',
                'fav2_icon': 'fa fa-globe',
                'fav2_style': 'btn-warning',
                'fav2_tab': '_blank',

                'fav3_url': 'https://orchidinfosys.com/',
                'fav3_name': 'Orchid Infosys',
                'fav3_icon': 'fa fa-life-globe',
                'fav3_style': 'btn-info',
                'fav3_tab': '_blank',

                'fav4_url': 'https://apps.odoo.com/apps',
                'fav4_name': 'App Store',
                'fav4_icon': 'fa fa-shopping-cart',
                'fav4_style': 'btn-info',
                'fav4_tab': '_blank',

                # Additional Favorite Buttons
                'fav5_url': 'https://orchidinfosys.com/odoo-support-kpi',
                'fav5_name': 'KPI Support',
                'fav5_icon': 'fa fa-ring',
                'fav5_style': 'btn-dark',
                'fav5_tab': '_blank',

                'fav6_url': 'https://chat.deepseek.com/',
                'fav6_name': 'DeepSeek',
                'fav6_icon': 'fa fa-search',
                'fav6_style': 'btn-info',
                'fav6_tab': '_blank',

                'fav7_url': 'https://chatgpt.com/',
                'fav7_name': 'ChatGPT',
                'fav7_icon': 'fa fa-search',
                'fav7_style': 'btn-info',
                'fav7_tab': '_blank',

                'fav8_url': 'https://github.com/orchidinfosys/orchid_home_dashboard',
                'fav8_name': 'GitHub',
                'fav8_icon': 'fa fa-github',
                'fav8_style': 'btn-dark',
                'fav8_tab': '_blank',
            })
