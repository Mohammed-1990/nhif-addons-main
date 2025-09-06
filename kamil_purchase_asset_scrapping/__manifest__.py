# *.* coding:utf-8 *.*

{
	
	'name': "Kamil Purchase - Asset Scrapping",
	'description': 'Purchase Asset Scrapping',
	'auther': "Muram Makkawi Mubarak",
	'version': "1.0",
	'category': "Purchase Management",
	'sequence': 2,

	'depends': [
		'kamil_purchase_qualifiying_suppliers',
		'account_asset',
		'kamil_accounting_assets',
		'kamil_purchase_request'
		],

	'data':[
		'data/scrap_request_data.xml',
		
		'views/asset_scrapping_views.xml',
		'views/asset_views.xml',
		# 'views/book_views.xml',
		# 'views/collection_views.xml',

		'report/scrap_report_view.xml',
		'report/dynamic_scrap_report.xml',
		'security/ir.model.access.csv',
	],

	'installable': True,
	'auto_installable': True,
	'application' : True


}