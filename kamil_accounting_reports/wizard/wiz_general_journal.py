# -*- -*-
from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class WizGeneralJournal(models.TransientModel):
	_name = 'wiz.general.journal'

	date_from = fields.Date('Date From', default = lambda self: date(date.today().year, 1, 1), required=True)
	date_to = fields.Date('Date To', default = lambda self: date(date.today().year, 12, 31), required=True)


	@api.multi
	def print_report(self):
		"""Call when button 'Print' button clicked.
		"""
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to' : self.date_to,

			},
		}

		return self.env.ref('kamil_accounting_reports.general_journal_report').report_action(self, data=data)
	




		