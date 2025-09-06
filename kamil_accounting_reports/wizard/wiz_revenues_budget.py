from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class RevenuesBudgettWizard(models.TransientModel):
	_name ='revenues.budget.wizard'

	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
	budget_ids = fields.Many2many('crossovered.budget', string='Budgets', domain="[('revenues_line_ids','!=',False),('state','=','validate')]")
	budget_item_ids = fields.Many2many('account.analytic.account', string="Budget Items")

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to' : self.date_to,
				'budget_ids' : self.budget_ids.ids,
				'budget_item_ids' : self.budget_item_ids.ids,

			},
		}

		return self.env.ref('kamil_accounting_reports.revenues_budget_report').report_action(self, data=data)
	