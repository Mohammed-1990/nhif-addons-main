# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class ProductFilter(models.TransientModel):
	_name = 'inv.product.filter'
	_description = 'Product Filter'

	categ_ids = fields.Many2many('product.category',string='Product Category')
	attribute_value_ids = fields.Many2many('product.attribute.value', string='Attribute value')
	product_ids = fields.Many2many('product.product', string='Products')

	@api.onchange('categ_ids')
	def _onchange_categ_ids(self):
		res = {}
		if self.categ_ids:
			res['domain'] = {
				'product_ids':[('categ_id', 'in', self.categ_ids.ids)]
			}
		return res

	@api.onchange('attribute_value_ids')
	def _onchange_attribute_value_ids(self):
		res = {}
		if self.attribute_value_ids:
			res['domain'] = {
				'product_ids':[('attribute_value_ids', 'in', self.attribute_value_ids.ids)]
			}
		return res


	@api.depends('attribute_value_ids','categ_ids')
	def _onchange_attribute_categ(self):
		res = {}
		if self.attribute_value_ids and self.categ_ids:
			res['domain'] = {
				'product_ids':[('attribute_value_ids', 'in', self.attribute_value_ids.ids),('categ_id', 'in', self.categ_ids.ids)]
			}
		return res


	def create_product(self):
		if self._context.get('active_model', '') == 'need.requisition':
			# Create a Purchase Order line with the selected product
			nr_line_obj = self.env['need.requisition.line']
			for product in self.product_ids:
				nr_line_vals = {
					'requests':self._context['active_id'],
					'item_id':product.id,
					'uom':product.uom_id.id,
					'qty':1.0,
					'date':fields.Datetime.now(),
				}
				nr_line = nr_line_obj.create(nr_line_vals)
		return True
		
				









	
