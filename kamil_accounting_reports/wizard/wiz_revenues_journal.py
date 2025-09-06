from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class WizRevenuesJournal(models.TransientModel):
	_name ='wiz.revenues.journal'

	date_from = fields.Date(default = lambda self: date(date.today().year, 1, 1)  ,required=True)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),required=True)
	group_id = fields.Many2one('account.account',string='Groups', domain=lambda self:self.get_revenue_accounts_domain() )


	@api.multi
	def get_revenue_accounts_domain(self):
		
		account_ids_list = []
		account_codes_list = []
		for account_id in self.env['account.account'].search([('code','=ilike','1%')]):
			if account_id.code not in account_codes_list:
				account_codes_list.append( account_id.code )
				account_ids_list.append(account_id.id)
		domain = [('id','in', account_ids_list )]
		return domain

	@api.multi
	def print_report(self):
		"""Call when button 'Print' button clicked.
		"""
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to' : self.date_to,
				'group_id' : self.group_id.id

			},
		}

		return self.env.ref('kamil_accounting_reports.revenues_journal_report').report_action(self, data=data)
	