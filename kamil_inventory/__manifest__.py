# -*- coding: utf-8 -*-
{
    'name': "kamil_inventory",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','stock','hr','kamil_purchase_request','default_inventory_translation', 'account'],

    # always loaded
    'data': [
        'security/inventory_security_views.xml',
        'security/ir.model.access.csv',

        'data/adjustment_cron.xml',
        'data/need_requisition_data.xml',
        'data/new_item_add_data.xml',
        'data/scrap_data.xml',
        'data/stock_picking_data.xml',
        
        'views/res_config_views.xml',
        'views/need_request_views.xml',
        'views/stock_views.xml',
        'views/adjustment_views.xml',
        'views/scrap_views.xml',
        'views/new_item_views.xml',
        'views/product_views.xml',

        'wizard/item_card_wizard_views.xml',
        # 'wizard/stock_immediate_transfer_views.xml',
        
        'report/stock_quant_views.xml',
        'report/stock_move_views.xml',
        'report/item_card_views.xml',

        # 'report/item_card_views_test.xml',
        # 'views/purchase_views.xml',

        'wizard/stock_inventory_wiz.xml',
        'report/stock_inventory_template.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}