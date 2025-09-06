from odoo import models,fields,api


class ReporttechnicalPerformance(models.AbstractModel):


    _name = 'report.kamil_hr_career.technical_performance_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        domain = []
        employee_id = data['form']['employee_id']
        if employee_id:
            domain.append(('employee_id','=',employee_id))
        unit_id = data['form']['unit_id']
        if unit_id:
            domain.append(('unit_id','=',unit_id))
        date_from = data['form']['date_from']
        if date_from:
            domain.append(('date_from','>=',date_from))
        date_to = data['form']['date_to']
        if date_to:
            domain.append(('date_to','<=',date_to))
        branch_id = data['form']['branch_id']
        if branch_id:
            domain.append(('employee_id.company_id','=',branch_id))

        performances = self.env['technical.performance'].search(domain)

        docs = []
        evaluations = []
        for eva in performances:
            for line in eva.evaluation_line_ids:
                if line.activity.name not in evaluations:
                    evaluations.append(line.activity.name)
        evaluations.append('النسبه الكليه')
        for performance in performances:
            list=[]
            for evaluation in evaluations:
                total = 0.00
                for line in performance.evaluation_line_ids:
                    if line.activity.name == evaluation:
                        total += line.evaluation
                if evaluation != 'النسبه الكليه':    
                    list.append(total)
            list.append(performance.total_evaluation)
            docs.append({'employee':performance.employee_id.name,
                'evaluation':list,
                })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'evaluations':evaluations,
            'date_from':date_from,
            'date_to':date_to,
        }