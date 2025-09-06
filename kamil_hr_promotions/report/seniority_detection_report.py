from odoo import models,fields,api


class ReportSeniorityDetection(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_promotions.seniority_detection_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        degree_id = data['form']['degree_id']
        domain = []
        if degree_id:
            domain.append(('degree_id','=',degree_id))
        

        docs = []
        count = 1
        for employee in self.env['hr.employee'].search(domain):
            docs.append({
                'number': count,
                'branch': employee.company_id.name,
                'employee': employee.name,
                'birthday': employee.birthday,
                'appoiontment_date': employee.appoiontment_date,
                'last_promotion_date': employee.last_promotion_date,
                'appointment_qualification': employee.appointment_qualification.name,
                })

            count +=1
       

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'degree_id': self.env['functional.degree'].search([('id', '=', degree_id)]).name
        }