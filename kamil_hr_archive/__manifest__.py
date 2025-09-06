# -*- coding: utf-8 -*-
{
    'name': "kamil HR - Archive",

    'summary': """
        """,

    'description': """
    """,

    'author': "My Company",
    'website': "http://www.almedtech.com",
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','kamil_hr_employee_profile',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/archive.xml',
        'wizard/employee_file_wizard.xml',
        'report/employee_file_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}