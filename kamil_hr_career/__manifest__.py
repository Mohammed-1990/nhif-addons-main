# -*- coding: utf-8 -*-
{
    'name': "Kamil HR - Career ",

    'summary': """
       """,

    'description': """
    """,

    'author': "AlmedTech",
    'website': "http://www.almedtech.com",

   
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','kamil_hr_employee_profile',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/career.xml',
        'data/sequence.xml',
        'wizard/competencie_wizard.xml',
        'report/competencie_template.xml',

        'wizard/distribution_activities_wizard.xml',
        'report/career_per_distribution_activities_template.xml',

        'wizard/technical_performance_wizard.xml',
        'report/technical_performance_template.xml',
        
        'report/monthly_performance_template.xml',

        # 'wizard/general_performance_report_wizard.xml',
        # 'report/general_performance_report_template.xml',
    
            ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
