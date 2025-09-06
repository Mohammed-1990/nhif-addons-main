# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kamilContractArticleConflictResolution(models.Model):
    _name = 'kamil.contracts.article.conflict_resolution'
    _rec_name = 'name'
    _description = 'conflict Resolution'
    _order = 'id desc'
    _inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']	
	
    
    name = fields.Char(string='Conflict Resolution Name', required=True, track_visibility="always")
    content = fields.Html('')
    category_sel = fields.Selection([('m', 'Male'), ('f', 'Female')])    
    
 