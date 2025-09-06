from odoo import models,fields,api


class administrativeWizard(models.TransientModel):
	_name="administrative.wizard"

	department_id = fields.Many2one('hr.department',string='Management/Department',)

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'department_id': self.department_id.id,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_hr_structure.administrative_report').report_action(self, data=data)
	
	