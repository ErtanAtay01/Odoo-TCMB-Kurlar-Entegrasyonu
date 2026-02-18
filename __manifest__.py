# -*- coding: utf-8 -*-
{
    'name': 'TCMB Currency Rates',
    'version': '19.0.1.0.13',
    'category': 'Accounting/Accounting',
    'summary': 'Turkish Central Bank daily currency rates integration',
    'author': 'Community',
    'website': 'https://github.com',
    'license': 'LGPL-3',
    'depends': ['account', 'mail'],
    'external_dependencies': {
        'python': ['requests', 'holidays'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/tcmb_update_action.xml',
        'views/tcmb_currency_rate_views.xml',
        'views/res_config_settings_views.xml',
        'views/tcmb_menus.xml',
        'views/tcmb_cron_run_views.xml',
        'views/tcmb_historical_import_wizard_views.xml',
        'views/res_currency_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
