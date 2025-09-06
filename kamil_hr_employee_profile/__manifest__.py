# -*- coding: utf-8 -*-
{
    'name': "kamil HR - Employee Profile",

    'summary': """Basic data for employee
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
    'depends': ['base','hr','kamil_hr_configurations','kamil_hr_security'],

    # always loaded
    'data': [
        
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/cron.xml',
        'views/employee_profile.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'security/security_view.xml',
        'report/work_certificate_template.xml',


        # 'views/templates.xml',
        # 'views/leaves_type.xml',
       
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
