# -*- coding: utf-8 -*-
{
    'name': "kamil HR - Leaves",

    'summary': """
    """,

    'description': """
    HR  Leaves for company 
    """,

    'author': "AlmedTech",
    'website': "http://www.almedtech.com",

    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_holidays','project_timesheet_holidays','kamil_hr_employee_profile','kamil_hr_personal'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/leaves_request.xml',
        'views/leaves_type.xml',
        'views/hr_leave_allocation.xml',
        'views/leave_interrupt.xml',
        'wizard/leave_wizard.xml',
        'report/leave_template.xml',
        'report/leave_certificate_template.xml',
        'report/work_directly_template.xml',
        'data/cron.xml'
       
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
