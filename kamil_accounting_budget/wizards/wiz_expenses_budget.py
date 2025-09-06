from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class ExpensesBudgettWizard(models.TransientModel):
	_name ='expenses.items.budget.wizard'

	date_from = fields.Date(default = lambda self: date(date.today().year, 1, 1) )
	date_to = fields.Date(default=lambda self: fields.Date.today())
	
	account_id = fields.Many2one("account.account",domain=lambda self:self.get_expense_accounts_domain())
	
	company_ids = fields.Many2many('res.company', string='The Companies', default= lambda self:[(4, self.env.user.company_id.id )] , required=True)


	@api.multi
	def get_expense_accounts_domain(self):
		
		account_ids_list = []
		account_codes_list = []
		for account_id in self.env['account.account'].search(['|',('code','=ilike','2%'),('code','=ilike','3%')]):
			if account_id.code not in account_codes_list:
				account_codes_list.append( account_id.code )
				account_ids_list.append(account_id.id)
		domain = [('id','in', account_ids_list )]
		return domain
	

	@api.multi
	def get_report(self):

		company_ids = []
		for company_id in self.company_ids:
			if company_id.id not in company_ids:
				company_ids.append( company_id.id )
			for child_company in company_id.child_ids:
				if child_company.id not in company_ids:
					company_ids.append( child_company.id )

		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from' : self.date_from,
				'date_to' : self.date_to,
				'account_id' : self.account_id.id,
				'company_ids' : company_ids,
				'selected_company_ids' : self.company_ids._ids,
			},
		}

		return self.env.ref('kamil_accounting_budget.expenses_budget_items_budget_report').report_action(self, data=data)
	