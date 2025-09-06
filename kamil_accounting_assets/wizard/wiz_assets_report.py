from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AccountReportWizard(models.TransientModel):
	_name ='asset.report'

	date = fields.Date(default=lambda self: fields.Date.today() )

	@api.multi
	def get_report(self):

		first_day = date( self.date.year , 1, 1)
		last_day = date( self.date.year , 12, 31)

		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				'date': self.date,
				'first_day' : first_day,
				'last_day' : last_day,
			},
		}

		return self.env.ref('kamil_accounting_assets.assets_summary_report').report_action(self, data=data)
	