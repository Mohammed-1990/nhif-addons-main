from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AccountOperationsReportWizard(models.TransientModel):
	_name ='asset.operations.report'

	operation_type = fields.Selection([('addition','Addition'),('revaluation','Re-evaluation'),('dispose','Dispose'),('freez','Freez'),('unfreez','unFreez')])

	dispose_type = fields.Selection([('sale','Sale'),('give','Grant'),('lost','Lost or Damaged')], default='sale')


	@api.multi
	def get_report(self):
		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				'operation_type': self.operation_type,
				'dispose_type' : self.dispose_type,
			},
		}

		return self.env.ref('kamil_accounting_assets.assets_operations_report').report_action(self, data=data)
	