{
	
	'name': 'Kamil Accounting - Assets',
	'Author': 'Muram Makkawi Mubarak',
	'category': 'Accounting',
	'sequence':0,
	'depends' : [
		'base',
		'kamil_accounting_base',
		'product',
		'account',
		'stock',
		'account_accountant',
		'hr',
		'kamil_accounting_money_supply',
		'html_text',
		'kamil_accounting_revenues_collection',
		'kamil_accounting_financial_ratification',
		],


	'data':[
		'data/account_asset_data.xml',

		'security/ir.model.access.csv',
		'security/assets_rules.xml',

		'wizard/asset_evaluation_views.xml',
		'wizard/wiz_account_asset_report_views.xml',

		'views/product_template_views.xml',
		


		'views/assets_view.xml',

		'reports/a3_paper_format.xml',

		'report/asset_report_views.xml',

		'wizard/wiz_assets_report.xml',

		'wizard/wiz_assets_operations_report.xml',
		
		'wizard/wiz_assets_registry_report.xml',

		'reports/assets_report.xml',
		'reports/assets_operations_report.xml',
		
		'reports/assets_registry_report.xml',

	],
	

	'installable': True,
    'auto_install': True,
	'application': True
}
