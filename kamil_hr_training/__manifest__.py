# -*- coding: utf-8 -*-
{
    'name': "kamil HR - Training",

    'summary': """
        """,

    'description': """
    """,

    'author': "My Company",
    'website': "http://www.almedtech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','kamil_hr_configurations','kamil_hr_career','survey','kamil_hr_security','kamil_contracts'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
         'security/security_view.xml',
         'views/launch_training_program.xml',
         'views/apply_training_program.xml',
         'views/study_mission.xml',
         'views/evaluation_candidates.xml',
         'views/criteria_evaluating_candidates.xml',
         'views/training_needs.xml',
         'views/inevitable_training.xml',
      	 'views/study_training_extension.xml',
         'views/training_course_design.xml',
         'views/program_execution.xml',
         'views/short_training_allowance.xml',
         'report/competencie_gap_template.xml',
         'report/training_allowance.xml',
         'wizard/competencie_wizard.xml',
         'wizard/competencie_gap_wizard.xml',
	     'data/sequence.xml',
         'data/cron.xml',
         'wizard/training_record_wizard.xml',
         'wizard/detailed_postgraduate_studies_wizard.xml',
         'wizard/total_executed_internal_and_external_wizard.xml',
         'wizard/brief_postgraduate_studies_wizard.xml',
         'report/training_record_report_view.xml',
         'report/detailed_postgraduate_studies_report_view.xml',
         'report/total_executed_report_view.xml',
         'report/brief_postgraduate_studies_report_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
