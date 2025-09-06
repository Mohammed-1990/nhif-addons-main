from odoo import models,fields,api,_
import datetime
from datetime import date,datetime

from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
	

class leave_interrupt(models.Model):
	_name= "leave.interrupt"

	name = fields.Char(default="/")
	manager_id =  fields.Many2one('res.users', string='Requestor', default=lambda self: self.env.user,readonly=True)
	employee_id = fields.Many2one('hr.employee', required=True,track_visibility='onchange')
	employee_no=fields.Integer(track_visibility='onchange')
	leave_request_id = fields.Many2one('hr.leave','Leave Request',required=True)
	date_interrupt = fields.Date('Interruption Date', required=True)
	date_start = fields.Datetime(related='leave_request_id.date_from',readonly=True)
	date_end = fields.Datetime(related='leave_request_id.date_to', readonly=True)
	days = fields.Integer(string="The number of leave days", related='leave_request_id.number_of_days_display')
	restored_days = fields.Integer('Restored Days', compute='_get_restored_days', store=True)
	state = fields.Selection([
        ('draft', 'Draft'),
        ('direct_manger', 'Direct Manger'),
        ('dep_manger','Department Manger Confirm'),
        ('g_manger','General Manger Confirm'),
        ('hr_manger','HR Manger'),
        ('confirm', 'Confirm'),
        ],default='draft')

	@api.multi
	def action_direct_manger(self):
		self.write({'state':'direct_manger'})

	@api.multi
	def action_dep_manger(self):
		self.write({'state':'dep_manger'})


	@api.multi
	def action_g_manger(self):
		self.write({'state':'g_manger'})


	@api.multi
	def action_hr_manger(self):
		self.write({'state':'hr_manger'})


	@api.multi
	def action_confirm(self):
		if self.leave_request_id.holiday_status_id.save_remaining == 'yes':
			leave_allocation = self.env['hr.leave.allocation'].create({'employee_id':self.employee_id.id,
				'holiday_type':'employee',
				'number_of_days':self.restored_days,
				'number_of_days_display':self.restored_days})
			leave_allocation.action_approve()
			self.leave_request_id.sudo().write({'state':'end'})
		self.write({'state':'confirm'})

	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = False
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)],limit=1).id

	
	@api.depends('employee_id','date_interrupt','leave_request_id')
	def _get_restored_days(self):
		if self.date_interrupt and self.leave_request_id:
			if self.date_interrupt < self.leave_request_id.request_date_from or self.date_interrupt > self.leave_request_id.request_date_to:
				raise ValidationError(_("Sorry! Interruption Date Should be between The Start and End Dates."))
			# if self.leave_request_id.holiday_status_id.can_cut == 'no':
			# 	raise ValidationError(_("Sorry, Interruption is not allowed for this type of leaves!"))

			restored_days = (fields.Date.from_string(self.leave_request_id.request_date_to)-fields.Date.from_string(self.date_interrupt)).days

			self.restored_days = restored_days+1

			self.days = (fields.Date.from_string(self.date_interrupt)-fields.Date.from_string(self.leave_request_id.request_date_from)).days


	@api.onchange('employee_id')
	def get_request_id(self):
		if self.employee_id:
			self.employee_no = False
			self.employee_no = self.employee_id.number
		emp_leave = self.env['hr.leave'].search([('employee_id','=',self.employee_id.id),('state','=','validate')],limit=1)
		self.leave_request_id = False
		if emp_leave:
			if emp_leave.holiday_status_id.can_cut == 'no':
				raise ValidationError(_("The employee (%s) on a leave (%s) the  interruption is not allowed")%(self.employee_id.name,emp_leave.holiday_status_id.name))
			else:
				self.leave_request_id = emp_leave.id
		return { 'domain':{'leave_request_id':[('id','in',emp_leave.id)]}
		}
			



