# -*- coding: utf-8 -*-
{
    'name': "kamil HR - End Service",

    'summary': """Employees end of service""",

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
    'depends': ['kamil_hr_employee_profile','kamil_hr_personal','kamil_hr_security',],

    # always loaded
    'data': [
        'views/views.xml',
        'views/after_service.xml',
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'report/experience_certificate_template.xml',
        'report/experience_certificate_template1.xml',
        'report/en_experience_certificate_template.xml',
        'report/en_experience_certificate_template1.xml',
      #  'security/record_rules.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
