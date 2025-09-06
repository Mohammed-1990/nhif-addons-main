# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta



class RatificationListReport(models.TransientModel):
	_name = 'wizard.ratification.list.report'
	_description = 'Wizard Ratification List Report'

	# date_from = fields.Date('Date From', default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
	# date_to = fields.Date('Date To', default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))


	date_from = fields.Date('Date From', default = lambda self: date(date.today().year, 1, 1))	
	date_to = fields.Date(default=lambda self: fields.Date.today())


	partner_ids = fields.Many2many('res.partner',string='Payment For')		
	group_id = fields.Many2one('account.analytic.account',string='Groups')

	def print_report(self):
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to': self.date_to,
				'partner_ids':self.partner_ids.ids,
				'group_id':self.group_id.id			},
		}

				# use `module_name.report_id` as reference.
		# `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_accounting_reports.ratification_list_report').report_action(self, data=data)

		