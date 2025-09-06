# -*- coding: utf-8 -*-
{
    'name': "kamil HR - Configurations",

    'summary': """
       """,

    'description': """
    """,

    'author': "AlmedTech",
    'website': "http://www.almedtech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','kamil_hr_security'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_views.xml',
        'views/configurations_views.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}