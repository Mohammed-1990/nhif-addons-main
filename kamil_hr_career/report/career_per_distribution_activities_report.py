from odoo import models,fields,api


class ReportDistributionActivities(models.AbstractModel):
    _name = 'report.kamil_hr_career.distribution_activities_report_view'

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
        for performance in performances:
            activities = []
            for activity in performance.activities_line_ids:
                activities.append({
                    'main_activity':activity.main_activity,
                    'sub_activity':activity.sub_activity,
                    'weight':activity.weight,
                    'date_from':activity.date_from,
                    'date_to':activity.date_to,
                    'execution_date':activity.execution_date,
                    'notes':activity.notes,})
            docs.append({
                'employee':performance.employee_id.name,
                'department':performance.employee_id.department_id.name,
                'job':performance.employee_id.functional_id.name,
                'activities':activities,
                'date_from':date_from,
                'date_to':date_to,
                'unit_id':unit_id,})

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }