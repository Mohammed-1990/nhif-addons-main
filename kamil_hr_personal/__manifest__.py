# -*- coding: utf-8 -*-
{
    'name': "kamil HR - Personal",

    'summary': """
        """,

    'description': """
    """,

    'author': "My Company",
    'website': "http://www.almedtech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','kamil_hr_employee_profile',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/work_injuries.xml',
        'data/sequence.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}