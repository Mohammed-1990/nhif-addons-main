from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class CollectionPeriodWizard(models.TransientModel):
	_name ='collection.period.wizard'

	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)),required=True,)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),required=True,)

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				'date_from': self.date_from,
				'date_to' : self.date_to,

			},
		}

		return self.env.ref('kamil_accounting_revenues_collection.account_statement_report').report_action(self, data=data)
	