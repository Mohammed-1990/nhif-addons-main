from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class WizAccountMove(models.TransientModel):
	_name ='wiz.account.move'

	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)) ,required=True)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),required=True)
	group_ids = fields.Many2many('account.account',string='Groups', required=True)



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
				'group_ids' : self.group_ids.ids

			},
		}

		return self.env.ref('kamil_accounting_reports.account_move_report').report_action(self, data=data)
	