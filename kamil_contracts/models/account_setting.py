# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
# from docx import Document
# from docx.shared import Inches
from odoo.exceptions import ValidationError
import shutil
import os
class kamilContractAccountSetting(models.Model):
    _name = 'kamil.contracts.account_setting'
    _description = 'Claims account setting'
    _inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']


    
    name = fields.Char(string='Setting Account Name', default='Setting Claim Account Names')    
    # account_code = fields.Char(string='Account Code', required=True, track_visibility="always")
    
    
    account_id = fields.Many2one('account.account',"Account Code", required=True, track_visibility="always")
    stamp = fields.Many2one('account.tax')
    # account_tax = fields.Many2one('account.tax',"Tax Account", required=True, track_visibility="always")
    # analytic_account= fields.Many2one('account.account',"Analytic Account",  track_visibility="always")
    # _sql_constraints = [('medical_service_name_uniqe', 'unique (name_service)','Sorry ! you can not create same name')]
    company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
