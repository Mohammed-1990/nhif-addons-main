from odoo import models,fields,api
import math

class ReportHrcompetencie(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_career.hr_competencie_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        unit_id = data['form']['unit_id']
        if unit_id:
            domain.append(('unit_id','=',unit_id))
        employee_ids = data['form']['employee_ids']
        if employee_ids:
            domain.append(('id','in',employee_ids))
        employees = self.env['hr.employee'].search(domain)
        
        domain = []
        employee_list = []
        for employee in employees:
            employee_list.append(employee.id)
        docs = []   
        date_from = data['form']['date_from']
        if date_from:
            domain.append(('date_from','>=',date_from))
        date_to = data['form']['date_to']
        if date_to:
            domain.append(('date_to','<=',date_to))
        if employee_list:
            domain.append(('employee_id','in',employee_list))

            competencies = self.env['evaluating.merits'].search(domain)

            employee_list = []
            for competencie in competencies:
                if competencie.employee_id not in employee_list:
                    employee_list.append(competencie.employee_id)

            for employee in employee_list:
                for competencie in competencies:
                    if competencie.employee_id == employee:
                        for line in competencie.line_ids:
                            docs.append({'employee': employee.name,
                                'unit': employee.unit_id.name,
                                'competencie': line.merit.name,
                                'required_level': line.required_level,
                                'employee_level': line.employee_level,
                                'gap':line.gap,
                                'gap_percentage':math.ceil(line.gap_percentage*100)/100,
                               })

       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
        }