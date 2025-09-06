    # -*- coding: utf-8 -*-
{
    'name': "Contracts management module",

    'summary': "This module will manage all contract types on NHIF",

    'description': " Kamil contract management mdule",

    'author': "Tariq@almedTech.com",
    'website': "http://www.almedtech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'contract',
    'version': '2.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase_requisition','purchase','hr','kamil_accounting_financial_ratification','kamil_hr_configurations','kamil_hr_benefits_wages','mail'],

    # always loaded
    'data': [
        'security/xx_security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/sequence.xml',
        'views/contract.xml',
        'views/extension.xml',
        'views/article_introduct.xml',
        'views/article_preface.xml',
        'views/article_first.xml',
        'views/article_second.xml',
        'views/article_preamble.xml',
        'views/article_explain.xml',
        'views/article_documents.xml',
        'views/article_delay_panalty.xml',
        'views/article_conflict_resolution.xml',
        'views/terminate.xml',
        'views/contract_claims.xml',
        'security/contract_rules.xml',
        # 'views/contacts.xml',
        'report/report.xml',
        'report/contract_report.xml',

        
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}