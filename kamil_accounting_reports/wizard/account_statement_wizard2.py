from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AccountStatementWizard(models.TransientModel):
	_name ='account.statement.wizard'

	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
	type = fields.Selection([('account_statment','Account Statement'),('account_group','Account Group')], string='Type', default='account_statment')
	revenue_account_ids = fields.Many2many("account.account")


	@api.onchange('type')
	def _onchange_type(self):
		res = {}
		domain = []
		if self.type == 'account_statment':
			domain = [('code','=like','1%'),('is_group','=','sub_account')]
		else:
			domain = [('code','=like','1%'),('is_group','=','group')]
		
		res['domain'] = {'revenue_account_ids':domain}
		return res

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
				'revenue_account_ids' : self.revenue_account_ids.ids,
				'type':self.type

			},
		}

		return self.env.ref('kamil_accounting_reports.account_statement_report').report_action(self, data=data)
	