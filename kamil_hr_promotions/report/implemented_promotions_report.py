from odoo import models,fields,api
from datetime import date,datetime
from dateutil.relativedelta import relativedelta


class ReportImplementedPromotion(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_promotions.implemented_promotion_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        domain = []
        if date_from:
            domain.append(('exection_date','>=',date_from))
        if date_to:
            domain.append(('exection_date','<=',date_to))

        

        docs = []
        for promotion in self.env['hr.promotions'].search(domain):
            docs.append({
                'employee': promotion.employee_id.name,
                'branch': promotion.employee_id.company_id.name,
                'unit': promotion.employee_id.department_id.parent_id.name,
                'category': promotion.employee_id.category_id.name,
                'qualifcation': promotion.employee_id.appointment_qualification.name,
                'degree': promotion.employee_id.degree_id.name,
                'appoiontment_date': promotion.employee_id.appoiontment_date,
                'promotion_date': promotion.promotion_date,
                'exection_date': promotion.exection_date,
                })
       

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
        }