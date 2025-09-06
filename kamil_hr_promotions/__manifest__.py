# -*- coding: utf-8 -*-
{
    'name': "Kamil HR - Promotions",

    'summary': """Employees Promotions & its reports
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
    'depends': ['mail','kamil_hr_employee_profile','kamil_hr_personal',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'views/hr_promotions.xml',
        'views/promotions_timeline.xml',
        'views/promotion_criteria_ratios.xml',
        'data/sequence.xml',
        'wizard/jobs_gradients_wizard.xml',
        'wizard/eligible_promotion_wizard.xml',
        'wizard/implemented_promotions_wizard.xml',
        'wizard/seniority_detection_wizard.xml',

        'wizard/qualification_detect_wizard.xml',
        'wizard/seniority_appoiontment_wizard.xml',
        'wizard/seniority_degree_wizard.xml',
        
        'report/jobs_gradients_template.xml',
        'report/eligible_promotion_template.xml',
        'report/implemented_promotions_template.xml',
        'report/seniority_detection_template.xml',

        'report/qualification_detect_template.xml',
        'report/seniority_appoiontment_template.xml',
        'report/seniority_degree_template.xml',
        

            ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
