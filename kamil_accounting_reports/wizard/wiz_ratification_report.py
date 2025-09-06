# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class RatificationReport(models.TransientModel):
	_name = 'wizard.ratification.report'
	_description = 'Wizard Ratification Report'


	date_from = fields.Date('Date From', default = lambda self: date(date.today().year, 1, 1))
	date_to = fields.Date('Date To', default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
	partner_ids = fields.Many2many('res.partner',string='Payment For')		
	group_id = fields.Many2one('account.analytic.account',string='Groups', domain="[('code','not like','1%')]")

	is_draft = fields.Boolean(string='Draft')
	is_executed = fields.Boolean(string='Executed')
	is_approved = fields.Boolean(string='Approved')
	is_payment_created = fields.Boolean(string='Payment Created')
	is_payment_confirmed = fields.Boolean(string='Payment Confirmed')
	is_paid = fields.Boolean(string='Paid')
	is_canceled = fields.Boolean(string='Is Cancel')



	def print_report(self):
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to': self.date_to,
				'partner_ids':self.partner_ids.ids,
				'group_id':self.group_id.id,
				'is_draft' : self.is_draft,
				'is_executed' : self.is_executed,
				'is_approved' : self.is_approved,
				'is_payment_created' : self.is_payment_created,
				'is_payment_confirmed' : self.is_payment_confirmed,
				'is_paid' : self.is_paid,
				'is_canceled' : self.is_canceled,
			},
		}

				# use `module_name.report_id` as reference.
		# `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_accounting_reports.ratification_report').report_action(self, data=data)

		