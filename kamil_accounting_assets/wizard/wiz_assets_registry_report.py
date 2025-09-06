from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AssetsRegistryReportWizard(models.TransientModel):
	_name ='asset.registry.report'

	date = fields.Date(default=lambda self: fields.Date.today())
	asset_category_ids = fields.Many2many('account.asset.category', string='Catgories')

	@api.multi
	def get_report(self):

		first_day = date( self.date.year , 1, 1)
		last_day = date( self.date.year , 12, 31)

		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				'date': self.date,
				'first_day' : first_day,
				'last_day' : last_day,
				'asset_category_ids' : self.asset_category_ids._ids,
			},
		}

		return self.env.ref('kamil_accounting_assets.assets_registry_report').report_action(self, data=data)
	