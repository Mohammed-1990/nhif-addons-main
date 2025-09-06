# -*- coding:utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	rule_admin_line_ids = fields.One2many('rule.administration.line','product_tmpl_id')

class DepartmentLine(models.Model):
	_name = 'rule.administration.line'

	admin_id = fields.Many2one('hr.department', string="Administration")
	dept_id = fields.Many2one('hr.department', 'Department')
	start_date = fields.Date('Start Date')
	end_date = fields.Date('End Date')
	product_tmpl_id = fields.Many2one('product.template')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)
	# product_id = fields.Many2one('product.product', string='Product',related="product_tmpl_id.product_id.id")

