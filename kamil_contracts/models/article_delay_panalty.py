# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kamilContractArticleDelayPanalty(models.Model):
    _name = 'kamil.contracts.article.delay_panalty'
    _rec_name = 'name'
    
    name = fields.Char(string='Delay Panalty Name', required=True, track_visibility="always")
    content = fields.Html('')
    category_sel = fields.Selection([('m', 'Male'), ('f', 'Female')])    
    