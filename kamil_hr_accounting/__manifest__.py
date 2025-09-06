# -*- coding: utf-8 -*-
{
    'name': "Kamil HR - Accounting",

    'summary': """HR modules accounting
       """,

    'description': """
    """,

    'author': "AlmedTech - Hadeel Ali",
    'website': "http://www.almedtech.com",

   
    'category': 'hr',
    'version': '0.1',
    'application' : True,
    'sequence' : 10,
    'description':''' Return HR ratifications and list to HR 
    ''',
    # any module necessary for this one to work correctly
    'depends': ['kamil_hr_allowances','kamil_hr_benefits_wages','kamil_hr_contract','kamil_hr_missions','kamil_hr_training',],
    'data': [
        'views/accounting.xml',
    ],
}
