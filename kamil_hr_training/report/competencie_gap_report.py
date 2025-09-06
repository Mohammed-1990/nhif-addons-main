from odoo import models,fields,api
import math

class ReportHrcompetencie(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_training.competencie_gap_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        date_from = data['form']['date_from']
        if date_from:
            domain.append(('date_from','>=',date_from))
        date_to = data['form']['date_to']
        if date_to:
            domain.append(('date_to','<=',date_to))

        competencie_id = data['form']['competencie_id']
        gap_from = data['form']['gap_from']
        gap_to = data['form']['gap_to']

        competencies = self.env['evaluating.merits'].search(domain)
        employee_list = []
        for competencie in competencies:
            if competencie.employee_id not in employee_list:
                employee_list.append(competencie.employee_id)

        docs = []
        for employee in employee_list:
            for competencie in competencies:
                if competencie.employee_id == employee:
                    for line in competencie.line_ids:
                        if competencie_id:
                            if line.merit.id == competencie_id and line.gap_percentage>= gap_from and line.gap_percentage<= gap_to:
                                docs.append({'employee': employee.name,
                                    'department': competencie.department_id.name,
                                    'competencie': line.merit.name,
                                    'employee_level': line.employee_level,
                                    'gap':line.gap,
                                    'gap_percentage':math.ceil(line.gap_percentage*100)/100,
                                   })
                        if not competencie_id:
                            if line.gap_percentage>= gap_from and line.gap_percentage<= gap_to:
                                docs.append({'employee': employee.name,
                                    'department': competencie.department_id.name,
                                    'competencie': line.merit.name,
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