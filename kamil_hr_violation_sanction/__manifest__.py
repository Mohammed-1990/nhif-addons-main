# -*- coding: utf-8 -*-
##############################################################################
#
#    App-script,app-script-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################
{
    'name': 'kamil HR - Violation Sanction',
    'author': "AlmedTech",
    'website': "http://www.almedtech.com",

    'category': 'HR',
    'sequence': 320,

    'summary': 'Warring, Investigation and Violation',
    'description': "Employee violation AND sanction",
    'depends': ['base','hr','kamil_hr_employee_profile','kamil_hr_personal','kamil_hr_benefits_wages','kamil_hr_allowances','kamil_inventory'],

    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/hr_investigation_view.xml',
        'views/warring.xml',
        'views/contravention.xml',
        'views/general_operations.xml',
        'views/employees_allowances.xml',
        

    ],

    'installable': True,
    'application': True,
}
