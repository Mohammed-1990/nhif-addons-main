from odoo import models,fields,api


class JobsGradients(models.TransientModel):
	_name="jobs.gradients.wizard"

	employee_id = fields.Many2one('hr.employee',)

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'employee_id': self.employee_id.id,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_hr_promotions.jobs_gradients_report').report_action(self, data=data)
	
	