# *.*  coding:utf-8 *.*

{
	'name': "Kamil Purchase RFQ",
	'description': "Purchase RFQ",
	'author': "Muram Makkawi Mubarak",
	'version': "1.0",
	'category': "Purchase Management",
	'sequence': 1,

	'depends': [
		'kamil_purchase_request', 
		'kamil_purchase_public_tender',

		],

	'data': [

		'data/rfq_data.xml',
		
		# 'report/rfq_report_views.xml',
		'wizard/direct_purchase_wiz.xml',
		'wizard/purchase_rfq_wiz.xml',
		'report/direct_purchase_template.xml',
		'report/purchase_rfq_template.xml',

		
		'views/request_for_quotation_views.xml',
		'views/purchase_order_views.xml',



		'security/ir.model.access.csv',
		'security/purchase_rfq_security.xml',

		],

	'installable': True,
    'auto_install': True,
    'application' : True






}