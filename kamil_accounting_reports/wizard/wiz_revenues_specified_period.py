from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class RevenuesSpecifiedPeriodWizard(models.TransientModel):
	_name ='revenues.specified.period.wizard'

	type = fields.Selection([
			('monthly','Monthly'),
			('first_quarter','First Quarter'),
			('second_quarter','Second Quarter'),
			('third_quarter','Third Quarter'),
			('fourth_quarter','Fourth Quarter'),
			('half_year_first','Half Year First'),
			('half_year_second','Half Year Second'),
			('annual','Annual')
			],string='Type', default='monthly')
	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
	revenue_account_ids = fields.Many2many("account.analytic.account",domain=[('is_group','=','group')], required=True)


	account_id = fields.Many2one("account.account",domain=lambda self:self.get_revenue_accounts_domain())
	
	company_ids = fields.Many2many('res.company', string='The Companies', default= lambda self:[(4, self.env.user.company_id.id )] , required=True)




	@api.multi
	def get_revenue_accounts_domain(self):
	
		# account_ids = self.env['account.account'].search([('code','=ilike','1%')])._ids

		account_ids_list = []
		account_codes_list = []
		for account_id in self.env['account.account'].search([('code','=ilike','1%')]):
			if account_id.code not in account_codes_list:
				account_codes_list.append( account_id.code )
				account_ids_list.append(account_id.id)
		domain = [('id','in', account_ids_list )]
		return domain

		# return [('id', 'in', account_ids )]
	

	@api.multi
	def get_budget_item_domain(self):
		budget_items_ids = []
		for account in self.env['account.account'].search([('is_group','=','sub_account')]):
			if account.parent_budget_item_id:
				budget_items_ids.append(str(account.parent_budget_item_id.code) )
		if budget_items_ids:
			return [('code','in', budget_items_ids)]
		return []





	@api.onchange('type')
	def _onchange_type(self):
		if self.type == 'monthly':
			self.date_from =  fields.Date.to_string(date.today().replace(day=1))
			self.date_to = fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())
		else:
			month = month2 = 1
			if self.type == 'first_quarter':
				month = 1
				month2 = 3
			if self.type == 'second_quarter':
				month = 4
				month2 = 6
			if self.type == 'third_quarter':
				month = 7
				month2 = 9
			if self.type == 'fourth_quarter':
				month = 10
				month2 = 12
			if self.type == 'half_year_first':
				month = 1
				month2 = 6
			if self.type == 'half_year_second':
				month = 7
				month2 = 12
			if self.type == 'annual':
				month = 1
				month2 = 12

			self.date_from = fields.Date.to_string(datetime(fields.Date.today().year,int(month),1))
			date_month = datetime(fields.Date.today().year,int(month2),1)
			self.date_to = fields.Date.to_string(date_month + relativedelta(day=31))


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
				'date_from': self.date_from,
				'date_to' : self.date_to,
				'revenue_account_ids' : self.revenue_account_ids.ids,
				'account_id' : self.account_id.id,
				'company_ids' : company_ids,
				'selected_company_ids' : self.company_ids._ids,
			},
		}

		return self.env.ref('kamil_accounting_reports.revenues_specified_period_report').report_action(self, data=data)
	