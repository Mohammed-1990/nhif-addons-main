{
	
	'name' : 'Kamil Accounting - Revenues Collection',
	'Author' : 'Alargm Ahmed - Nada Hassan',
	'application' : True,
	'sequence' : 0,
	'depends' : ['base','account','account_accountant','hr','kamil_accounting_money_supply','html_text'],
	'data' : [
		
		'security/ir.model.access.csv',
		'security/collection_rules.xml',
		'data/collection_sequence_view.xml',
		'views/subscribers_view.xml',
		'views/collection_view.xml',
		'views/collector_view.xml',
		'views/receipt_67_view.xml',
        'views/account_journal.xml',
		'views/banking_application.xml',
        		'views/account_move.xml',
        'wizard/cancel_receipt_e_15_wizard.xml',
        'wizard/returned_to_collector_wizard.xml',
        'reports/revenue_receipt_report.xml',
		],
}