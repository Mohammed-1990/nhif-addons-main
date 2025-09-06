# *.* coding:utf-8 *.*

from odoo import models, fields, api
from datetime import datetime



class WizQualifyingSuppliers(models.TransientModel):
	_name = 'wiz.qualifying.suppliers'
	_description = 'Wiz qualifying suppliers'

	area_id = fields.Many2one('area.rehabilitation',domain=lambda self:self._domain_area(), string='Area of rehabilitation', required=True)
	requisition_id = fields.Many2one('purchase.requisition')
	partner_ids = fields.Many2many('res.partner')

	
	def _domain_area(self):
		requisition =  self.env['purchase.requisition'].browse(self.env.context.get('active_id'))
		vals = []
		if requisition:
			vals = [v.area_rehabilitation_id.id for v in requisition.area_rehabilitation_line_ids]
		return [('id','in',vals)]	

	def action_print(self):
		vals = []
		requisition =  self.env['purchase.requisition'].browse(self.env.context.get('active_id'))
		for rec in requisition.area_rehabilitation_line_ids:
			if rec.area_rehabilitation_id.id == self.area_id.id:
				self.partner_ids = rec.partner_ids
		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				'area_id': self.area_id.id,
			},
		}
		return self.env.ref('kamil_purchase_qualifiying_suppliers.report_area').report_action(self)

