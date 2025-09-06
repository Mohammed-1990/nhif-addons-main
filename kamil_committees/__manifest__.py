# -*- coding: utf-8 -*-
{
    'name': "committees",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "AlmedTech",
    'website': "http://www.gnhsoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '12.0.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','hr','purchase'],

    # always loaded
    'data': [
        # 'security/xx_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml',
        'data/cron.xml',
        'views/templates.xml',
    ],
}
