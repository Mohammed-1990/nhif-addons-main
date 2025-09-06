# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning
import datetime
import time
import math
from datetime import datetime, date, time , timedelta
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

class leavesRequest(models.Model):
    _inherit = "hr.leave"

    number_of_days = fields.Float(
    'Duration (Days)', copy=False, readonly=True,  default="1", track_visibility=False)
    number_of_days_display = fields.Integer(
    'Duration in days', copy=False, readonly=True,track_visibility='onchange',
    default="1")
    date_from = fields.Datetime('Start Date', track_visibility=False)
    date_to = fields.Datetime( 'End Date', track_visibility=False)
    request_date_from = fields.Date('Request Start Date', track_visibility='onchange')
    request_date_to = fields.Date('Request End Date', track_visibility='onchange')
    date_direct_action = fields.Date(track_visibility='onchange')
    address = fields.Char(track_visibility='onchange', string="The employee's leave address")
    employee_id = fields.Many2one('hr.employee', required=True,track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='Requestor', related='employee_id.user_id', related_sudo=True, compute_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)
    employee_no=fields.Integer(track_visibility='onchange')
    who_acting = fields.Many2one("hr.employee", string="Who is acting",track_visibility='onchange')
    reason= fields.Text("Reason",track_visibility='onchange')
    document_ids = fields.One2many('leaves.document','line_id', )
    can_acting = fields.Selection([('yes','Yes'),('no','No')],"Can Acting",related='holiday_status_id.can_acting')
    duration_display = fields.Char('Requested (Days/Hours)',)
    

    state = fields.Selection([
        ('draft', 'Draft'),
        ('acting','The approval of a designee'),
        ('dep_manger','Department Manger Confirm'),
        ('confirm', 'Unit Manger Confirm'),
        ('hr_manger','HR Manger'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('end','Interrupted'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',)

    @api.onchange('who_acting')
    def _onchange_who_acting(self):
        if self.who_acting and self.employee_id:
            if self.who_acting == self.employee_id:
                self.who_acting = False
            
    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.allocation_type == 'no':
                continue
            leave_days = holiday.holiday_status_id.get_days(holiday.employee_id.id)[holiday.holiday_status_id.id]
            if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
              float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                        ))

    def leave_deadline_check(self):
        for rec in self.env['hr.leave'].search([]):
            if rec.request_date_to:
                if rec.request_date_to < date.today():
                    rec.state = 'end'



    @api.onchange('holiday_status_id','request_date_from','request_date_to')
    def _onchange_leave_document(self):
        if self.holiday_status_id:
            if self.holiday_status_id.unpaid == True:
                different_date =fields.Date.from_string(self.request_date_from)+relativedelta(months=+self.holiday_status_id.request_duration)
                if different_date < self.request_date_to:
                    raise ValidationError(_("Sorry!,you can not request for more paid leave than permitted years"))
            if self.holiday_status_id.can_saved == 'yes':  
                allocated_year = self.env['hr.leave.allocation'].search([('holiday_status_id','=',self.holiday_status_id.id),('start_date','>=',self.request_date_from),('end_date','<=',self.request_date_to)], limit=1)
                if allocated_year.end_date:
                    allocation_end_date =(datetime.strptime(str(allocated_year.end_date), "%Y-%m-%d") + relativedelta(months=self.holiday_status_id.duration)).date()
                    end_year_request  = (fields.Date.from_string(self.request_date_to))
                    if end_year_request > allocation_end_date:
                        raise ValidationError(_("You can not request this type leave,becaudr the entitlement for days fell"))

            if self.holiday_status_id.documents == True:
                lines = []
                for doc in self.holiday_status_id.document:
                    lines.append({'document_id':doc.id})
                self.document_ids = False
                self.document_ids = lines


    @api.onchange('employee_no')
    def _onchange_employee_no(self):
        if self.employee_no:
            self.employee_id = False
            self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)],limit=1).id

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.employee_no = False
            self.employee_no = self.employee_id.number
            self.department_id = self.employee_id.department_id

    def set_to_draft(self):
        self.state = 'draft'

    def return1(self):
        self.state = 'draft'

    def do_send(self):
        self._check_holidays()
        for line in self.document_ids:
            if not line.attach:
                raise Warning(_('Please attach all required documents'))
        if self.holiday_status_id.can_acting == 'yes':
            self.write({'state':'acting'})
        else:
            self.write({'state': 'dep_manger'})
            self.state = 'dep_manger'

    @api.multi
    def action_acting(self):
        self.write({'state':'dep_manger'})
    
    @api.multi
    def action_return1(self):
        self.write({'state':'draft'})

    @api.multi
    def action_return2(self):
        self.write({'state':'dep_manger'})

    @api.multi
    def action_return3(self):
        self.write({'state':'confirm'})
        
    @api.multi
    def dep_manger_confirm(self):
        self.write({'state':'confirm'})

    @api.multi
    def hr_manger(self):
        self.write({'state':'hr_manger'})

    
    @api.multi
    def action_validate(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # if any(holiday.state not in ['confirm', 'hr_manger'] for holiday in self):
        #     raise UserError(_('Leave request must be confirmed in order to approve it.'))


        self.write({'state': 'validate'})
        #notify employee
        if self.employee_id.user_id and self.state == 'validate' and self.employee_id.user_id.email:
            self.env['mail.activity'].create({
                'res_name': self.holiday_status_id.name,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'date_deadline':date.today(),
                'summary': self.holiday_status_id.name,
                'user_id': self.employee_id.user_id.id,
                'res_id': self.id,
                'res_model_id': self.env.ref('hr_holidays.model_hr_leave').id,
            })
        self.filtered(lambda holiday: holiday.validation_type == 'both').write({'second_approver_id': current_employee.id})
        self.filtered(lambda holiday: holiday.validation_type != 'both').write({'first_approver_id': current_employee.id})

        for holiday in self.filtered(lambda holiday: holiday.holiday_type != 'employee'):
            if holiday.holiday_type == 'category':
                employees = holiday.category_id.employee_ids
            elif holiday.holiday_type == 'company':
                employees = self.env['hr.employee'].search([('company_id', '=', holiday.mode_company_id.id)])
            else:
                employees = holiday.department_id.member_ids

            if self.env['hr.leave'].search_count([('date_from', '<=', holiday.date_to), ('date_to', '>', holiday.date_from),
                               ('state', 'not in', ['cancel', 'refuse']), ('holiday_type', '=', 'employee'),
                               ('employee_id', 'in', employees.ids)]):
                raise ValidationError(_('You can not have 2 leaves that overlaps on the same day.'))

            values = [holiday._prepare_holiday_values(employee) for employee in employees]
            leaves = self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True,
            ).create(values)
            leaves.action_approve()
            # FIXME RLi: This does not make sense, only the parent should be in validation_type both
            if leaves and leaves[0].validation_type == 'both':
                leaves.action_validate()

        employee_requests = self.filtered(lambda hol: hol.holiday_type == 'employee')
        employee_requests._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            employee_requests.activity_update()
        return True

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):
        #Over write this method 
        return True

    def _check_approval_update(self, state):
        #Over write this method 
        return True

    @api.multi
    def _create_resource_leave(self):
        #Over write this method 
        return True

    def _validate_leave_request(self):
        #Over write this method 
        return True



    @api.onchange('number_of_days_display','request_date_from','request_date_to')
    def _onchange_number_of_days(self):
        if self.number_of_days_display and self.request_date_from:
            self.number_of_days = self.number_of_days_display
            self.request_date_to = (datetime.strptime(str(self.request_date_from), "%Y-%m-%d") + relativedelta(days=self.number_of_days_display-1)).date()
            self.duration_display =  self.number_of_days_display  

    @api.onchange('request_date_to')
    def _number_of_days(self):
        if self.request_date_from and self.request_date_to:
            self.number_of_days = (datetime.strptime(str(self.request_date_to), '%Y-%m-%d') - datetime.strptime(str(self.request_date_from), '%Y-%m-%d')).days + 1
            self.number_of_days_display = self.number_of_days
            self.duration_display =  self.number_of_days_display   
   

class LeaveDocument(models.Model):
    _name = 'leaves.document'
    
    document_id = fields.Many2one('document.document',string='Name')
    attach = fields.Binary()

    line_id = fields.Many2one('hr.leave',)
    