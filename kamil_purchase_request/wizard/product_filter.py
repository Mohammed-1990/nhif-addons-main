# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class ProductFilter(models.TransientModel):
	_name = 'product.filter'
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
		if self._context.get('active_model', '') == 'purchase.order':
			# Create a Purchase Order line with the selected product
			po_line_obj = self.env['purchase.order.line']
			for product in self.product_ids:
				po_line_vals = {
					'order_id':self._context['active_id'],
					'product_id':product.id,
					'product_barcode':product.barcode,
					'name':product.name,
					'product_uom':product.uom_id.id,
					'price_unit':product.standard_price,
					'product_qty':1.0,
					'date_planned':fields.Datetime.now(),
				}
				po_line = po_line_obj.create(po_line_vals)

		else:
			pr_line_obj = self.env['purchase.request.line']
			for product in self.product_ids:
				pr_line_vals = {
					'request_id':self._context['active_id'],
					'product_id':product.id,
					'product_barcode':product.barcode,
					'name':product.name,
					'product_uom':product.uom_id.id,
					'price_unit':product.standard_price,
					'product_qty':1.0,
					'date_planned':fields.Datetime.now(),
				}
				pr_line = pr_line_obj.create(pr_line_vals)

				









	
