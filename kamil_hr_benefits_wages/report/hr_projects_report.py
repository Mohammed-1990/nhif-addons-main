from odoo import models,fields,api
import math

class ReportHrProject(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_benefits_wages.hr_project_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        employee_id = data['form']['employee_id']
        if employee_id:
            domain.append(('employee_id','=',employee_id))
        project_ids = data['form']['project_ids']
        if project_ids:
            domain.append(('project_id','in',project_ids))
        date_from = data['form']['date_from']
        if date_from:
            domain.append(('date','>=',date_from))
        date_to = data['form']['date_to']
        if date_to:
            domain.append(('date','<=',date_to))

        projects = self.env['hr.projects.request'].sudo().search(domain)

        employee_list = []
        for project in projects:
            if project.employee_id not in employee_list:
                employee_list.append(project.employee_id)

        docs = []
        for employee in employee_list:
            for project in projects:
                if project.employee_id == employee:
                    docs.append({'employee':employee.name,
                        'unit':employee.unit_id.name,
                        'job_title':employee.job_title_id.name,
                        'project':project.project_id.name,
                        'date':project.date,
                        'amount':math.ceil(project.total_amount*100)/100,                        
                        'paid_amount':math.ceil(project.total_paid_amount*100)/100,
                        'balance':math.ceil(project.balance_amount*100)/100,})

       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }