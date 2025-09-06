from odoo import models,fields,api,_


class ReportSeniorityDegree(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_promotions.seniority_degree_template'

    @api.model
    def _get_report_values(self, docids, data=None):

        degree_id = data['form']['degree_id']
        domain = []
        if degree_id:
            domain.append(('degree_id','=',degree_id))
            

        committe_date = data['form']['data']
        

        docs = []
        employees = self.env['hr.employee'].search(domain)
        max_difference = 0
        for employee in employees:
            difference_days = 0
            if employee.last_promotion_date:
                difference_days = (fields.Date.from_string(committe_date)-fields.Date.from_string(employee.last_promotion_date)).days
            if difference_days > max_difference:
                max_difference = difference_days
                
        for employee in employees:

            difference_days = 0
            ratio = 0
            if employee.last_promotion_date:
                if committe_date > str(employee.last_promotion_date):
                    difference_days = (fields.Date.from_string(committe_date)-fields.Date.from_string(employee.last_promotion_date)).days
                else:
                    difference_days = 0
            degree_ratio = self.env['promotion.criteria.ratios'].search([],limit=1).degree_ratio
            if max_difference != 0:
                ratio = (difference_days * degree_ratio)/max_difference
            docs.append({
                'employee': employee.name,
                'degree_id':employee.degree_id.name,
                'last_promotion_date': employee.last_promotion_date or _('لا يوجد'),
                'difference_days':difference_days,
                'ratio':ratio
                })

        docs = sorted(docs, key = lambda i: i['ratio'],reverse=True)

       

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'date': committe_date,
            'degree_id': self.env['functional.degree'].search([('id', '=', degree_id)]).name
        }