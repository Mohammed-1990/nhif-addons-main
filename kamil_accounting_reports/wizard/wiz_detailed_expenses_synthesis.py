from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class DetailedExpensesSythesis(models.TransientModel):
	_name ='detailed.expenses.synthesis.wizard'

	group_ids = fields.Many2many('account.analytic.account',string='Groups', domain="[('code','=ilike','2%')]")
	year = fields.Char('Year', default=fields.Date.today().year, required=True)
	# company_ids = fields.Many2many('res.company', string='Companys')

	
	date_from = fields.Date('Date From', default = lambda self: date(date.today().year, 1, 1), required=True)
	
	date_to = fields.Date(default=lambda self: fields.Date.today(), required=True)



	account_id = fields.Many2one('account.account', domain=lambda self:self.get_expenses_accounts(), string='Select Group', required=True)
	company_ids = fields.Many2many('res.company', string='The Companies', default= lambda self:[(4, self.env.user.company_id.id )] , required=True)


	@api.multi
	def get_expenses_accounts(self):
		account_ids_list = []
		account_codes_list = []

		for account_id in self.env['account.account'].search([('code','=ilike','2%'),('is_group','=','group')]):
			if len(account_id.code) == 2 or len(account_id.code) == 1 :
				if account_id.code not in account_codes_list:
					account_codes_list.append( account_id.code )
					account_ids_list.append(account_id.id)
		return [('id','in',account_ids_list)]



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
				'group_ids': self.group_ids.ids,
				'year' : self.year,
				# 'company_ids' : self.company_ids.ids,
				'company_ids' : company_ids,
				'account_id' : self.account_id.id,

				'date_from' : self.date_from,
				'date_to' : self.date_to,
			},
		}

		return self.env.ref('kamil_accounting_reports.detail_exp_report').report_action(self, data=data)
	