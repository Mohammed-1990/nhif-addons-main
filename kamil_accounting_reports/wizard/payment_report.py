# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class PaymentReport(models.TransientModel):
	_name = 'wizard.payment.report'
	_description = 'Wizard Payment Report'

	# date_from = fields.Date('Date From',default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
	# date_to = fields.Date('Date To',default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

	date_from = fields.Date('Date From', default = lambda self: date(date.today().year, 1, 1))
	date_to = fields.Date('Date To',default=lambda self: fields.Date.today())


	budget_ids = fields.Many2many('account.analytic.account',string='Budget items', domain=lambda self:self.get_budget_ids_domain())
	partner_ids = fields.Many2many('res.partner',string='Payment For')	



	@api.multi
	def get_budget_ids_domain(self):
		
		account_ids_list = []
		account_codes_list = []
		for account_id in self.env['account.analytic.account'].search(['|','|',('code','=ilike','2%'),('code','=ilike','3%'),('code','=ilike','4%')]):
			if account_id.code not in account_codes_list:
				account_codes_list.append( account_id.code )
				account_ids_list.append(account_id.id)
		domain = [('id','in', account_ids_list )]
		return domain	

	def print_report(self):
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to': self.date_to,
				'budget_ids': self.budget_ids.ids,
				'partner_ids':self.partner_ids.ids
			},
		}

				# use `module_name.report_id` as reference.
		# `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_accounting_reports.payment_report').report_action(self, data=data)

		