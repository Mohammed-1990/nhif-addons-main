# -*- -*-
from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class WizBalanceSheet(models.TransientModel):
	_name = 'wiz.balance.sheet'

	# date_from = fields.Date('Date From', default = lambda self: date(date.today().year, 1, 1), required=True)

	date_to = fields.Date('Date To', default=lambda self: fields.Date.today(), required=True)
	date_from_ = fields.Date('Date From', default=lambda self: date(date.today().year, 1, 1))
	date_to_ = fields.Date(default=lambda self: fields.Date.today())
	revenue_account_id = fields.Many2one("account.account", compute="get_expense_accounts_domain")

	@api.multi
	def get_expense_accounts_domain(self):
		# expense_account_ids = self.env['account.account'].search(['|',('code','=ilike','2%'),('code','=ilike','3%')])._ids
		# return [('id', 'in', expense_account_ids )]
		for account_id in self.env['account.account'].search([('code', '=ilike', '41')]):
			self.revenue_account_id = account_id

	@api.model
	def get_41_id(self):
		for account_ids in self.env['account.account'].search([('code','=ilike','41')]):
			self.revenue_account_id = account_ids.id

	company_ids = fields.Many2many('res.company', string='The Companies', default= lambda self:[(4, self.env.user.company_id.id )] , required=True)


	@api.multi
	def print_report(self):
		
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
				'date_to' : self.date_to,
				'date_from_': self.date_from_,
				'date_to_': self.date_to_,
				'revenue_account_id': self.revenue_account_id.id,
				'company_ids' : company_ids,
				'selected_company_ids' : self.company_ids._ids,
			},
		}

		return self.env.ref('kamil_accounting_reports.balance_sheet_report').report_action(self, data=data)
	




		