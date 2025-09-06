# -*- coding: utf-8 -*-
{
    'name': "kamil HR Contract",

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
    'depends': ['base','hr','hr_payroll', 'kamil_hr_benefits_wages',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/hr_contract.xml',
        'views/removing_differences.xml',
        'report/removing_differ_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
