from odoo import models,fields,api


class reportFinalPromotionAssessment(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_promotions.final_promotion_assessment_template'

    @api.model
    def _get_report_values(self, docids, data=None):

        domain = []
        employee_id = data['form']['employee_id']
        if employee_id:
            domain.append(('employee_id','=',employee_id))
        

        docs = []
        count = 1
        for employee in self.env['hr.employee'].search(domain):
            docs.append({
                'number': count,
                'employee_id': employee.name,
                'seniority_appoiontment':'',
                'seniority_degree':'',
                'last_2years_performance': "",
                'appoiontment': employee.appoiontment_type.name,
                'total_grades':"",
                'order':'',
                'functional_id': employee.functional_id.name,
                'job_number':'',
                })

            count +=1
       

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            # 'employee_id': self.env['hr.employee'].search([('id', '=', employee_id)]).name
        }