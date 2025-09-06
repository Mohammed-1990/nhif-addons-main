from odoo import models,fields,api
import math

class ReportHrSettlement(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_benefits_wages.settlement_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        type = data['form']['type']
        appoiontment_type = data['form']['appoiontment_type']
       
        

        rules_list = []
        rules_ids_list = []
        states_list = []
        states_ids_list = []
        if type == 'main':
            com = self.env['res.company'].search([('is_main_company','=',True),('id','not in',[1,7,44])], limit=1)
            states_list.append(com.name)
            payslips = self.env['hr.payslip'].search([('date_from','=',date_from),('date_to','=',date_to),('employee_id.appoiontment_type','in',appoiontment_type),('company_id','=',com.id)],)
        else:
            for company in self.env['res.company'].search([('is_main_company','=',False),('id','not in',[1,7,44])]):
                if company.name not in states_list:
                    states_list.append(company.name)
                if company.id not in states_ids_list:
                    states_ids_list.append(company.id)
            payslips = self.env['hr.payslip'].search([('date_from','=',date_from),('date_to','=',date_to),('employee_id.appoiontment_type','in',appoiontment_type),('company_id','in',states_ids_list)],)

        count = 0
        for payslip in payslips:
            if count == 0:
                for line in payslip.line_ids:
                    if line.name not in rules_list:
                        rules_list.append(line.name)
                    if line.salary_rule_id.id not in rules_ids_list:
                        rules_ids_list.append(line.salary_rule_id.id)
                count = 1
            else:
                break

                    
        docs = []
        index = 0
        for rule in rules_ids_list:
            state_rules = []
            total_row = 0.00
            for state in states_list:
                rule_total = 0.00
                for payslip in payslips:
                    for line in payslip.line_ids:
                        if payslip.employee_id.company_id.name == state and line.salary_rule_id.id == rule:
                            rule_total += line.total
                state_rules.append(rule_total)
                total_row += rule_total
            state_rules.append(total_row)
            docs.append({
                'rule':rules_list[index],
                'rules':state_rules,})
            index += 1


       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'states_list': states_list,
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
        }