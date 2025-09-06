from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class PublicTenderwizard(models.TransientModel):
	_name = "qualifiy.suppliers.wizard"

	# area_id = fields.Many2one('area.rehabilitation', domain=lambda self: self._domain_area(),
	# 						  string='Area of rehabilitation')
	# def _domain_area(self):
	# 	requisition =  self.env['purchase.requisition'].browse(self.env.context.get('active_id'))
	# 	vals = []
	# 	if requisition:
	# 		vals = [v.area_rehabilitation_id.id for v in requisition.area_rehabilitation_line_ids]
	# 	return [('id','in',vals)]

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked."""
		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				# 'area_id': self.area_id,
			},
		}

		return self.env.ref('kamil_purchase_qualifiying_suppliers.qualifiying_suppliers_report_pdf').report_action(self, data=data)