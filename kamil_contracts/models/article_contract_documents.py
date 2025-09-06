# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kamilContractArticleDocuments(models.Model):
    _name = 'kamil.contracts.article.documents'
    _rec_name = 'name'

    name = fields.Char(string='documents Name', required=True, track_visibility="always")
    content = fields.Text(required=True)
    category_sel = fields.Selection([('m', 'Male'), ('f', 'Female')]) 