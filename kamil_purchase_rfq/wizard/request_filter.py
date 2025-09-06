# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class RequestFilterRFQ(models.TransientModel):
	_name = 'request.filter.rfq'
	_description = 'Request Filter'

	request_ids = fields.Many2many('purchase.request', string='Requests', domain=lambda self:self._domain_request())
	type = fields.Selection([
					('request_for_quotaion','Request For Quotaion(RFQs)'),
					('direct_purchase','Direct Purchase')
					],'Type')



	@api.multi
	def _domain_request(self):
		context = self._context
		
		current_uid = context.get('uid')
		user = self.env['res.users'].browse(current_uid)
		if user.company_id.is_main_company:
			return [('type','=','request_for_quotaion'),('state','=','in_process')]

		else:
			return [('type','=','request_for_quotaion'),('state','=','in_process'),('is_transfer','=','1')]



	@api.model
	def default_get(self, default_fields):
		res = super(RequestFilterRFQ, self).default_get(default_fields)
		request = self.env['purchase.rfq'].browse(self.env.context.get('active_id'))
		res['type'] = request.type
		return res


	def create_product(self):
		data = []
		product_list = []
		if self._context.get('active_model') == 'purchase.rfq':

			order = self.env['purchase.rfq'].browse(self._context.get('active_id'))
			order_lind = self.env['purchase.rfq.line']
			for rec in self.request_ids:
				for line in rec.line_ids:
					if not any(l['product']==line.product_id.id  for l in product_list):
						product_list.append({'product':line.product_id.id,'product_uom_id':line.product_id.uom_po_id.id})

			for x in product_list:
				qty = 0.0
				for rec in self.request_ids:
					for line in rec.line_ids:
						if line.product_id.id == x['product']:
							qty += line.product_qty
				data.append((0,0,{
						'product_id':x['product'],
						'product_qty':qty,
						'product_uom_id':x['product_uom_id']
					}))

			order.line_ids.unlink()
			order.write({'line_ids':data, 'request_ids':[(6,0, [v.id for v in self.request_ids])]})
		