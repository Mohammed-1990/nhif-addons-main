from odoo import models,fields,api
from datetime import date

class seniorityDegreeWizard(models.TransientModel):
	_name="seniority.degree.wizard"

	degree_id = fields.Many2one("functional.degree",string="Functional Degree" ,required=True,)
	date = fields.Date(string="Committee Formation Date" , required=True,)

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
	"""
		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				'degree_id': self.degree_id.id,
				'data': self.date,
			},
		}

		# use `module_name.report_id` as reference.
		# `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_hr_promotions.seniority_degree_report').report_action(self, data=data)