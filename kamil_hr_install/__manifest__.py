# -*- coding: utf-8 -*-
{
    'name': "Kamil HR - install modules",

    'summary': """Install HR modules
    NHIF Project
       """,

    'description': """
    """,

    'author': "AlmedTech",
    'website': "http://www.almedtech.com",

   
    'category': 'hr',
    'version': '0.1',
    'application' : True,
    'sequence' : 4,
    'description':''' Install Kamil hr modules
    ''',
    # any module necessary for this one to work correctly
    'depends': ['hr','kamil_hr_configurations','kamil_hr_employee_profile','kamil_hr_allowances','kamil_hr_archive','kamil_hr_benefits_wages','kamil_hr_personal','kamil_hr_career','kamil_hr_contract','kamil_hr_end_service','kamil_hr_leaves','kamil_hr_missions','kamil_hr_promotions','kamil_hr_record_jobs','kamil_hr_structure','kamil_hr_training','kamil_hr_transfer','kamil_hr_violation_sanction','kamil_hr_accounting'],
}
