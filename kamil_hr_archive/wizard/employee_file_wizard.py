from odoo import models,fields,api
from datetime import date

class employeeFile(models.TransientModel):
	_name="employee.file.wizard"


	employee_ids = fields.Many2many('hr.employee',string="Employees")

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		employee_ids = []
		for employee in self.employee_ids:
			employee_ids.append(employee.id)
		data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'employee_ids': employee_ids,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_hr_archive.employee_file_report').report_action(self, data=data)
	
	