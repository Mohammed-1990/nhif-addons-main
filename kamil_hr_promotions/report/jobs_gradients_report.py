from odoo import models,fields,api


class ReportJobsGradients(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_promotions.jobs_gradients_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        domain = []
        if data['form']['employee_id']:
            domain.append(('employee_id','=',data['form']['employee_id']))

        docs = []
        employees_list = []
        for promotion in self.env['hr.promotions'].search(domain):
            if promotion.employee_id not in employees_list:
                employees_list.append(promotion.employee_id)
        for employee in employees_list:
            for promotion in self.env['hr.promotions'].search(domain):
                if employee == promotion.employee_id:
                    docs.append({'employee':employee.name,
                    'deprtment':promotion.department_id.name,
                    'previous_degree':promotion.current_degree_id.name,
                    'new_degree':promotion.new_degree_id.name,
                    'date':promotion.promotion_date,})

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }