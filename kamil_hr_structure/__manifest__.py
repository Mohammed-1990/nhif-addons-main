# -*- coding: utf-8 -*-
{
    'name': "Kamil HR - Structure",

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
    'depends': ['base','hr','kamil_hr_configurations','kamil_hr_personal'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/salary_structure.xml',
        'views/hr_department.xml',
        'wizard/administrative_structure_wizard.xml',
        'report/administrative_structure_report.xml',
            ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
