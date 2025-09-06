from odoo import models,fields,api


class HousingFormWizard(models.TransientModel):
    _name="housing.form.wizard"

    date_from = fields.Date('The first month',required=True,)
    date_to = fields.Date('The second month',required=True,)
    branch_id = fields.Many2one('res.company')
    appoiontment_ids = fields.Many2many('appointment.type',)
    employee_ids = fields.Many2many('hr.employee')


    @api.multi
    def get_report(self):
    
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'employee_ids': self.employee_ids.mapped('id'),
                'appoiontment_ids': self.appoiontment_ids.mapped('id'),
                'branch_id': self.branch_id.id,
            },
        }

        return self.env.ref('kamil_hr_benefits_wages.housing_form').report_action(self, data=data)
	
	