from odoo import models,fields,api


class balancingSalariesWizard(models.TransientModel):
    _name="balancing.salaries.wizard"

    date_from = fields.Date('The first month',required=True,)
    date_to = fields.Date('The second month',required=True,)
    branch_id = fields.Many2one('res.company',required=True)
    struct_ids = fields.Many2many("hr.payroll.structure", required=True)
    employee_ids = fields.Many2many('hr.employee')


    @api.multi
    def get_report(self):

        employee_ids = []
        for employee in self.employee_ids:
            employee_ids.append(employee.id)

        struct_ids = []
        for struct in self.struct_ids:
            struct_ids.append(struct.id)
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'employee_ids': employee_ids,
                'branch_id': self.branch_id.id,
                'struct_ids': struct_ids,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        return self.env.ref('kamil_hr_benefits_wages.balancing_salaries').report_action(self, data=data)
	
	