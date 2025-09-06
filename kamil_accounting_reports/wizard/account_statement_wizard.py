from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AccountStatementWizard(models.TransientModel):
	_name ='account.statement.wizard'

	# date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)))

	date_from = fields.Date('Date From', default = lambda self: date(date.today().year, 1, 1))
	
	# date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
	date_to = fields.Date(default=lambda self: fields.Date.today())


	type = fields.Selection([('account_statment','Account Statement'),('account_group','Account Group')], string='Type', default='account_statment')
	revenue_account_id = fields.Many2one("account.account" , required=True)
	partner_id = fields.Many2one('res.partner',string='Payment For')
	is_group_by_partners = fields.Boolean(string='Group By Partners')	
	report_type = fields.Selection([('group_by_account','Group By Account'),('per_partner','Per Partner')], default='group_by_account')	


	@api.onchange('type')
	def onchange_type(self):
		res = {}
		domain = []
		if self.type == 'account_statment':
			account_ids_list = []
			account_codes_list = []
			for account_id in self.env['account.account'].search([('is_group','=','sub_account')]):
					if account_id.code not in account_codes_list:
						account_codes_list.append( account_id.code )
						account_ids_list.append(account_id.id)
			domain = [('id','in', account_ids_list )]
		else:
			account_ids_list = []
			account_codes_list = []
			for account_id in self.env['account.account'].search([('is_group','=','group')]):
					if account_id.code not in account_codes_list:
						account_codes_list.append( account_id.code )
						account_ids_list.append(account_id.id)
			domain = [('id','in', account_ids_list )]
		
		res['domain'] = {'revenue_account_id':domain}
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
				'revenue_account_id' : self.revenue_account_id.id,
				'partner_id':self.partner_id.id,
				'code':self.revenue_account_id.code,
				'type':self.type,
				'is_group_by_partners' : self.is_group_by_partners,
				'report_type' : self.report_type,

			},
		}

		return self.env.ref('kamil_accounting_reports.account_statement_report').report_action(self, data=data)
	