# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kamilContractArticleIntroduct(models.Model):
    _name = 'kamil.contracts.article.introduct'
    _rec_name = 'name_introduct'

    name_introduct = fields.Char(string='introduct Name', required=True, track_visibility="always")
    content_introduct = fields.Html('')
    category_sel = fields.Selection([('m', 'Male'), ('f', 'Female')])