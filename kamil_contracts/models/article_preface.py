# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kamilContractArticlePreface(models.Model):
    _name = 'kamil.contracts.article.preface'
    _rec_name = 'name'

    name = fields.Char(string='Preface Name', required=True, track_visibility="always")
    content_p = fields.Html('')
    category_sel = fields.Selection([('m', 'Male'), ('f', 'Female')])