from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class LeaveWizard(models.TransientModel):
	_name="leave.wizard"

	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)),required=True,)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),required=True,)
	employee_id = fields.Many2one("hr.employee")
	department_id = fields.Many2one("hr.department")
	leave_id = fields.Many2one("hr.leave.type")

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		 
		data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to' : self.date_to,
                'employee_id' : self.employee_id.id,
                'department_id' : self.department_id.id,
                'leave_id' : self.leave_id.id
            },
        }

		return self.env.ref('kamil_hr_leaves.leave_report').report_action(self, data=data)
	
	