# -*- coding: utf-8 -*-
{
    'name': "Kamil Inventory Installer",

    'summary': """
        Installation of kamil_inventory, kamil_inventory_accounting, default_inventory_translation""",

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
    'depends': ['stock','account','kamil_inventory','kamil_inventory_accounting','default_inventory_translation'],

    # always loaded
    'data': [

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application':True,
}