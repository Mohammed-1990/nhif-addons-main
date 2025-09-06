# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
import datetime
from datetime import date,datetime

from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.exceptions import Warning


class ReasonTerminationService(models.Model):
	_name="reason.termination.service"

	name = fields.Char("Termination Reason",required=True)
	depend_age = fields.Boolean("Depend on age")
	resignation = fields.Boolean("Is Resignation?")
	age = fields.Integer("Age")

class TerminationService(models.Model):
	_name="termination.service"
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = "employee_id"

	date = fields.Date(required=True)
	employee_id = fields.Many2one("hr.employee",string="Employee",required=True,track_visibility="onchange")
	employee_no = fields.Integer("Employee Number")
	unit_id = fields.Many2one("hr.department",)
	department_id = fields.Many2one("hr.department",)
	appoiontment_type=fields.Many2one('appointment.type',track_visibility="onchange",)
	years_service = fields.Integer("Years of service")
	termination_id = fields.Many2one("reason.termination.service", domain=[('resignation','=',False), ],track_visibility="onchange" )
	reason_refuse = fields.Html("the reason of refuse")
	attach = fields.Binary(string ="Attahcment",)
	state = fields.Selection([
		('draft', 'Draft'),
		('gm_confirm','GM Confirm'), 
		('hr_confirm', 'HR Confirm'),
		('hr_g_confirm', 'HR G Confirm'),
		('hr_user_confirm','HR User Confirm'),
		('confirmed','Confirmed'),
		('rejected','Rejected')],"States", 
		default="draft",track_visibility="onchange")

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise Warning(_('Cannot be deleted in a case other than draft'))
		return models.Model.unlink(self)

	
	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = False
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)],limit=1).id



	@api.multi
	def do_confirm(self):
		self.state = 'gm_confirm'

	@api.multi
	def do_hr_confirm(self):
		self.state = 'hr_confirm'

	@api.multi
	def do_hr_g_confirm(self):
		self.state = 'hr_g_confirm'

	@api.multi
	def hr_user_confirm(self):
		self.state = 'hr_user_confirm'

	@api.multi
	def do_confirm2(self):
		self.employee_id.toggle_active()
		self.employee_id.user_id.active = False
		self.state = 'confirmed'

	@api.multi
	def action_reject(self):
		if not self.env["ir.fields.converter"].text_from_html(self.reason_refuse, 40, 1000, "..."):
			raise Warning(_('Please Enter reason'))
		self.state = 'rejected'

	@api.multi
	def action_reject1(self):
		if not self.env["ir.fields.converter"].text_from_html(self.reason_refuse, 40, 1000, "..."):
			raise Warning(_('Please Enter reason'))
		self.state = 'rejected'

	@api.multi
	def action_reject2(self):
		if not self.env["ir.fields.converter"].text_from_html(self.reason_refuse, 40, 1000, "..."):
			raise Warning(_('Please Enter reason'))
		self.state = 'rejected'

	@api.multi
	def action_reject3(self):
		if not self.env["ir.fields.converter"].text_from_html(self.reason_refuse, 40, 1000, "..."):
			raise Warning(_('Please Enter reason'))
		self.state = 'rejected'





	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.employee_no = self.employee_id.number
			self.emp_dep = self.employee_id.department_id
			self.appoiontment_type = self.employee_id.appoiontment_type
			self.unit_id = self.employee_id.unit_id
			self.department_id = self.employee_id.department_id
			

class ResignationResignation(models.Model):
	_name="resignation.resignation"
	_inherit = ['mail.thread','mail.activity.mixin']

	_rec_name = "employee_id"

	last_day_date = fields.Date(required=True)
	employee_id = fields.Many2one("hr.employee",string="Employee",required=True,track_visibility="onchange")
	employee_no = fields.Integer("Employee Number",track_visibility="onchange")
	unit_id = fields.Many2one("hr.department",)
	department_id = fields.Many2one("hr.department",related='employee_id.department_id')
	request_date  = fields.Date(default=lambda self: fields.Date.today(),readonly=True, )
	
	years_service = fields.Integer("Years of service")
	termination_id = fields.Many2one("reason.termination.service", domain=[('resignation','=',True), ],track_visibility="onchange")
	reason_refuse = fields.Html("the reason of refuse",track_visibility="onchange")
	state = fields.Selection([('draft', 'Draft'),('manger_confirm','Direct Manager'),('general_manager_confirm','General Manager'),('human_resource_confirm','Human Resource'),('hr2_user_confirm','HR User'),('rejected','Rejected'),('rejected1','Rejected1'),('rejected2','Rejected2')],"States", default="draft",track_visibility="onchange")

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

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise Warning(_('Cannot be deleted in a case other than draft'))
		return models.Model.unlink(self)
	
	@api.multi
	def manger_confirm(self):
		self.write({'state':'manger_confirm'})

	@api.multi
	def general_manager_confirm(self):
		self.write({'state':'general_manager_confirm'})

	@api.multi
	def human_resource_confirm(self):
		self.write({'state':'human_resource_confirm'})

	@api.multi
	def hr2_user_confirm(self):
		self.employee_id.toggle_active()
		self.employee_id.user_id.toggle_active()
		self.write({'state':'hr2_user_confirm'})

	@api.multi
	def action_reject(self):
		if not self.env["ir.fields.converter"].text_from_html(self.reason_refuse, 40, 1000, "..."):
			raise Warning(_('Please Enter reason'))
		self.state = 'rejected'

	@api.multi
	def action_reject1(self):
		if not self.env["ir.fields.converter"].text_from_html(self.reason_refuse, 40, 1000, "..."):
			raise Warning(_('Please Enter reason'))
		self.state = 'rejected1'

	@api.multi
	def action_reject2(self):
		if not self.env["ir.fields.converter"].text_from_html(self.reason_refuse, 40, 1000, "..."):
			raise Warning(_('Please Enter reason'))
		self.state = 'rejected2'


	# @api.depends('request_date','last_day_date')
	# @api.multi
	# def _get_date(self):
	# 	if self.request_date and self.last_day_date:
	# 		if self.last_day_date < self.request_date + 14:
	# 			raise ValidationError(_("Sorry! "))
	
	# 	return True
	# @api.onchange('last_day_date','request_date')
	# @api.multi
	# def _onchange_last_day_date(self):
	# 	if self.request_date and self.last_day_date:
	# 		if self.last_day_date < self.request_date + 14:
	# 			raise ValidationError(_("Sorry! "))
