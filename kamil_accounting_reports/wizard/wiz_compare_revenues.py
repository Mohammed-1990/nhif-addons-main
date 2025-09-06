from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class CompareRevenuesWizard(models.TransientModel):
	_name ='compare.revenues.wizard'

	date_from1 = fields.Date('From', required="1")
	date_to1 = fields.Date('To', required="1")
	date_from2 = fields.Date('From',required="1")
	date_to2 = fields.Date('To', required="1")
	budget_item_ids = fields.Many2many('account.analytic.account', string="Budget Items")


	account_id = fields.Many2one("account.account",domain=lambda self:self.get_revenue_accounts_domain())
	budget_id = fields.Many2one('crossovered.budget', string='Budget')
	

	@api.multi
	def get_revenue_accounts_domain(self):
		# account_ids = self.env['account.account'].search([('code','=ilike','1%')])._ids
		# return [('id', 'in', account_ids )]
		
		account_ids_list = []
		account_codes_list = []
		for account_id in self.env['account.account'].search([('code','=ilike','1%')]):
			if account_id.code not in account_codes_list:
				account_codes_list.append( account_id.code )
				account_ids_list.append(account_id.id)
		domain = [('id','in', account_ids_list )]
		return domain
	

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from1': self.date_from1,
				'date_to1' : self.date_to1,
				'date_from2': self.date_from2,
				'date_to2' : self.date_to2,
				# 'budget_ids' : self.budget_ids.ids,
				'budget_item_ids' : self.budget_item_ids.ids,
				'account_id' : self.account_id.id,
				'budget_id' : self.budget_id.id, 

			},
		}

		return self.env.ref('kamil_accounting_reports.compare_revenues_report').report_action(self, data=data)
	