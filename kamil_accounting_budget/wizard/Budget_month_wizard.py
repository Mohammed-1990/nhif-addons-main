# -*- coding:utf-8 -*-
from odoo import models, fields, api


class BudgetMonthWizardReport(models.TransientModel):
	_name = 'budget.month.wizard'
	_description = 'Wizard Budget Month Report'

	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
	budget_ids = fields.Many2many('account.analytic.account',string='Budget items')
		

	def print_report(self):
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to': self.date_to,
				'budget_ids': self.budget_ids.ids
			},
		}

				# use `module_name.report_id` as reference.
		# `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_accounting_budget.budget_month_report').report_action(self, data=data)

		