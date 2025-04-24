# -*- coding: utf-8 -*-
{
    'name': 'Orchid KPI Dashboard',
    'version': '18.0.0.0.0',
    'category': 'Productivity/Discuss',
    'summary': 
        """
        Orchid KPI Dashboard: 
        A fully customizable and interactive Home dashboard for Odoo.
        """,
    'description': 
        """
        The Orchid Dynamic Dashboard is a powerful and configurable dashboard solution 
        designed for Odoo. It provides users with a centralized platform to monitor 
        critical business metrics, track performance, and make data-driven decisions. 
        With dynamic content and auto-refresh capabilities, the dashboard ensures 
        real-time updates and seamless visibility into your operations.

        Key features include:
        - Fully customizable layout and widgets.
        - Real-time data visualization with auto-refresh options.
        - Support for multiple data sources and integrations.
        - Interactive charts, graphs, and KPIs for enhanced insights.
        - User-friendly interface for easy configuration and personalization.

        Ideal for businesses of all sizes, the Orchid Dynamic Dashboard empowers teams 
        to streamline workflows, improve productivity, and stay ahead with actionable 
        insights. Transform your Odoo experience with this dynamic and intuitive 
        dashboard solution.
        """,
    'author': 'Orchid Infosys',
    'company': 'Orchid Infosys',
    'maintainer': 'Orchid Infosys',
    'website': 'https://www.orchidinfosys.com',
    'depends': ['base_setup'],
    'post_init_hook': '_post_init_hook',
    'external_dependencies': {
        'python': ['pandas'],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/user_security.xml',
        'views/odi_hp_config_view.xml',
        'views/odi_hp_setting_view.xml',
        'data/config_data.xml',
        'views/home_page.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'home_dashboard_oi/static/src/css/home_page.css',
            'home_dashboard_oi/static/src/js/home_page.js',
            'home_dashboard_oi/static/src/xml/home_page.xml',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js',
        ],
    },
    'images': ["static/description/banner.png"],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}