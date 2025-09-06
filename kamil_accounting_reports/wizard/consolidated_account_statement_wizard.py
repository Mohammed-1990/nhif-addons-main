from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class ConsolidatedGroupStatementWizard(models.TransientModel):
	_name ='consolidated.group.statement.wizard'

	date_from = fields.Date('Date From', default = lambda self: date(date.today().year, 1, 1), required=True)
	
	date_to = fields.Date(default=lambda self: fields.Date.today(), required=True)
	account_id = fields.Many2one("account.account" , required=True, domain=lambda self:self.get_account_domain() )
	company_ids = fields.Many2many('res.company', string='The Companies', default= lambda self:[(4, self.env.user.company_id.id )] , required=True)
	report_type = fields.Selection([('account_statement','Account Statement'),('group_statement','Group Statement')], default='account_statement', string='Type')
	

	@api.onchange('report_type')
	def onchange_report_type(self):
		res = {}
		domain = []
		if self.report_type == 'account_statement':
			domain = [('is_group','=','sub_account')]
		else:
			domain = [('is_group','=','group')]
		
		res['domain'] = {'account_id':domain}
		return res


	@api.multi
	def get_account_domain(self):
		account_ids = []
		account_codes = []
		for account in self.env['account.account'].search([('is_group','=','group')]):
			if account.code not in account_codes:
				account_codes.append( account.code )
				account_ids.append( account.id )
		return [('id','in',account_ids)]
		

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
			'form': {
				'date_from': self.date_from,
				'date_to' : self.date_to,
				'account_id' : self.account_id.id,
				'company_ids' : company_ids,
				'selected_company_ids' : self.company_ids._ids,
			},
		}
		if self.report_type == 'account_statement':
			return self.env.ref('kamil_accounting_reports.consolidated_account_statement_report').report_action(self, data=data)
		if self.report_type == 'group_statement':
			return self.env.ref('kamil_accounting_reports.consolidated_group_statement_report').report_action(self, data=data)
	