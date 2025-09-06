from odoo import models,fields,api,_


class ReportQualificationDetect(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_promotions.qualification_detect_template'

    @api.model
    def _get_report_values(self, docids, data=None):

        degree_id = data['form']['degree_id']
        domain = []
        if degree_id:
            domain.append(('degree_id','=',degree_id))
        

        docs = []
        for employee in self.env['hr.employee'].search(domain):
            promotion_criteria = self.env['promotion.criteria.ratios'].search([],limit=1)
            ratio = 0.0
            for line in promotion_criteria.line_ids:
                if line.qualifcation == employee.appointment_qualification:
                    ratio = line.ratio

            docs.append({
                'employee': employee.name,
                'degree': employee.degree_id.name,
                'appointment_qualification': employee.appointment_qualification.name or _('لا يوجد'),
                'ratio': ratio
                })
        docs = sorted(docs, key = lambda i: i['ratio'],reverse=True)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'degree_id': self.env['functional.degree'].search([('id', '=', degree_id)]).name
        }