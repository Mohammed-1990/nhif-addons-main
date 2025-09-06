# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class AlternativeAllowance(models.Model):
	_name="alternative.allowance"
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(default='/')
	
	emp_number = fields.Integer()
	employee_no = fields.Integer(default=False,track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee' , required=True,track_visibility='onchange')
	managment_id = fields.Many2one("hr.department",string="Managment",related='employee_id.unit_id')
	department_id = fields.Many2one("hr.department",related='employee_id.department_id')
	current_degree = fields.Many2one('functional.degree',related='employee_id.degree_id')

	date_from = fields.Date("Date From", required=True,)
	date_to = fields.Date("Date To", required=True,)
	alternative_degree = fields.Many2one("functional.degree",track_visibility="onchange", required=True,)
	state = fields.Selection([
		('draft','Draft'),
		('personnel','Personnel'),
		('sub_manager','Human Resources Sub-Manager'),
		('general_directorate','General Directorate of Human Resources'),
		('approved','Approved')], string="Status" ,default='draft',track_visibility="onchange" )
	notes = fields.Html()

	def do_submit(self):
		self.state = 'personnel'


	def do_personnel_confirm(self):
		self.state = 'sub_manager'
	
	def do_sm_confirm(self):
		self.state = 'general_directorate'
	
	def do_gd_confirm(self):
		self.employee_id.degree_id = self.alternative_degree
		self.state = 'approved'

	def do_return(self):
		if self.state == 'personnel':
			self.state = 'draft'
		if self.state == 'sub_manager':
			self.state = 'personnel'
		if self.state == 'general_directorate':
			self.state = 'sub_manager'

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
			self.current_degree = self.employee_id.degree_id
