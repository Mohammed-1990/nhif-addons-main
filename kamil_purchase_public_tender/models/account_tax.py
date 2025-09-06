# -*- coding:utf-8 -*-
from odoo import models, fields, api

class AccountTax(models.Model):
	_inherit = 'account.tax'

	tax_type = fields.Selection([('deduct','Deduct'),('addition','Addition')], string='Type', default='deduct')
		