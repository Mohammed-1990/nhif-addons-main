# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class BudgetMonthly(models.TransientModel):
	_name = 'wizard.budget.monthly.report'
	_description = 'Wizard Budget Month Report'

	date_from = fields.Date('Date From', default = lambda self: date(date.today().year, 1, 1) )
	date_to = fields.Date('Date To', default = lambda self: date(date.today().year, 12, 31)  )
	group_id = fields.Many2one('account.analytic.account',string='Groups')
	account_id = fields.Many2one('account.account', string='Group', domain=lambda self:self.get_accounts_domain())

	budget_id = fields.Many2one('crossovered.budget', string='Budget', domain=[('state','in',('validate','done'))])





	@api.multi
	def get_accounts_domain(self):
		expense_account_ids = self.env['account.account'].search(['|','|',('code','=ilike','1%'),('code','=ilike','2%'),('code','=ilike','3%'),('is_group','=','group')])._ids
		return [('id', 'in', expense_account_ids )]
	


	def print_report(self):

		if self.account_id:
			group = self.account_id.budget_item_id.id
		else:
			group = False

		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to': self.date_to,
				'group_id': group,
				'account_id' : self.account_id.id,
				'budget_id' : self.budget_id.id,
			},
		}

				# use `module_name.report_id` as reference.
		# `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_accounting_reports.budget_monthly_report').report_action(self, data=data)

		