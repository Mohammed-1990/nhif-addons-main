from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class CompareRevenuesCompaniesWizard(models.TransientModel):
	_name ='compare.revenues.companies.wizard'

	date_from1 = fields.Date('From', required="1")
	date_to1 = fields.Date('To', required="1")
	date_from2 = fields.Date('From',required="1")
	date_to2 = fields.Date('To', required="1")



	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from1': self.date_from1,
				'date_to1' : self.date_to1,
				'date_from2': self.date_from2,
				'date_to2' : self.date_to2,
			

			},
		}

		# return self.env.ref('kamil_accounting_reports.compare_expenses_comp_report').report_action(self, data=data)
		return self.env.ref('kamil_accounting_reports.compare_companies_report').report_action(self, data=data)
	