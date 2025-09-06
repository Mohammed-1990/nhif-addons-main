# *.*  coding:utf-8 *.*

{
	'name': "Kamil Purchase Public Tender",
	'description': "Purchase Public Tender",
	'author': "Muram Makkawi Mubarak",
	'version': "1.0",
	'category': "Purchase Management",
	'sequence': 2,

	'depends': [
			'kamil_purchase_request','kamil_contracts','purchase_stock'
			],

	'data': [

		'report/tender_book_report.xml',
		# 'report/publice_tender_report.xml',
		
		'data/mail_template_data.xml',


		'report/purchase_report_views.xml',

		'wizard/general_conditions_views.xml',
		'wizard/rejection_views.xml',
		'wizard/request_filter_views.xml',

		'wizard/public_tender_wiz.xml',
		'report/public_tender_template.xml',

		'views/public_tender_views.xml',
		'views/public_tender_menu.xml',
		'views/product_template_views.xml',

		'data/publice_tender_data.xml',

        'views/tender_book_views.xml',
        'views/book_template.xml',
        'views/tender_book_template.xml',
        'views/acount_tax_views.xml',

        'security/ir.model.access.csv',
		'security/stock_rule_views.xml',




		],

	'installable': True,
    'auto_install': True,
    'application' : True






}
