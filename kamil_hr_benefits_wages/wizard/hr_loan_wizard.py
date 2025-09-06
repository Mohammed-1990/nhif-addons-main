from odoo import models,fields,api


class hrLoanWizard(models.TransientModel):
	_name="hr.loan.wizard"

	employee_id = fields.Many2one('hr.employee',)
	loan_type = fields.Many2many('loan.type',)
	date_from = fields.Date()
	date_to = fields.Date()

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		loan_type = []
		for loan in self.loan_type:
			loan_type.append(loan.id)
		data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'employee_id': self.employee_id.id,
                'loan_type': loan_type,
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_hr_benefits_wages.hr_loan_report').report_action(self, data=data)
	
	