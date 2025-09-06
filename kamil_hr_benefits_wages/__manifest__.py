# -*- coding: utf-8 -*-
{
	'name' : 'kamil HR - Benefits and Wages',
	'version' : '0.1',
	'author' : 'AlmedTech',
	'category' : 'hr',
	'summary' : """
		Payroll, Loans, Incentives, 
	""",

	'depends' : ['hr','account', 'kamil_hr_employee_profile', 'hr_payroll','kamil_accounting_install',],
	'data': [
		'security/security_view.xml',
		'security/ir.model.access.csv',
		'sequences/sequence.xml',
		'data/hr_payroll.xml',
		'data/cron.xml',
		'views/hr_payroll.xml',
		'views/hr_loan_view.xml',
		'views/hr_projects.xml',
		'views/hr_incentive.xml',
		'views/hr_projects_request.xml',
		'views/temporary_payroll.xml',
		'wizard/hr_loan_wizard.xml',
		'wizard/hr_projects_wizard.xml',
		'wizard/settlement_report_wizard.xml',
		'wizard/balancing_salaries_wizard.xml',
		'wizard/housing_form_wizard.xml',
		'report/incentive_template.xml',
		'report/hr_loan_template.xml',
		'report/hr_projects_template.xml',
		'report/settlement_report_template.xml',
		'report/balancing_salaries_template.xml',
		'report/salary_certificate_template.xml',
		'report/hr_payslips_template.xml',
		'report/incentive_template_dup2.xml',
		'report/incentive_template_dup3.xml',
		'report/housing_form_template.xml',	
	],

	'installable': True,
	'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
