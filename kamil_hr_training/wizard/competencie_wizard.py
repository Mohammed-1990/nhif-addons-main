from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class CompetencieWizard(models.TransientModel):
	_name="competencie.wizard"
	
	employee_ids = fields.Many2many('hr.employee',)
	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)),required=True,)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),required=True,)
	unit_id= fields.Many2one('hr.department')

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
		"""
		employee_list = []
		for employee in self.employee_ids:
			employee_list.append(employee.id)

		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				'date_from': self.date_from,
				'date_to': self.date_to,
				'employee_ids': employee_list,
				'unit_id': self.unit_id.id
			},
		}

		return self.env.ref('kamil_hr_career.hr_competencie_report').report_action(self, data=data)
	
