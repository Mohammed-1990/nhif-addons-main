{
	
	'name': "Kamil Purchase Qualifying Suppliers",
	'author': "Muram Makkawi Mubabrk",
	'category': 'Purchase Management',
	'version':	"1.0",
	'sequence': 0,

    'depends': [
        'base',
        'mail',
        'hr',
        'purchase',
        'purchase_requisition',
        'purchase_stock',
        'stock',
        'website_form',
        'kamil_accounting_revenues_collection',
        'kamil_accounting_financial_ratification',
        'kamil_committees'
        ],



    'data': [
        

        'security/qualifying_suppliers_security.xml',
        'security/ir.model.access.csv',

        'wizard/announcement_view.xml',
        'wizard/visit_views.xml',
        'wizard/representative_attendance_views.xml',
        'wizard/area_rehabilitaion_views.xml',
        'wizard/wiz_qualifying_suppliers_views.xml',
        'wizard/general_conditions_views.xml',
        'wizard/field_visit_template_views.xml',
        'wizard/visit_template_view.xml',
        'wizard/newspaper_views.xml',
        'wizard/suppliers_valuation_views.xml',

        'wizard/qualify_suppliers_wiz.xml',
        'report/qualifiying_suppliers_report_pdf.xml',

        'report/qualifying_suppliers.xml',
        'report/qualifying_suppliers_template.xml',
        'report/area_rehabilitaion.xml',
        'report/required_documents_report.xml',
        'report/required_documents_report_template.xml',
        'report/visit_report.xml',
        'report/visit_report_template.xml',
        'report/tender_book_report.xml',
        # 'report/qualifying_suppliers_report_views.xml',

        'views/tender_book_template.xml',
        'views/tender_book_views.xml',

        'views/qualifying_suppliers_view.xml',
        'views/qualifying_suppliers_menus.xml',

        'views/res_partner_views.xml',
        
        'views/collection_views.xml',
        
        'data/mail_template_data.xml',
	    'data/qualifying_suppliers_data.xml',
        'data/visit_criteria_data.xml',
        'data/purchase_requisition_data.xml',
        'data/area_rehabilitation_data.xml',
        'data/newspaper_data.xml',
    	],

    'installable': True,
    'auto_install': True,
    'application' : True


}
