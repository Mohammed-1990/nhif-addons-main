{
	
	'name' : 'Kamil Accounting - Base',
	'Author' : 'Alargm Ahmed - Nada Hassan',
	'sequence' : 0,
	'depends' : ['base','account','stock','stock_account','purchase','chart_of_account_hierarchy','analytic','account_reports_followup'],
	'data' : [
		'security/access_groups.xml',
		'security/ir.model.access.csv',
		'security/base_rules.xml',
		'views/base_view.xml',

		'views/accounting_dashboard_view.xml',

		'reports/journal_entiries_report.xml',
		],
}
