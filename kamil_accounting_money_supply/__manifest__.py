{
	
	'name' : 'Kamil Accounting - Money Supply',
	'Author' : 'Alargm Ahmed - Nada Hassan',
	'application' : True,
	'sequence' : 0,
	'depends' : ['base','kamil_accounting_base','account'],
	'data' : [
		'security/ir.model.access.csv',
		'security/money_supply_rule.xml',
		'data/money_sequence_view.xml',		
		'views/money_supply_view.xml',
		'views/money_movement_view.xml',
		'views/money_supply_request_view.xml',

		'reports/bank_transfer_report2.xml',
		'reports/save_money_supply_report.xml',
		'reports/money_supply_request_report.xml',
		],
}