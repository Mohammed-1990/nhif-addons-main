# *.*  coding:utf-8 *.*

{
	'name': "Kamil Purchase Limited Tender",
	'description': "Purchase Limited Tender",
	'author': "Muram Makkawi Mubarak",
	'version': "1.0",
	'category': "Purchase Management",
	'sequence': 2,

	'depends': [
		'kamil_purchase_request',
		'kamil_purchase_public_tender'
		],

	'data': [

		
		'views/limited_tender_views.xml',
		'views/limited_tender_menu.xml',

		# 'report/limited_tender_report.xml',
		'wizard/limited_tender_wiz.xml',
		'report/limited_tender_template.xml',
		
		'data/limited_tender_data.xml',
		],

	'installable': True,
    'auto_install': True,
    'application' : True







}
