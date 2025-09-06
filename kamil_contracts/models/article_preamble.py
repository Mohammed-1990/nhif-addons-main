# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kamilContractArticlePreaamble(models.Model):
    _name = 'kamil.contracts.article.preamble'  
    _rec_name = 'name'

    name = fields.Char(string='Preamble Name', required=True, track_visibility="always")
    content = fields.Html('')
    category_sel = fields.Selection([('m', 'Male'), ('f', 'Female')])    
    
 
    is_active = fields.Boolean('Active', readonly=True)
