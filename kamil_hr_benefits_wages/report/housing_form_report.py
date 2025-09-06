from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar


class HousingForm(models.AbstractModel):
    
    _name = 'report.kamil_hr_benefits_wages.housing_form_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        employee_ids = data['form']['employee_ids']
        branch_id = data['form']['branch_id']
        appoiontment_ids = data['form']['appoiontment_ids']

        first_date = datetime.strptime(date_from, '%Y-%m-%d').strftime('%m')
        second_date = datetime.strptime(date_to, '%Y-%m-%d').strftime('%m')


        first_domain = []
        second_domain = []
        employees_domain = []
        docs = []


        if employee_ids:
            employees_domain.append(('id','in',employee_ids))
        if appoiontment_ids:
            employees_domain.append(('appoiontment_type','in',appoiontment_ids))
        if branch_id:
            employees_domain.append(('company_id','=',branch_id))

        for employee in self.env['hr.employee'].search(employees_domain):
            first_domain = [('employee_id','=',employee.id),('date_from','<=',date_from),('date_to','>=',date_from)]
            second_domain = [('employee_id','=',employee.id),('date_from','<=',date_to),('date_to','>=',date_to)]
            first_payslip = self.env['hr.payslip'].sudo().search(first_domain,limit=1)
            second_payslip = self.env['hr.payslip'].sudo().search(second_domain,limit=1)
            
            rules_row = []
            first_payslip_row = []
            second_payslip_row = []
            minues_row = []

            old_basic = 0.00
            old_high_cost = 0.00
            new_basic = 0.00
            new_high_cost = 0.00

            for line in first_payslip.line_ids:
                if line.salary_rule_id.code == 'الابتدائى':
                    old_basic = line.total
                if line.salary_rule_id.code == 'غلاء المعيشة':
                    old_high_cost = line.total


            for line in second_payslip.line_ids:
                if line.salary_rule_id.code == 'الابتدائى':
                    new_basic = line.total
                if line.salary_rule_id.code == 'غلاء المعيشة':
                    new_high_cost = line.total
            
            new_salary = new_basic + new_high_cost
            old_salary = old_basic + old_high_cost
            
            docs.append({ 
                'employee': employee.name,
                'functional': employee.functional_id.name,
                'degree': employee.degree_id.name,
                'old_basic': old_basic,
                'old_high_cost': old_high_cost,
                'old_salary': old_salary,
                'new_basic':new_basic,
                'new_high_cost':new_high_cost,
                'new_salary': new_salary,
                'diff_basic': new_basic - old_basic,
                'diff_high_cost': new_high_cost - old_high_cost,
                'diff_salary': new_salary - old_salary,
                })
       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }


