# -*- -*-
from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class WizClarifications(models.TransientModel):
	_name = 'wiz.clarifications'

	clarification_number = fields.Char(required=True,)
	date_to = fields.Date('Date To', default = lambda self: date(date.today().year, 12, 31), required=True,)
	account_id = fields.Many2one('account.account',string="Item", required=True,)
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id,)

	@api.onchange('clarification_number')
	def _onchange_clarification_number(self):
		self.account_id = False
		if self.clarification_number:
			return {
				'domain':
					{'account_id':[('clarification_number','=',self.clarification_number),('is_group','=','group')]}}

	@api.multi
	def print_report(self):

		company_ids = []
		for company_id in self.company_id:
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
				'clarification_number' : self.clarification_number,
				'account_id' : self.account_id.id,
				'company_id' : self.company_id.id,
				'company_ids': company_ids,
			},
		}

		return self.env.ref('kamil_accounting_reports.clarifications_report').report_action(self, data=data)
	




		