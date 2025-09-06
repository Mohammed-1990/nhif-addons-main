# *.*  coding:utf-8 *.*

{
	'name': "Kamil Purchase Request",
	'description': "Purchase Request",
	'author': "Muram Makkawi Mubarak",
	'version': "1.0",
	'category': "Purchase Management",
	'sequence': 1,

	'depends': [
		'base',
		'kamil_purchase_qualifiying_suppliers'
		],

	'data': [

		'data/purchase_request_data.xml',
		
		'wizard/product_filter_views.xml',

		
		'views/purchase_request_views.xml',
		'views/purchase_order_views.xml',
		'views/res_company_views.xml',


		'security/ir.model.access.csv',
		'security/purchase_request_security.xml',

		],

	'installable': True,
    'auto_install': True,
    'application' : True

}