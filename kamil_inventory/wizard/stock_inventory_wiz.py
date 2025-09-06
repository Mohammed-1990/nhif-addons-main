from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class StockInventorywizard(models.TransientModel):
	_name = "stock.inventory.wizard"

	location_id = fields.Many2one('stock.location', 'Location', domain="[('usage','=','internal')]", required=True)

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked."""
		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				'location_id': self.location_id,
			},
		}

		return self.env.ref('kamil_inventory.stock_inventort_report_pdf').report_action(self, data=data)