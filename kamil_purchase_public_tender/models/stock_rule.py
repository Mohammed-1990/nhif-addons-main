# -*- coding:utf-8 -*-
from odoo import models, fields, api

class StockRule(models.Model):
	_inherit = 'stock.rule'


	@api.multi
	def _prepare_purchase_request(self,supplier):

		return{
			'admin_id':supplier.admin_id.id,
			'dept_id': supplier.dept_id.id,
			'date':fields.Date.today(),
			'state':'purchase_department',
			
		}

	@api.multi
	def _prepare_purchase_request_line(self, product_id, product_qty, product_uom, po):
	   
		return {
			'name': product_id.name,
			'product_qty': product_qty,
			'product_id': product_id.id,
			'product_uom_id': product_id.uom_po_id.id,
			'request_id': po.id,

		}
	def _make_po_select_admin(self, values, suppliers):
		""" Method intended to be overridden by customized modules to implement any logic in the
			selection of supplier.
		"""
		return suppliers[0]
	@api.multi
	def _run_buy(self, product_id, product_qty, product_uom, location_id, name, origin, values):
		res = super(StockRule, self)._run_buy(product_id=product_id,product_qty=product_qty, product_uom=product_uom, location_id=location_id, name=name, origin=origin, values=values)

		suppliers = product_id.rule_admin_line_ids\
			.filtered(lambda r: (not r.company_id or r.company_id == values['company_id']))
		supplier = self._make_po_select_admin(values, suppliers)


			
		admin_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id.parent_id
		department_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id

		vals = self._prepare_purchase_request(supplier=supplier)

		company_id = values.get('company_id') and values['company_id'].id or self.env.user.company_id.id
		po = self.env['purchase.request'].with_context(force_company=company_id).sudo().create(vals)

		vals = self._prepare_purchase_request_line(product_id, product_qty, product_uom, po)
		self.env['purchase.request.line'].sudo().create(vals)

		print('\n\n\n\n\n\n\n\n\n')
		print('supplier =',supplier.admin_id.name)
		print('######################## Muram ######################')
		print('\n\n\n\n\n\n\n\n\n')

		return res