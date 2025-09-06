{
	
	'name' : 'Kamil Accounting - Budget Control',
	'Author' : 'Alargm Ahmed - Nada Hassan',
	'application' : True,
	'sequence' : 0,
	'depends' : ['base','kamil_accounting_base','account', 'account_budget','analytic'],
	'data' : [
		'security/ir.model.access.csv',
		'security/budget_rules.xml',
		# 'data/money_sequence_view.xml',		
		'views/account_budget_view.xml',
		'views/budget_operation_view.xml',

		'wizards/wiz_expenses_budget.xml',
		'reports/expenses_budget_report.xml',
		],
}