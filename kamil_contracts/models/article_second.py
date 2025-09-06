# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kamilContractArticleSecond(models.Model):
    _name = 'kamil.contracts.article.second'
    _rec_name = 'name_second'

    name_second = fields.Char(string='second Party Obligation Name', required=True, track_visibility="always")
    content_second = fields.Html('')
    category_sel = fields.Selection([('m', 'Male'), ('f', 'Female')])