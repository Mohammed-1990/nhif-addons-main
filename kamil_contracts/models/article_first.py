# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kamilContractArticleFirst(models.Model):
    _name = 'kamil.contracts.article.first'
    _rec_name = 'name_first'
    
    name_first = fields.Char(string='First Party Obligation Name', required=True, track_visibility="always")
    content_first = fields.Html('')
    category_sel = fields.Selection([('m', 'Male'), ('f', 'Female')])