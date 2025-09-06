# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kamilContractArticleExplain(models.Model):
    _name = 'kamil.contracts.article.explain'
    _rec_name = 'name'

    name = fields.Char(string='Explain Name', required=True, track_visibility="always")
    content = fields.Html('')
    category_sel = fields.Selection([('m', 'Male'), ('f', 'Female')])