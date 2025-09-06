# -*- coding: utf-8 -*-
{
    'name': "kamil HR - Transfer",

    'summary': """
       """,

    'description': """
    """,

    'author': "Almedtech",
    'website': "http://www.almedtech.com",
    
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','kamil_hr_employee_profile',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/final_transfer.xml',
        'views/internal_transfer.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}