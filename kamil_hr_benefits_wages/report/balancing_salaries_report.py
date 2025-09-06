from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar


class ReportBalancingSalaries(models.AbstractModel):
    
    _name = 'report.kamil_hr_benefits_wages.balancing_salaries_view'





    @api.model
    def _get_report_values(self, docids, data=None):

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        employee_ids = data['form']['employee_ids']
        branch_id = data['form']['branch_id']
        struct_ids = data['form']['struct_ids']

        first_date = datetime.strptime(date_from, '%Y-%m-%d').strftime('%m')
        second_date = datetime.strptime(date_to, '%Y-%m-%d').strftime('%m')


        if str(first_date) == '01':
            first_date = 'يناير'
        if str(second_date) == '01':
            second_date = 'يناير'
        if str(first_date) == '02':
            first_date = 'فبراير'
        if str(second_date) == '02':
            second_date = 'فبراير'
        if str(first_date) == '03':
            first_date = 'مارس'
        if str(second_date) == '03':
            second_date = 'مارس'
        if str(first_date) == '04':
            first_date = 'ابريل'
        if str(second_date) == '04':
            second_date = 'ابريل'
        if str(first_date) == '05':
            first_date = 'مايو'
        if str(second_date) == '05':
            second_date = 'مايو'
        if str(first_date) == '06':
            first_date = 'يونيو'
        if str(second_date) == '06':
            second_date = 'يونيو'
        if str(first_date) == '07':
            first_date = 'يوليو'
        if str(second_date) == '07':
            second_date = 'يوليو'
        if str(first_date) == '08':
            first_date = 'أغسطس'
        if str(second_date) == '08':
            second_date = 'أغسطس'
        if str(first_date) == '09':
            first_date = 'سبتمبر'
        if str(second_date) == '09':
            second_date = 'سبتمبر'
        if str(first_date) == '10':
            first_date = 'أكتوبر'
        if str(second_date) == '10':
            second_date = 'أكتوبر'
        if str(first_date) == '11':
            first_date = 'نوفمبر'
        if str(second_date) == '11':
            second_date = 'نوفمبر'
        if str(first_date) == '12':
            first_date = 'ديسمبر'
        if str(second_date) == '12':
            second_date = 'ديسمبر'





        first_domain = []
        second_domain = []

        if employee_ids:
            first_domain.append(('employee_id','in',employee_ids))
            second_domain.append(('employee_id','in',employee_ids))
        if struct_ids:
            first_domain.append(('struct_id','in',struct_ids))
            second_domain.append(('struct_id','in',struct_ids))
        if branch_id:
            first_domain.append(('payslip_run_id.branch_id','=',branch_id))
            second_domain.append(('payslip_run_id.branch_id','=',branch_id))



        first_domain.append(('date_from','<=',date_from))
        first_domain.append(('date_to','>=',date_from))

        second_domain.append(('date_from','<=',date_to))
        second_domain.append(('date_to','>=',date_to))
               
        first_payslips = self.env['hr.payslip'].sudo().search(first_domain)
        second_payslips = self.env['hr.payslip'].sudo().search(second_domain)

        employees_list = []


        rule_names = []
        for payslip in first_payslips:
            if payslip.struct_id:
                for line in payslip.struct_id.rule_ids:
                    if line.code not in ['اجمالى بدلات','اجمالى استقطاعات', 'صافي المرتب', 'الاجمالى','الاساسى'] : 
                        rule_names.append( line.code )
                break;


        for payslip in first_payslips:
            if payslip.employee_id not in employees_list:
                employees_list.append(payslip.employee_id)

        for payslip in second_payslips:
            if payslip.employee_id not in employees_list:
                employees_list.append(payslip.employee_id)
            

        docs = []
        for employee in employees_list:
            
            first_total = 0.00
            second_total =0.00

            notes = ''
            addition = 0
            minues = 0

            is_in_leave = False
            is_internal_transfer = False
            is_final_transfer = False
            is_termination_service = False
            is_resignation = False

            leave_name = ''
            termination_service_reason = ''

            first_rule_lines = {}
            second_rule_lines = {}

            for payslip in first_payslips:
                if payslip.employee_id == employee:


                    for internal_transfer in self.env['internal.transfer'].sudo().search([('employee_id','=',employee.id),('date','>=',payslip.date_from),('date','<=',payslip.date_to)]):
                        is_internal_transfer = True

                    for final_transfer in self.env['final.transfer'].sudo().search([('name','=',payslip.employee_id.name),('date','>=',payslip.date_from),('date','<=',payslip.date_to)]):
                        is_final_transfer = True

                    for termination in self.env['termination.service'].sudo().search([('employee_id','=',employee.id),('date','>=',payslip.date_from),('date','<=',payslip.date_to)]):
                        termination_service_reason = 'إنهاء خدمة _ ' + termination.termination_id.name 
                        is_termination_service = True

                    for termination in self.env['resignation.resignation'].sudo().search([('employee_id','=',employee.id),('last_day_date','>=',payslip.date_from),('last_day_date','<=',payslip.date_to)]):
                        termination_service_reason = 'إنهاء خدمة _ ' + termination.termination_id.name 
                        is_resignation = True


                    for line in payslip.line_ids:
                        if line.code == 'صافي المرتب':
                            first_total = line.total

                        first_rule_lines[ line.salary_rule_id.code ] = abs(line.total)

                    for line in payslip.worked_days_line_ids :
                        if line.code == 'غير مدفوعه' or line.code == 'غير مدفوعة' or line.code == 'ايقاف راتب':
                            is_in_leave = True
                            notes = ' - إجازة غير مدفوعة - '
                            leave_name = 'إجازة غير مدفوعة'

                        if line.code == 'امومة بدون مرتب':
                            is_in_leave = True
                            notes = ' - إجازة امومة بدون مرتب - '
                            leave_name = 'إجازة امومة بدون مرتب'
                        if line.code == 'ايقاف راتب':
                            is_in_leave = True
                            notes = ' - ايقاف راتب - '
                            leave_name = 'ايقاف راتب'

            for payslip in second_payslips:
                if payslip.employee_id == employee:
                    for internal_transfer in self.env['internal.transfer'].sudo().search([('employee_id','=',employee.id),('date','>=',payslip.date_from),('date','<=',payslip.date_to)]):
                        is_internal_transfer = True


                    for final_transfer in self.env['final.transfer'].sudo().search([('name','=',payslip.employee_id.name),('date','>=',payslip.date_from),('date','<=',payslip.date_to)]):
                        is_final_transfer = True


                    for termination in self.env['termination.service'].sudo().search([('employee_id','=',employee.id),('date','>=',payslip.date_from),('date','<=',payslip.date_to)]):
                        termination_service_reason = 'إنهاء خدمة _ ' + termination.termination_id.name 
                        is_termination_service = True

                    for termination in self.env['resignation.resignation'].sudo().search([('employee_id','=',employee.id),('last_day_date','>=',payslip.date_from),('last_day_date','<=',payslip.date_to)]):
                        termination_service_reason = 'إنهاء خدمة _ ' + termination.termination_id.name 
                        is_resignation = True


                    for line in payslip.line_ids:

                        if line.code == 'صافي المرتب':
                            second_total = line.total

                        second_rule_lines[ line.salary_rule_id.code ] = abs(line.total)                        

                    for line in payslip.worked_days_line_ids :
                        if line.code == 'غير مدفوعه' or line.code == 'غير مدفوعة' or line.code == 'امومة':
                            is_in_leave = True
                            notes =  ' - إجازة غير مدفوعة - '
                            leave_name = 'إجازة غير مدفوعة'

                        if line.code == 'امومة بدون مرتب':
                            is_in_leave = True
                            notes =  ' - إجازة امومة بدون مرتب - '
                            leave_name = 'إجازة امومة بدون مرتب'

                        if line.code == 'ايقاف راتب':
                            is_in_leave = True
                            notes = ' - ايقاف راتب - '
                            leave_name = 'ايقاف راتب'
                        if line.code == 'امومة':
                            is_in_leave = True
                            notes = ' - امومة باجر اساسي - '
                            leave_name = 'امومة باجر اساسي'

            addition = minues = 0
            for rule_name in rule_names:
                                    
                    if abs(float( first_rule_lines.get(rule_name ,0)) ) != abs(float(second_rule_lines.get(rule_name ,0)) ):

                        if rule_name == 'LOAN':
                            notes = notes +  ' - سلفية - '
                        else:
                            notes = notes +  ' - ' + rule_name + ' - '

                        if abs(float(second_rule_lines.get(rule_name,0)) ) > abs(float(first_rule_lines.get(rule_name, 0)) ):
                            addition = addition + ( abs(float(second_rule_lines.get(rule_name,0)) ) - abs(float(first_rule_lines.get(rule_name ,0) )) )
                        if abs(float(first_rule_lines.get(rule_name ,0) ))> abs(float(second_rule_lines.get(rule_name , 0))):
                            minues = minues + (abs(float(first_rule_lines.get(rule_name,0)) ) - abs(float(second_rule_lines.get(rule_name,0 )) ) ) 
            if is_in_leave:
                notes = leave_name
                if first_total > second_total:
                    minues = first_total
                if second_total > first_total:
                    addition = second_total
            
            if second_total == 0:
                sec_month = datetime.strptime(date_to, '%Y-%m-%d').date()
                start_of_second = datetime.strptime(str(1)+str(sec_month.month)+str(sec_month.year), '%d%m%Y').date()
                end_of_seecond = datetime.strptime(str(calendar.monthrange(sec_month.year,sec_month.month)[1])+str(sec_month.month)+str(sec_month.year), '%d%m%Y').date()
                for internal_transfer in self.env['internal.transfer'].sudo().search([('employee_id','=',employee.id),('date','>=',start_of_second),('date','<=',end_of_seecond)]):
                        is_internal_transfer = True
            if is_internal_transfer:
                notes = 'نقل داخلي'
                if first_total > second_total:
                    minues = first_total
                if second_total > first_total:
                    addition = second_total
            
            if is_final_transfer:
                notes = 'نقل نهائي'
                if first_total > second_total:
                    minues = first_total
                if second_total > first_total:
                    addition = second_total

            if is_termination_service or is_resignation:
                notes = termination_service_reason
                if first_total > second_total:
                    minues = first_total
                if second_total > first_total:
                    addition = second_total



            difference =  second_total - first_total
            
            addition = minues = 0

            if difference > 0:
                addition = difference
            elif difference < 0:
                minues = difference * -1


            docs.append({'number': employee.number,
                'employee': employee.name,
                'first_month': first_total,
                'second_month': second_total,
                'increase': addition,
                'decrease': minues,
                'notes': notes,})
       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'first_date' : first_date,
            'second_date' : second_date,
            'branch_id':self.env['res.company'].search([('id','=',branch_id)]).name
        }

