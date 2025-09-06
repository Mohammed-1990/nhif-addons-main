# -*- coding:utf-8 -*-
from odoo import models, fields, api


class BudgetExchangeWizardReport(models.TransientModel):
	_name = 'budget.exchange.wizard'
	_description = 'Wizard Budget Exchange Report'

	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
		

	def print_report(self):
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to': self.date_to
			},
		}

				# use `module_name.report_id` as reference.
		# `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_accounting_budget.budget_exchange_report').report_action(self, data=data)

		