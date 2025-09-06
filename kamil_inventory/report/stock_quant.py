# -*- coding:utf-8 -*-

from odoo import models, fields, api, _


class StockQuant(models.Model):
	_inherit = 'stock.quant'

	product_id = fields.Many2one(
		'product.product', 'Product',
		ondelete='restrict', readonly=True, required=True, index=True)
	# categ_id = fields.Many2one(related='product_id.categ_id', store=True)
	category_id = fields.Many2one('product.category')


	@api.depends('product_id')
	def _get_categ_id(self):
		self.category_id = self.product_id.categ_id.id