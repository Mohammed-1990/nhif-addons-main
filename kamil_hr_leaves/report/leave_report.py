from odoo import models,fields,api
import time
import datetime

class ReportLeave(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_leaves.leave_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        domain = []
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        employee_id = data['form']['employee_id']
        if employee_id:
            domain.append(('employee_id','=',employee_id))
        department_id = data['form']['department_id']
        if department_id:
            domain.append(('department_id','=',department_id))
        leave_id = data['form']['leave_id']
        if leave_id:
            domain.append(('holiday_status_id','=',leave_id))


        # leaves = self.env['hr.leave'].search(['|','&',('request_date_from','>=',date_from),('request_date_from','<=',date_to),'&',('request_date_to','>=',date_from),('request_date_to','<=',date_to)])

        leaves = self.env['hr.leave'].search(['|','|','&',('request_date_from','<',date_from),('request_date_to','>',date_to),'&',('request_date_from','>=',date_from),('request_date_from','<=',date_to),'&',('request_date_to','>=',date_from),('request_date_to','<=',date_to)])
        employee_list = []
        for leave in leaves:
            if employee_id:
                if leave.employee_id.id == employee_id and leave.employee_id not in employee_list:
                    employee_list.append(leave.employee_id)
            else:
                if leave.employee_id not in employee_list:
                    employee_list.append(leave.employee_id)

        docs = []
        for employee in employee_list:
            for leave in leaves:
                print(leave.employee_id.name)
                days_leave = 0
                if leave.state == 'validate':
                    if str(leave.request_date_from) >= date_from and str(leave.request_date_to) <= date_to:
                        days_leave = str(leave.number_of_days_display)
                    elif str(leave.request_date_from) < date_from:
                        different_days = (fields.Date.from_string(date_from)-fields.Date.from_string(leave.request_date_from)).days
                        days_leave = leave.number_of_days_display - different_days
                    elif str(leave.request_date_to) > date_to:
                        different_days = (fields.Date.from_string(leave.request_date_to)-fields.Date.from_string(date_to)).days
                        days_leave = leave.number_of_days_display - different_days
                    month_days_number = days_leave
                    if int(days_leave) >= 20:
                        month_days_number = 22 

                    if leave_id and department_id:
                        if leave.holiday_status_id.id == leave_id and leave.employee_id.department_id.id == department_id and leave.employee_id == employee:
                            docs.append({
                                'employee':leave.employee_id.name,
                                'department':leave.employee_id.department_id.name,
                                'leave':leave.holiday_status_id.name,
                                'days_number':leave.number_of_days_display,
                                'month_days_number':month_days_number,
                                'date_from':leave.request_date_from,
                                'date_to':leave.request_date_to
                                })
                    elif leave_id and not department_id:
                        if leave.holiday_status_id.id == leave_id and leave.employee_id == employee:
                            docs.append({
                                'employee':leave.employee_id.name,
                                'department':leave.employee_id.department_id.name,
                                'leave':leave.holiday_status_id.name,
                                'days_number':leave.number_of_days_display,
                                'month_days_number':month_days_number,
                                'date_from':leave.request_date_from,
                                'date_to':leave.request_date_to
                                })
                    elif not leave_id and department_id:
                        if leave.employee_id.department_id.id == department_id and leave.employee_id == employee:
                            docs.append({
                                'employee':leave.employee_id.name,
                                'department':leave.employee_id.department_id.name,
                                'leave':leave.holiday_status_id.name,
                                'days_number':leave.number_of_days_display,
                                'month_days_number':month_days_number,
                                'date_from':leave.request_date_from,
                                'date_to':leave.request_date_to
                                })
                    else:
                        if leave.employee_id == employee:
                            docs.append({
                                'employee':leave.employee_id.name,
                                'department':leave.employee_id.department_id.name,
                                'leave':leave.holiday_status_id.name,
                                'days_number':leave.number_of_days_display,
                                'month_days_number':month_days_number,
                                'date_from':leave.request_date_from,
                                'date_to':leave.request_date_to
                                })
                    

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
        }