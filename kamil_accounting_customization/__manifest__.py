{
	
	'name' : 'Kamil Accounting - Customization',
	'Author' : 'Alargm Ahmed - Nada Hassan',
	'application' : True,
	'sequence' : 0,
	'depends' : ['base','kamil_accounting_base','kamil_accounting_financial_ratification','kamil_accounting_claims', 'kamil_accounting_budget','kamil_accounting_revenues_collection'],
	'data' : [
		'security/ir.model.access.csv',
		'security/customization_rules.xml',
		'views/customization_view.xml',
		'views/customization_result_view.xml',
		
		'wizard/wiz_monthly_allocation_views.xml',
		'reports/monthly_allocation_report_views.xml',
		'reports/customization_report.xml',


		],
}