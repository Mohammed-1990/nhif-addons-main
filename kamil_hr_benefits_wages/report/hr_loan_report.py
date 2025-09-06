from odoo import models,fields,api
import math

class ReportHrLoan(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_benefits_wages.hr_laon_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        employee_id = data['form']['employee_id']
        if employee_id:
            domain.append(('employee_id','=',employee_id))
        loan_type = data['form']['loan_type']
        if loan_type:
            domain.append(('loan_type','in',loan_type))
        date_from = data['form']['date_from']
        if date_from:
            domain.append(('date','>=',date_from))
        date_to = data['form']['date_to']
        if date_to:
            domain.append(('date','<=',date_to))

        loans = self.env['hr.loan'].sudo().search(domain)

        employee_list = []
        for loan in loans:
            if loan.employee_id not in employee_list:
                employee_list.append(loan.employee_id)

        docs = []
        for employee in employee_list:
            for loan in loans:
                if loan.employee_id == employee:
                    docs.append({'employee':employee.name,
                        'unit':employee.unit_id.name,
                        'job_title':employee.job_title_id.name,
                        'loan':loan.loan_type.name,
                        'date':loan.date,
                        'amount':math.ceil(loan.total_amount*100)/100,                        
                        'paid_amount':math.ceil(loan.total_paid_amount*100)/100,
                        'balance':math.ceil(loan.balance_amount*100)/100,})

       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }