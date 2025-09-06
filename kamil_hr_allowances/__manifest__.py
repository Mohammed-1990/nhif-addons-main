# -*- coding: utf-8 -*-
{
    'name': "kamil HR - Allowances",

    'summary': """
        """,

    'description': """
    """,

    'author': "AlmedTech",
    'website': "http://www.almedtech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','kamil_hr_configurations','kamil_hr_benefits_wages'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/hr_allowance.xml',
        'views/meal_allowance.xml',
        'views/allowance_allowance.xml',
        'views/inclination_allowance.xml',
        'views/special_allowance.xml',
        'views/hr_account_config.xml',
        'report/meal_allowance_template.xml',
        'report/allowances_template.xml',
        'report/inclination_allowance_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
