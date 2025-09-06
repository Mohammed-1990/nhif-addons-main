# -*- coding: utf-8 -*-
{
    'name': "Kamil HR - Record Jobs",

    'summary': """Record jobs & its reports
       """,

    'description': """
    """,

    'author': "AlmedTech",
    'website': "http://www.almedtech.com",

   'category': 'hr',
    'version': '0.1',

    'depends': ['base','hr','kamil_hr_configurations'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/record_jobs.xml',
        'wizard/record_job_function_wizard.xml',
        'report/record_jobs_per_function_template.xml',
        'wizard/record_job_vacancies_wizard.xml',
        'report/record_jobs_per_vacancies_template.xml',
        'wizard/record_job_vacancy_and_busy_wizard.xml',
        'report/record_jobs_per_vacancy_and_busy.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
