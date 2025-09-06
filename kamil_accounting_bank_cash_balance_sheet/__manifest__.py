{
	
	'name' : 'Kamil Accounting - Bank/Cash Balance Sheet',
	'Author' : 'Alargm Ahmed - Nada Hassan',
	'application' : True,
	'sequence' : 0,
	'depends' : ['kamil_accounting_financial_ratification','kamil_accounting_revenues_collection'],
	'data' : [
		'security/ir.model.access.csv',
		'security/balance_sheet_rules.xml',
		'views/bank_cash_balance_sheet_view.xml',

		'reports/bank_cash_balance_sheet_report.xml',
		'reports/cheques_not_provided_for_exchange_report.xml',
		'reports/canceled_cheques_report.xml',
		],
}