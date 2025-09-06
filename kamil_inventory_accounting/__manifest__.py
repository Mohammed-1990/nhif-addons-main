# -*- coding: utf-8 -*-
{
    'name': "Accounting/Inventory Integration",

    'summary': """
        Integration of accounting and inventory""",

    'description': """
        Long description of module's purpose
    """,

    'author': "AlmedTech",
    'website': "http://www.almedtech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','account'],

    # always loaded
    'data': [

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}