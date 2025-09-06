# *.* coding:utf-8 *.*
from odoo import models, fields, api

class WizAccountAssetReport(models.TransientModel):
	_name = 'wiz.account.asset.report'
	_description = 'Wizard Account Asset Report'

	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
	category_id = fields.Many2one('account.asset.category', 'Category')


	def print_report(self):
		""" Call when button 'Print' button click
		"""
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to': self.date_to,
				'category': self.category_id.id
			},
		}

				# use `module_name.report_id` as reference.
		# `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_accounting_assets.asset_report').report_action(self, data=data)

		