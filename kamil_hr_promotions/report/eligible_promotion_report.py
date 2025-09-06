from odoo import models,fields,api
from datetime import date,datetime
from dateutil.relativedelta import relativedelta


class ReportEligiblePromotion(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_promotions.eligible_promotion_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        
        domain = []

        docs = []
        timeline = self.env['promotions.timeline'].search([('state','=','validated')], limit=1)
        for employee in self.env['hr.employee'].search([]):
            for line in timeline.line_ids:
                for category in line.category_id:
                    if category == employee.category_id and line.from_degree_id == employee.degree_id:
                        promotion_date = str((datetime.strptime(str(employee.last_promotion_date), "%Y-%m-%d") + relativedelta(months=(line.years * 12 ))).date())
                        if promotion_date >= date_from and promotion_date <= date_to:
                            docs.append({'employee': employee.name,
                                'branch': employee.company_id.name,
                                'department': employee.department_id.name,
                                'unit': employee.department_id.parent_id.name,
                                'category': employee.category_id.name,
                                'qualifcation': employee.appointment_qualification.name,
                                'degree': employee.degree_id.name,
                                'date':promotion_date,
                                })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
        }