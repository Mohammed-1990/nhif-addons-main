from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class technicalPerformanceWizard(models.TransientModel):
	_name="technical.performance.wizard"

	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)),required=True,)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),required=True,)
	branch_id = fields.Many2one("res.company")
	employee_id = fields.Many2one("hr.employee")
	unit_id= fields.Many2one('hr.department',domain=[('type','=','general_administration')])

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
                'branch_id':self.branch_id.id,
                'employee_id' : self.employee_id.id,
                'unit_id' : self.unit_id.id,
            },
        }

		return self.env.ref('kamil_hr_career.technical_performance_report').report_action(self, data=data)
	
	