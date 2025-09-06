# -*- -*-
from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class WizMonthlyAllocation(models.TransientModel):
	_name = 'wiz.monthly.allocation'

	month = fields.Selection([(1,'January'),(2, 'February'),(3, 'March'),(4, 'April'),(5, 'May'),(6, 'June'),(7, 'July'),(8, 'August'),(9, 'September'),(10, 'October'),(11, 'November'),(12, 'December')], default=fields.Date.today().month,track_visibility='always', required=True)
	year = fields.Char('Year', default=fields.Date.today().year, required=True)


	@api.multi
	def print_report(self):
		"""Call when button 'Print' button clicked.
		"""
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'month': self.month,
				'year' : self.year,

			},
		}

		return self.env.ref('kamil_accounting_reports.monthly_allocation_report').report_action(self, data=data)
	




		