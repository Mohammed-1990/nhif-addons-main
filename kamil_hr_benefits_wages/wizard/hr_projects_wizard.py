from odoo import models,fields,api


class hrProjectWizard(models.TransientModel):
	_name="hr.project.wizard"

	employee_id = fields.Many2one('hr.employee',)
	project_ids = fields.Many2many('hr.projects',)
	date_from = fields.Date()
	date_to = fields.Date()

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		project_ids = []
		for project in self.project_ids:
			project_ids.append(project.id)

		data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'employee_id': self.employee_id.id,
                'project_ids': project_ids,
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_hr_benefits_wages.hr_project_report').report_action(self, data=data)
	
	