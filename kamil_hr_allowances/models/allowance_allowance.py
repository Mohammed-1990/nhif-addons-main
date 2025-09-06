# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning


class allowanceAllowance(models.Model):
	_inherit = ['mail.thread','mail.activity.mixin']
	_name="allowance.allowance"
	_order = 'id desc'
	
	name = fields.Char(required=True, track_visibility="onchange")
	company_id = fields.Many2one('res.company',string='Branch',default=lambda self: self.env.user.company_id,readonly=True,)
	date = fields.Date(default=lambda self: fields.Date.today(), required=True, track_visibility="onchange")
	config_id = fields.Many2one('allowance.allowance.config', string='Allowance', required=True, track_visibility="onchange", domain=[ ('is_active','=',True)])
	eligible = fields.Selection([
        ('branchs', 'Branchs'),
        ('employees', 'Employees'),
        ('departments', 'Departments'),
        ('appointment_types', 'Appointment Type'),
        ('degree', 'Degree'),
    ],string='Eligible', required=True, track_visibility="onchange")
	company_ids = fields.Many2many('res.company', string='Branchs', track_visibility="onchange")
	branch_id = fields.Many2one('res.company', string='Branch', track_visibility="onchange")
	employee_ids = fields.Many2many('hr.employee', string="Employees")
	department_ids = fields.Many2many('hr.department', string="Departments")
	appointment_type_ids = fields.Many2many('appointment.type', string="Appointment types")
	degree_ids = fields.Many2many('functional.degree', string='Degrees', track_visibility="onchange")
	total_amount = fields.Float(compute='_compute_total_amount')
	stamp = fields.Many2one('account.tax')


	line_ids=fields.One2many("allowance.allowance.line","allowance_allowance_id","Employees Allowances", copy=True)
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

	@api.onchange('branch_id')
	def onchange_branch_id(self):
		if self.branch_id:
			self.company_id = self.branch_id.id

	@api.onchange('line_ids')
	def _compute_total_amount(self):
		for rec in self:
			total = 0.00
			for line in rec.line_ids:
				total += line.net
			rec.total_amount = total

	@api.onchange('config_id')
	def _onchange_config_id(self):
		if self.config_id:
			if self.config_id.stamp:
				self.stamp = self.config_id.stamp

	def compute_allowance_line(self):
		if self.config_id:
			domain = []
			if self.branch_id:
				domain.append(('company_id','=',self.branch_id.id))
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
			if self.eligible == 'degree':
				ids_list = []
				for degree in self.degree_ids:
					ids_list.append(degree.id)
				domain.append(('degree_id','in',ids_list))
			
			lines_list = []
			for employee in self.env['hr.employee'].search(domain):
				amount = 0.00
				from_salary = 0.00
				rules = []
				no_months = 0
				stamp = self.stamp.amount
				for config_line in self.config_id.line_ids:
					for degree in config_line.degree_id:
						if degree == employee.degree_id:
							if config_line.marital_status:
								if config_line.marital == employee.marital:
									for rule in config_line.salary_rule_id:
										rules.append(rule.id)
									no_months = config_line.no_months
							else:
								for rule in config_line.salary_rule_id:
									rules.append(rule.id)
								no_months = config_line.no_months
				payslips = self.env['hr.payslip'].search([('employee_id','=',employee.id)])
				if payslips:
					last_payslip = self.env['hr.payslip'].search([('employee_id','=',employee.id)])[-1]
					for line in last_payslip.line_ids:
						if line.salary_rule_id.id in rules:
							amount += line.total * no_months
							from_salary += line.total

				if amount == 0:
					stamp = 0

				lines_list.append({'employee_id':employee.id,
					'from_salary':from_salary,
					'no_months':no_months,
					'amount':amount,
					'stamp':stamp,
					'date':self.date,
					})

			self.line_ids = False
			self.line_ids = lines_list
			for line in self.line_ids:
				line.get_allowance_allowance()

	def do_submit(self):
		if not self.line_ids:
			raise Warning(_('Please enter allowance details'))
		if self.total_amount == 0:
			raise Warning(_('Total amount can not be zero'))
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
		for rati in self.env['ratification.list'].search([('allowance_id','=',self.id)]):
			rati.write({'state':'canceled'})
			rati.sudo().unlink()
		if self.config_id.central == True:
			ratification_line = []
			ratification = self.env['ratification.list'].create({'name':'مُسير ('+self.name+')',
				'date':date.today(),
				'from_hr':True,
				'allowance_id':self.id,
				'company_id' : self.env['res.company'].search([('is_main_company','=',True)])[0].id
				})
			for line in self.line_ids:
				deduction_list = []
				if self.stamp and self.stamp.amount != 0:
					deduction_list.append({'tax_id':self.stamp,'name':self.stamp.name,'amount':self.stamp.amount,'company_id' : self.env['res.company'].search([('is_main_company','=',True)])[0].id,'branch_id':line.employee_id.company_id.id,})
				#ratification line
				if line.net != 0:
					ratification_line.append({
						'name':self.name,
						'partner_id':line.employee_id.partner_id.id,
						'branch_id':line.employee_id.company_id.id,
						'amount':line.amount,
						'account_id':self.config_id.account_id.id,
						'analytic_account_id':self.config_id.account_id.parent_budget_item_id.id,
						'deduction_ids':deduction_list,
						'ratification_list_id':ratification.id,
						'company_id' : self.env['res.company'].search([('is_main_company','=',True)])[0].id})
			ratification.ratification_line_ids = ratification_line
		else:
			ratification_line = []
			ratification = self.env['ratification.list'].create({'name':'مُسير ('+self.name+')',
				'date':date.today(),
				'from_hr':True,
				'allowance_id':self.id,
				})
			for line in self.line_ids:
				deduction_list = []
				if self.stamp and self.stamp.amount != 0:
					deduction_list.append({'tax_id':self.stamp,'name':self.stamp.name,'amount':self.stamp.amount})
				#ratification line
				if line.net != 0:
					ratification_line.append({
						'name':self.name,
						'partner_id':line.employee_id.partner_id.id,
						'branch_id':line.employee_id.company_id.id,
						'amount':line.amount,
						'account_id':self.config_id.account_id.id,
						'analytic_account_id':self.config_id.account_id.parent_budget_item_id.id,
						'deduction_ids':deduction_list,
						'ratification_list_id':ratification.id,})
			ratification.ratification_line_ids = ratification_line
		for rec in self:
			for line in rec.line_ids:
				line.state = 'accounting'
		self.state = 'accounting'
		if self.branch_id:
			self.company_id = self.branch_id.id

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

class allowanceAllowanceLine(models.Model):
	_name="allowance.allowance.line"
	_rec_name = 'employee_id'

	employee_id = fields.Many2one("hr.employee",required=True , )
	employee_no = fields.Integer(related='employee_id.number' )
	date = fields.Date()
	department_id = fields.Many2one("hr.department", )
	degree_id = fields.Many2one('functional.degree', )
	marital=fields.Selection([('single','SINHLE'),('married','Married'),('have_kids','Married  and have kids'),('widowre','Widowre'),('divorced','Divorced')],track_visibility="onchange")
	from_salary = fields.Float()
	no_months = fields.Float()
	amount = fields.Float(string="Allowance amount",)
	stamp = fields.Float( )
	net = fields.Float("Net",)
	account_number = fields.Char("Account Number",related='employee_id.bank_account_id.acc_number', )
	allowance_allowance_id = fields.Many2one("allowance.allowance",string="Allowance Name",readonly=True,ondelete='cascade')
	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits and wages'),
		('personnel','Personnel'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounting','Accounting')], string="Status" ,default='draft',track_visibility="onchange" )



	@api.onchange('employee_id')
	@api.multi
	def get_allowance_allowance(self):
		if self.employee_id:
			self.department_id = self.employee_id.department_id
			self.degree_id = self.employee_id.degree_id
			self.marital = self.employee_id.marital
			if self.amount - self.stamp > 0:
				self.net = self.amount - self.stamp
				

class allowanceAllowanceConfig(models.Model):
	_name="allowance.allowance.config"
	_inherit = ['mail.thread','mail.activity.mixin']
	_order = "id desc"
	
	name = fields.Char(required=True,track_visibility="onchange")
	is_active = fields.Boolean(track_visibility="onchange",default=True)
	central = fields.Boolean(track_visibility="onchange",default=False)
	account_id = fields.Many2one('account.account', domain=[('is_group','=','sub_account')],track_visibility="onchange")
	stamp = fields.Many2one('account.tax',track_visibility="onchange")
	line_ids = fields.One2many('allowance.allowance.config.line','line_id',)
	company_id = fields.Many2one('res.company',string='Branch',default=lambda self: self.env.user.company_id,readonly=True,)

	@api.onchange('central')
	def onchange_central(self):
		if self.central and self.env.user.company_id.is_main_company == False:
			raise Warning(_('The setting of this allowance can only be modified in the presidency'))
		self.account_id = False


	def toggle_active(self):
		if self.is_active == True:
			self.is_active = False
		elif self.is_active == False:
			self.is_active = True

class allowanceAllowanceConfig(models.Model):
	_name="allowance.allowance.config.line"
	degree_id = fields.Many2many('functional.degree',required=True,)
	marital_status = fields.Boolean(string="Depends on marital status",)
	marital=fields.Selection([('single','SINHLE'),('married','Married'),('have_kids','Married  and have kids'),('widowre','Widowre'),('divorced','Divorced')],track_visibility="onchange")	
	salary_rule_id = fields.Many2many('hr.salary.rule',required=True,)
	no_months = fields.Integer(required=True,)

	line_id = fields.Many2one('allowance.allowance.config',)