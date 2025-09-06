{
	
	'name' : 'Kamil Accounting - Claims',
	'Author' : 'Alargm Ahmed - Nada Hassan',
	'application' : True,
	'sequence' : 0,
	'depends' : ['base','kamil_accounting_base','account','account_accountant','html_text', 'kamil_accounting_financial_ratification'],
	'data' : [
		
		'security/ir.model.access.csv',
		'security/claim_rules.xml',
		'data/claim_sequence.xml',
		'views/claim_view.xml',
		'views/claim_complex_view.xml',

		'views/integration_info_view.xml',
	],

}
