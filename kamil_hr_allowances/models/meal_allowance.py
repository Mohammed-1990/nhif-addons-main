# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning


class MealAllowance(models.Model):
	_inherit = ['mail.thread','mail.activity.mixin']
	_name="meal.allowance"
	_order = 'id desc'
	
	name = fields.Char("Name", track_visibility="onchange")
	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)),)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),)
	eligible = fields.Selection([
        ('branchs', 'Branchs'),
        ('employees', 'Employees'),
        ('departments', 'Departments'),
        ('appointment_types', 'Appointment Type'),
    ],string='Eligible', track_visibility="onchange")
	company_ids = fields.Many2many('res.company', string='Branchs',track_visibility="onchange")
	employee_ids = fields.Many2many('hr.employee', string="Employees")
	department_ids = fields.Many2many('hr.department', string="Departments")
	appointment_type_ids = fields.Many2many('appointment.type', string="Appointment types")
	amount = fields.Float()
	deduction_amount = fields.Float()
	total_amount = fields.Float(compute='_compute_total_amount')
	stamp = fields.Many2one('account.tax')
	company_id = fields.Many2one('res.company',string='Branch',default=lambda self: self.env.user.company_id,readonly=True,)


	line_ids=fields.One2many("meal.allowance.line","line_id","Employees Allowances", copy=True)
	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits and wages'),
		('personnel','Personnel'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounting','Accounting')], string="Status" ,default='draft',track_visibility="onchange" )
	notes = fields.Html()

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise Warning(_('Cannot be deleted in a case other than draft'))
		return models.Model.unlink(self)

	@api.onchange('line_ids')
	def _compute_total_amount(self):
		for rec in self:
			total = 0.00
			for line in rec.line_ids:
				total += line.net
			rec.total_amount = total
	        
	
	def compute_allowance_line(self):
		if self.amount == 0:
			raise Warning(_("The amount cannot be zero"))
		domain = []
		if self.eligible == 'branchs':
			ids_list = []
			for company in self.company_ids:
				ids_list.append(company.id)
			domain.append(('company_id','in',ids_list))
		if self.eligible == 'employees':
			ids_list = []
			for employee in self.employee_ids:
				ids_list.append(employee.id)
			domain.append(('id','in',ids_list))
		if self.eligible == 'departments':
			ids_list = []
			for department in self.department_ids:
				ids_list.append(department.id)
			domain.append(('department_id','in',ids_list))
		if self.eligible == 'appointment_types':
			ids_list = []
			for appointment in self.appointment_type_ids:
				ids_list.append(appointment.id)
			domain.append(('appoiontment_type','in',ids_list))

		lines_list = []
		for employee in self.env['hr.employee'].search(domain):
			if employee.appoiontment_type.eligible != 'without_first_class':
				leaves = self.env['hr.leave'].search(['&',('employee_id','=',employee.id),'|','|','&',('request_date_from','<',self.date_from),('request_date_to','>',self.date_to),'&',('request_date_from','>=',self.date_from),('request_date_from','<=',self.date_to),'&',('request_date_to','>=',self.date_from),('request_date_to','<=',self.date_to)])
				
				days_leave = 0
				for leave in leaves:
					if leave.state == 'validate':
						if leave.request_date_from >= self.date_from and leave.request_date_to <= self.date_to:
							days_leave += leave.number_of_days_display
						elif leave.request_date_from < self.date_from:
							different_days = (fields.Date.from_string(self.date_from)-fields.Date.from_string(leave.request_date_from)).days
							days_leave += leave.number_of_days_display - different_days
						elif leave.request_date_to > self.date_to:
							different_days = (fields.Date.from_string(leave.request_date_to)-fields.Date.from_string(self.date_to)).days
							days_leave += leave.number_of_days_display - different_days
				stamp = self.stamp.amount
				if days_leave > 22:
					days_leave = 22 
					stamp = 0
				if days_leave != 22:
					lines_list.append({'employee_id':employee.id,
						'department_id':employee.department_id.id,
						'date_from':self.date_from,
						'date_to':self.date_to,
						'amount':self.amount,
						'stamp':stamp,
						'days_leave':days_leave,
						})

		self.line_ids = False
		self.line_ids = lines_list
		for line in self.line_ids:
			line.get_meal_allowance()

	def update_allowance_line(self):
		if self.amount == 0:
			raise Warning(_("The amount cannot be zero"))
		lines_list = []
		for line in self.line_ids:
			if line.employee_id.appoiontment_type.eligible != 'without_first_class':
				leaves = self.env['hr.leave'].search(['&',('employee_id','=',line.employee_id.id),'|','|','&',('request_date_from','<',self.date_from),('request_date_to','>',self.date_to),'&',('request_date_from','>=',self.date_from),('request_date_from','<=',self.date_to),'&',('request_date_to','>=',self.date_from),('request_date_to','<=',self.date_to)])

				days_leave = 0
				for leave in leaves:
					if leave.state == 'validate':
						if leave.request_date_from >= self.date_from and leave.request_date_to <= self.date_to:
							days_leave += leave.number_of_days_display
						elif leave.request_date_from < self.date_from:
							different_days = (fields.Date.from_string(self.date_from)-fields.Date.from_string(leave.request_date_from)).days
							days_leave += leave.number_of_days_display - different_days
						elif leave.request_date_to > self.date_to:
							different_days = (fields.Date.from_string(leave.request_date_to)-fields.Date.from_string(self.date_to)).days
							days_leave += leave.number_of_days_display - different_days
				stamp = self.stamp.amount
				if days_leave > 22:
					days_leave = 22 
					stamp = 0.00

				lines_list.append({'employee_id':line.employee_id.id,
					'department_id':line.employee_id.department_id.id,
					'date_from':self.date_from,
					'date_to':self.date_to,
					'amount':self.amount,
					'stamp':stamp,
					'days_leave':days_leave,
					})

		self.line_ids = False
		self.line_ids = lines_list
		for line in self.line_ids:
			line.get_meal_allowance()

	def do_submit(self):
		if not self.line_ids:
			raise Warning(_('Please enter allowance details'))
		# if self.total_amount == 0:
		# 	raise Warning(_('Total amount can not be zero'))
		for rec in self:
			for line in rec.line_ids:
				line.state = 'benefits_wages'
		self.state = 'benefits_wages'

	def do_confirm(self):
		for rec in self:
			for line in rec.line_ids:
				line.state = 'personnel'
		self.state = 'personnel'

	def do_personnel_confirm(self):
		for rec in self:
			for line in rec.line_ids:
				line.state = 'general_directorate'
		self.state = 'general_directorate'

	def do_gd_confirm(self):
		# general directorate confirm
		for rec in self:
			for line in rec.line_ids:
				line.state = 'internal_auditor'
		self.state = 'internal_auditor'

	def do_ia_confirm(self):
		# internal auditor confirm
		#Delete the old rati list
		for rati in self.env['ratification.list'].search([('meal_allowance_id','=',self.id)]):
			rati.write({'state':'canceled'})
			rati.sudo().unlink()

		ratification_line = []
		ratification = self.env['ratification.list'].create({'name':'مُسير ('+self.name+')',
			'date':date.today(),
			'from_hr':True,
			'meal_allowance_id':self.id,
			})
		account_config = self.env['hr.account.config'].search([],limit=1)
		meal_account = account_config.meal_allowance
		meal_leave_deduction = account_config.meal_leave_deduction
		meal_allowance_honesty = account_config.meal_allowance_honesty
		deduction_amount = account_config.deduction_amount
		for line in self.line_ids:
			deduction_list = []
			if self.stamp and line.stamp != 0:
				deduction_list.append({'tax_id':self.stamp,'name':self.stamp.name,'amount':line.stamp})
			if meal_leave_deduction and line.discount != 0:
				deduction_list.append({'tax_id':meal_leave_deduction,'name':meal_leave_deduction.name,'amount':line.discount})
			if meal_allowance_honesty and line.receivable != 0:
				deduction_list.append({'tax_id':meal_allowance_honesty,'name':meal_allowance_honesty.name,'amount':line.total})
			if not meal_allowance_honesty and deduction_amount and line.deductions != 0:
				deduction_list.append({'tax_id':deduction_amount,'name':deduction_amount.name,'amount':line.deductions})
			#ratification line
			if line.net != 0:
				ratification_line.append({
					'name':self.name,
					'partner_id':line.employee_id.partner_id.id,
					'branch_id':line.employee_id.company_id.id,
					'amount':line.amount,
					'account_id':meal_account.id,
					'analytic_account_id':meal_account.parent_budget_item_id.id,
					'deduction_ids':deduction_list,
					'ratification_list_id':ratification.id,})
		ratification.ratification_line_ids = ratification_line
		for rec in self:
			for line in rec.line_ids:
				line.state = 'accounting'
		self.state = 'accounting'

	def do_return(self):
		if self.state == 'benefits_wages':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'draft'
			self.state = 'draft'
		if self.state == 'personnel':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'benefits_wages'
			self.state = 'benefits_wages'
		if self.state == 'general_directorate':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'personnel'
			self.state = 'personnel'
		if self.state == 'internal_auditor':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'general_directorate'
			self.state = 'general_directorate'

	def do_return1(self):
		if self.state == 'benefits_wages':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'draft'
			self.state = 'draft'
		if self.state == 'personnel':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'benefits_wages'
			self.state = 'benefits_wages'
		if self.state == 'general_directorate':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'personnel'
			self.state = 'personnel'
		if self.state == 'internal_auditor':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'general_directorate'
			self.state = 'general_directorate'

	def do_return2(self):
		if self.state == 'benefits_wages':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'draft'
			self.state = 'draft'
		if self.state == 'personnel':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'benefits_wages'
			self.state = 'benefits_wages'
		if self.state == 'general_directorate':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'personnel'
			self.state = 'personnel'
		if self.state == 'internal_auditor':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'general_directorate'
			self.state = 'general_directorate'

	def do_return3(self):
		if self.state == 'benefits_wages':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'draft'
			self.state = 'draft'
		if self.state == 'personnel':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'benefits_wages'
			self.state = 'benefits_wages'
		if self.state == 'general_directorate':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'personnel'
			self.state = 'personnel'
		if self.state == 'internal_auditor':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'general_directorate'
			self.state = 'general_directorate'


class MealAllowanceLine(models.Model):
	_name="meal.allowance.line"
	_rec_name = 'employee_id'
	
	employee_id = fields.Many2one("hr.employee",)
	employee_no = fields.Integer(related='employee_id.number' )
	department_id = fields.Many2one("hr.department", )
	date_from = fields.Date()
	date_to = fields.Date()
	amount = fields.Float(string="Allowance amount",)
	days_leave = fields.Integer()
	discount = fields.Integer(String="Leave Discount",)
	receivable = fields.Integer("Receivable",)
	deductions = fields.Integer("Deduction Amount")
	stamp = fields.Float()
	total_deductions = fields.Float()
	total = fields.Float()
	net = fields.Float("Net",)
	account_number = fields.Char("Account Number",related='employee_id.account_number', )
	line_id = fields.Many2one("meal.allowance",ondelete='cascade')
	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits and wages'),
		('personnel','Personnel'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounting','Accounting')], string="Status" ,default='draft',track_visibility="onchange" )



	@api.onchange('employee_id','amount','days_leave','discount','stamp','deductions',)
	def get_meal_allowance(self):
		if self.employee_id:
			self.department_id = self.employee_id.department_id.id
			self.discount = (self.amount/22) *self.days_leave
			self.receivable = self.amount - self.discount
			self.deductions = self.line_id.deduction_amount
			if self.days_leave >= 22:
				self.stamp = 0
				self.net = 0
				self.total_deductions = 0
			elif self.receivable - self.stamp - self.deductions > 0:
				self.total_deductions = self.discount + self.stamp + self.deductions
				meal_allowance_honesty = self.env['hr.account.config'].search([],limit=1).meal_allowance_honesty
				if meal_allowance_honesty:
					self.net = 0.00
					self.total = self.amount - self.total_deductions
				else: 
					self.net = self.amount - self.total_deductions
					self.total = self.amount - self.total_deductions

