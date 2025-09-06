# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta



class WizBankStatementReport(models.TransientModel):
	_name = 'wizard.bank.statement.report'
	_description = 'Wizard Bank Statement Report'

	# date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
	date_from = fields.Date(default = lambda self: date(date.today().year, 1, 1))

	date_to = fields.Date(default=lambda self: fields.Date.today())


	# date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))


	bank_id = fields.Many2one('account.journal', domain="[('type','=','bank')]" ,string='Bank Selected')
			

	def print_report(self):
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to': self.date_to,
				'bank_id': self.bank_id.id,
			},
		}

				# use `module_name.report_id` as reference.
		# `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_accounting_reports.bank_statement_report').report_action(self, data=data)

		