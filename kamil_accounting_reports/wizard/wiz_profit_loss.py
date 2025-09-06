# -*- -*-
from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class WizProfitLoss(models.TransientModel):
	_name = 'wiz.profit.loss'

	date_from = fields.Date('Date From', default = lambda self: date(date.today().year, 1, 1), required=True)
	date_to = fields.Date('Date To', default = lambda self: date(date.today().year, 12, 31), required=True)

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
				'date_from': self.date_from,
				'date_to' : self.date_to,
				'company_ids' : company_ids,
				'selected_company_ids' : self.company_ids._ids,
			},
		}

		return self.env.ref('kamil_accounting_reports.profit_loss_report').report_action(self, data=data)
	




		