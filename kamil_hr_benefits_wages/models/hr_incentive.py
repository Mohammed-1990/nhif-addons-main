# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class hrIncentive(models.Model):
	_name = 'hr.incentive'
	_inherit = ['mail.thread','mail.activity.mixin']
	_description= "Incentives"
	_order = "id desc"
		
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
	name = fields.Char(string="Incentive Name", track_visibility="onchange", required=True,)
	user_id = fields.Many2one('res.users', string='Create by', default=lambda self: self.env.user,track_visibility="onchange")
	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)),required=True,track_visibility="onchange",copy=False)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),required=True,track_visibility="onchange",copy=False)
	incentive = fields.Many2one('incentive.type', string="Incentive name",required=True,)
	eligible = fields.Selection([
		('branchs', 'Branchs'),
        ('employees', 'Employees'),
        ('departments', 'Departments'),
        ('appointment_types', 'Appointment Type'),],string='Eligible', required=True,track_visibility="onchange")
	company_ids = fields.Many2many('res.company', string='Branchs',track_visibility="onchange")
	employee_ids = fields.Many2many('hr.employee', string="Employees",track_visibility="onchange")
	department_ids = fields.Many2many('hr.department', string="Departments",track_visibility="onchange")
	appointment_type_ids = fields.Many2many('appointment.type', string="Appointment types",track_visibility="onchange")
	calculation_method = fields.Selection([('fixed','Fixed amount'),('fixed_degree','Fixed amount per degree'),('fixed_job_title','Fixed amount per Job title'),('salary','Salary'),('salary_job_title','Salary per Job title')], required=True,track_visibility="onchange")
	amount = fields.Float(track_visibility="onchange")
	salary_rule = fields.Many2one('hr.salary.rule',track_visibility="onchange")
	no_months = fields.Float('Number of months',track_visibility="onchange")
	stamp = fields.Many2one('account.tax',track_visibility="onchange")
	tax_percentage = fields.Many2one('account.tax',track_visibility="onchange",string="Tax percentage %")
	deduct_leaves = fields.Many2many('hr.leave.type',track_visibility="onchange",)

	line_ids = fields.One2many('hr.incentive.line', 'incentive_id', string="Incentive Line", index=True, copy=True)
	degree_line_ids = fields.One2many('fixed.degree.line', 'incentive_id', string="Degrees details",copy=True)
	job_line_ids = fields.One2many('fixed.job.line', 'incentive_id', string="Job title details", copy=True)
	
	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits and wages'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounting','Accounting')], string="Status" ,default='draft',track_visibility="onchange" )
	notes = fields.Html(track_visibility="onchange")

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise Warning(_('Cannot be deleted in a case other than draft'))
		return models.Model.unlink(self)
	
	@api.onchange('line_ids')
	def _onchange_line_ids(self):
		#duplicate employee
			employees = []
			for line in self.line_ids:
				if line.employee_id in employees:
					raise Warning('Cannot duplicate employee %s' %(line.employee_id.name))
				else:
					employees.append(line.employee_id)

	
	@api.onchange('date_from','date_to')
	def _date_constratin(self):
		if self.date_from > self.date_to:
			raise Warning(_('Start date cannot be greater than end date'))
	        
	def update_incentive_line(self):
		if self.calculation_method == 'fixed' and self.amount == 0:
			raise Warning(_("The incentive amount cannot be zero"))
		if self.calculation_method == 'salary' and self.no_months == 0:
			raise Warning(_("The number of months cannot be zero"))
		if self.calculation_method == 'fixed_degree' and not self.degree_line_ids:
			raise Warning(_("Please enter degrees amount details"))
		if self.calculation_method == 'fixed_job_title' and not self.job_line_ids:
			raise Warning(_("Please enter job titles amount details"))
		if self.calculation_method == 'salary_job_title' and (not self.job_line_ids or not self.salary_rule):
			raise Warning(_("Please enter job titles amount details"))
		lines_list = []
		for line in self.line_ids:
			if line.employee_id.appoiontment_type.eligible != 'without_second_class':
				stamp = tax = 0.00
				if self.stamp.amount_type=='fixed':
					stamp = self.stamp.amount
				#fixed amount
				if self.calculation_method == 'fixed':
					if line.employee_id.tax_exempt:
						tax = 0.00
					else:
						tax = (self.tax_percentage.amount*self.amount)/100
					lines_list.append({
						'name':self.name,
						'employee_id':line.employee_id.id,
						'amount':self.amount,
						'stamp':stamp,
						'tax_id':tax,})
				#month salary
				elif self.calculation_method == 'salary':
					amount = tax = salary_amount = 0.00
					if self.env['hr.payslip'].search([('employee_id','=',line.employee_id.id),('state','=','done')]):
						last_slip = self.env['hr.payslip'].search([('employee_id','=',line.employee_id.id),('state','=','done')])[-1]

						for line in last_slip.line_ids:
							if line.salary_rule_id == self.salary_rule:
								salary_amount = line.total
								amount = line.total * self.no_months
					if line.employee_id.tax_exempt:
						tax = 0.00
					else:
						tax = (self.tax_percentage.amount*amount)/100
					lines_list.append({
						'name':self.name,
						'employee_id':line.employee_id.id,
						'salary_amount':salary_amount,
						'amount':amount,
						'stamp':stamp,
						'tax_id':tax,})		

				elif self.calculation_method == 'fixed_degree':
					for line in self.degree_line_ids:
						for degree in line.degree_ids:
							if line.employee_id.degree_id == degree:
								if line.employee_id.tax_exempt:
									tax = 0.00
								else:
									tax = (self.tax_percentage.amount*line.amount)/100
								lines_list.append({
									'name':self.name,
									'employee_id':line.employee_id.id,
									'amount':line.amount,
									'stamp':stamp,
									'tax_id':tax,})
				elif self.calculation_method == 'fixed_job_title':
					amount = tax = 0.00
					for job_line in self.job_line_ids:
						for job in job_line.job_ids:
							if line.employee_id.job_title_id == job:
								if line.employee_id.tax_exempt:
									tax = 0.00
								else:
									tax = (self.tax_percentage.amount*job_line.amount)/100
								amount = job_line.amount
								lines_list.append({
									'name':self.name,
									'employee_id':line.employee_id.id,
									'amount':amount,
									'stamp':stamp,
									'tax_id':tax,})
				elif self.calculation_method == 'salary_job_title':
					amount = salary_amount = tax = 0.00
					if self.env['hr.payslip'].search([('employee_id','=',line.employee_id.id),('state','=','done')]):
						last_slip = self.env['hr.payslip'].search([('employee_id','=',line.employee_id.id),('state','=','done')])[-1]

						for slip_line in last_slip.line_ids:
							if slip_line.salary_rule_id == self.salary_rule:
								salary_amount = slip_line.total
					for job_line in self.job_line_ids:
						for job in job_line.job_ids:
							if line.employee_id.job_title_id == job:
								amount = salary_amount * job_line.amount
								if line.employee_id.tax_exempt:
									tax = 0.00
								else:
									tax = (self.tax_percentage.amount*amount)/100
								lines_list.append({
									'name':self.name,
									'employee_id':line.employee_id.id,
									'salary_amount':salary_amount,
									'amount':amount,
									'stamp':stamp,
									'tax_id':tax,})
		self.line_ids = False
		self.line_ids = lines_list
		for line in self.line_ids:
			line._onchange_employee_id()

	def compute_incentive_line(self):
		if self.calculation_method == 'fixed' and self.amount == 0:
			raise Warning(_("The incentive amount cannot be zero"))
		if self.calculation_method == 'salary' and self.no_months == 0:
			raise Warning(_("The number of months cannot be zero"))
		if self.calculation_method == 'fixed_degree' and not self.degree_line_ids:
			raise Warning(_("Please enter degrees amount details"))
		if self.calculation_method == 'fixed_job_title' and not self.job_line_ids:
			raise Warning(_("Please enter job titles amount details"))
		if self.calculation_method == 'salary_job_title' and (not self.job_line_ids or not self.salary_rule):
			raise Warning(_("Please enter job titles amount details"))
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
			domain.append(('unit_id','in',ids_list))
		if self.eligible == 'appointment_types':
			ids_list = []
			for appointment in self.appointment_type_ids:
				ids_list.append(appointment.id)
			domain.append(('appoiontment_type','in',ids_list))

		lines_list = []
		for employee in self.env['hr.employee'].search(domain):
			if employee.appoiontment_type.eligible != 'without_second_class':
				stamp = tax = 0.00
				if self.stamp.amount_type=='fixed':
					stamp = self.stamp.amount
				#fixed amount
				if self.calculation_method == 'fixed':
					if employee.tax_exempt:
						tax = 0.00
					else:
						tax = (self.tax_percentage.amount*self.amount)/100
					lines_list.append({
						'name':self.name,
						'employee_id':employee.id,
						'amount':self.amount,
						'stamp':stamp,
						'tax_id':tax,})
				#month salary
				elif self.calculation_method == 'salary':
					if self.env['hr.payslip'].search([('employee_id','=',employee.id),('state','=','done')]):
						last_slip = self.env['hr.payslip'].search([('employee_id','=',employee.id),('state','=','done')])[-1]

						amount = tax = salary_amount = 0.00
						for line in last_slip.line_ids:
							if line.salary_rule_id == self.salary_rule:
								salary_amount = line.total
								amount = line.total * self.no_months
								
						if employee.tax_exempt:
							tax = 0.00
						else:
							tax = (self.tax_percentage.amount*amount)/100

						lines_list.append({
							'name':self.name,
							'employee_id':employee.id,
							'salary_amount':salary_amount,
							'amount':amount,
							'stamp':stamp,
							'tax_id':tax,})

				elif self.calculation_method == 'fixed_degree':
					for line in self.degree_line_ids:
						for degree in line.degree_ids:
							if employee.degree_id == degree:
								if employee.tax_exempt:
									tax = 0.00
								else:
									tax = (self.tax_percentage.amount*line.amount)/100
								lines_list.append({
									'name':self.name,
									'employee_id':employee.id,
									'amount':line.amount,
									'stamp':stamp,
									'tax_id':tax,})
				elif self.calculation_method == 'fixed_job_title':
					amount = tax = 0.00
					for line in self.job_line_ids:
						for job in line.job_ids:
							if employee.job_title_id == job:
								if employee.tax_exempt:
									tax = 0.00
								else:
									tax = (self.tax_percentage.amount*line.amount)/100
								amount = line.amount
								lines_list.append({
									'name':self.name,
									'employee_id':employee.id,
									'amount':amount,
									'stamp':stamp,
									'tax_id':tax,})
				elif self.calculation_method == 'salary_job_title':
					amount = salary_amount = tax = 0.00
					if self.env['hr.payslip'].search([('employee_id','=',employee.id),('state','=','done')]):
						last_slip = self.env['hr.payslip'].search([('employee_id','=',employee.id),('state','=','done')])[-1]
						for line in last_slip.line_ids:
							if line.salary_rule_id == self.salary_rule:
								salary_amount = line.total
					for line in self.job_line_ids:
						for job in line.job_ids:
							if employee.job_title_id == job:
								amount = salary_amount * line.amount
								if employee.tax_exempt:
									tax = 0.00
								else:
									tax = (self.tax_percentage.amount*amount)/100
								lines_list.append({
									'name':self.name,
									'employee_id':employee.id,
									'salary_amount':salary_amount,
									'amount':amount,
									'stamp':stamp,
									'tax_id':tax,})

		for line in self.line_ids:
			line.unlink()
		self.line_ids = lines_list
		for line in self.line_ids:
			line._onchange_employee_id()

	def do_submit(self):
		if not self.line_ids:
			raise Warning(_('Please enter incentive details'))

		for rec in self:
			for line in rec.line_ids:
				line.state = 'benefits_wages'
		self.state = 'benefits_wages'

	def do_confirm(self):
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

	def do_return1(self):
		if self.state == 'benefits_wages':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'draft'
			self.state = 'draft'

	def do_return2(self):
		if self.state == 'general_directorate':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'benefits_wages'
			self.state = 'benefits_wages'
	
	def do_return3(self):
		if self.state == 'internal_auditor':
			for rec in self:
				for line in rec.line_ids:
					line.state = 'general_directorate'
			self.state = 'general_directorate'
	
	@api.one
	def do_ia_confirm(self):
		#Delete old rati list
		for rati in self.env['ratification.list'].search([('incentive_id','=',self.id)]):
			rati.write({'state':'canceled'})
			rati.sudo().unlink()

		ratification_line = []
		ratification = self.env['ratification.list'].create({'name':'مُسير ('+self.name+')',
			'date':date.today(),
			'from_hr':True,
			'incentive_id':self.id,

			})

		for line in self.line_ids:
			ded_list = []

			if line.employee_id.total_cards_amount != 0:
				for card in line.employee_id.cards_line_ids:
					if card.card_id.incentive_type_id == self.incentive:
						ded_list.append({'tax_id':card.card_id.tax_id,'name':card.card_id.name,'amount':card.total})
			if self.stamp and line.stamp != 0:
				ded_list.append({'tax_id':self.stamp,'name':self.stamp.name,'amount':line.stamp})
			if self.tax_percentage and line.tax_id != 0:
				ded_list.append({'tax_id':self.tax_percentage.id,'name':self.tax_percentage.name,'amount':line.tax_id})
			if line.deduction_amount != 0:
				ded_list.append({'tax_id':self.incentive.monthly_performance_account.id,'name':_('Monthly Performance Discount'),'amount':line.deduction_amount})
			if line.projects != 0:
				for project in self.env['hr.projects.request'].search([('employee_id','=',line.employee_id.id),('state','=','start_payments')]):
					for project_line in project.installments_line_ids:
						if project_line.payment_date and self.date_from and self.date_to:
							if project_line.payment_date >= self.date_from and project_line.payment_date <= self.date_to and project.incentive_id == self.incentive and project_line.paid == False:
								ded_list.append({'tax_id':project.project_id.deduct_account.id,'name':project.project_id.name,'amount': project_line.amount})
			if line.loans != 0:
				hr_loan = self.env['hr.loan'].search([('employee_id','=',line.employee_id.id),('state','=','start_payments'),('deduction','=','incentive'),('incentive_id','=',self.incentive.id)])
				for loan in hr_loan:
					for loan_line in loan.line_ids:
						if loan_line.paid == False and loan_line.paid_date: 
							if loan_line.paid_date >= self.date_from and loan_line.paid_date <= self.date_to:
								ded_list.append({'tax_id':loan.loan_type.deduct_account_id.id,'name':loan.loan_type.name,'amount':loan_line.paid_amount})
			if line.leave_deduction_amount > 0:
				ded_list.append({'tax_id':self.incentive.leave_deduction_id.id,'name':self.incentive.leave_deduction_id.name,'amount':line.leave_deduction_amount})
			if line.net > 0:
				if self.incentive.is_salary:
					# Accounts payable ratification
					ratification_line.append({
						'name':self.incentive.name,
						'the_type':'accounts_payable',
						'partner_id':line.employee_id.partner_id.id,
						'branch_id':line.employee_id.company_id.id,
						'amount':line.amount,
						'account_id':self.incentive.account_id.id,
						'analytic_account_id':self.incentive.account_id.parent_budget_item_id.id,
						'deduction_ids':ded_list,
						'ratification_list_id':ratification.id,})
				else:
					# Budget ratification
					ratification_line.append({
						'name':self.incentive.name,
						'the_type':'budget',
						'partner_id':line.employee_id.partner_id.id,
						'branch_id':line.employee_id.company_id.id,
						'amount':line.amount,
						'account_id':self.incentive.account_id.id,
						'analytic_account_id':self.incentive.account_id.parent_budget_item_id.id,
						'deduction_ids':ded_list,
						'ratification_list_id':ratification.id,})

		ratification.ratification_line_ids = ratification_line
		
		
		for rec in self:
			for line in rec.line_ids:
				line.state = 'accounting'
		self.state = 'accounting'

	def register_payment(self,incentive_id):
		for inc_line in incentive_id.line_ids:
			#Paid Projects 
			for project in self.env['hr.projects.request'].search([('employee_id','=',inc_line.employee_id.id),('state','=','start_payments')]):
				for line in project.installments_line_ids:
					if line.payment_date >= incentive_id.date_from and line.payment_date <= incentive_id.date_to and project.incentive_id == incentive_id.incentive and line.paid == False:
						#change project line state
						line.write({'paid': True})
						#change project state
						flag = 0
						for line in project.installments_line_ids:
							if line.paid == False:
								flag = 1
						if flag == 0:
							project.write({'state': paid})
			#Paid Loans
			hr_loan = self.env['hr.loan'].search([('employee_id','=',inc_line.employee_id.id),('state','=','start_payments'),('deduction','=','incentive'),('incentive_id','=',incentive_id.incentive.id)])
			for loan in hr_loan:
				for line in loan.line_ids:
					if line.paid_date: 
						if line.paid == False and line.paid_date >= incentive_id.date_from and line.paid_date <= incentive_id.date_to:
							line.write({'paid':True})
				loan._compute_amount()

	def canceled_register_payment(self,incentive_id):
		for inc_line in incentive_id.line_ids:
			#Paid Projects 
			for project in self.env['hr.projects.request'].search([('employee_id','=',inc_line.employee_id.id),('state','=','start_payments')]):
				for line in project.installments_line_ids:
					if line.payment_date >= incentive_id.date_from and line.payment_date <= incentive_id.date_to and project.incentive_id == incentive_id.incentive and line.paid == True:
						#change project line state
						line.write({'paid': False})
						#change project state
						project.state = 'start_payments'
								
			#Paid Loans
			hr_loan = self.env['hr.loan'].search([('employee_id','=',inc_line.employee_id.id),('state','=','start_payments'),('deduction','=','incentive'),('incentive_id','=',incentive_id.incentive.id)])
			for loan in hr_loan:
				for line in loan.line_ids:
					if line.paid_date: 
						if line.paid == True and line.paid_date >= incentive_id.date_from and line.paid_date <= incentive_id.date_to:
							line.write({'paid':False})
				loan._compute_amount()

class fixedDegreeLine(models.Model):
	_name="fixed.degree.line"
		
	degree_ids=fields.Many2many('functional.degree',string="Degrees", required=True,)
	amount = fields.Float(required=True,)
	incentive_id = fields.Many2one('hr.incentive', string="Incentive", ondelete='cascade')
	
class fixedJobLine(models.Model):
	_name="fixed.job.line"
		
	job_ids=fields.Many2many('job.title',string="Job titles", required=True,)
	amount = fields.Float(required=True,string='Amount/Months')
	incentive_id = fields.Many2one('hr.incentive', string="Incentive", ondelete='cascade')
		
class hrIncentiveLine(models.Model):
	_name = "hr.incentive.line"
	_description = "Incentives"

	name = fields.Char('Incentive Number')	
	employee_id = fields.Many2one('hr.employee', string="Employee", )
	employee_no = fields.Integer(readonly=True,related='employee_id.number' )
	department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True, )
	degree_id=fields.Many2one("functional.degree", related='employee_id.degree_id', readonly=True,)
	date_from = fields.Date(related='incentive_id.date_from')
	date_to = fields.Date(related='incentive_id.date_to')
	amount = fields.Float()
	leave_deduction_amount = fields.Float()
	deduction_percentage = fields.Float(string="Monthly performance discount rate %",)
	deduction_amount = fields.Float(string="Monthly performance discount amount",)
	violations_deduction = fields.Float()
	card = fields.Float()
	projects = fields.Float()
	loans = fields.Float()
	stamp = fields.Float()
	tax_id = fields.Float()
	net = fields.Float()
	salary_amount = fields.Float(string="From salary")
	total_deductions = fields.Float( string="Total Deductions")
	incentive = fields.Many2one('incentive.type', string="Incentive name",readonly=True, related='incentive_id.incentive', ondelete='restrict')
	project_id = fields.Many2one('hr.projects',)
	loan_type_id = fields.Many2one('loan.type',)
	incentive_id = fields.Many2one('hr.incentive', string="Incentive", ondelete='cascade')
	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits and wages'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounting','Accounting')], string="Status" ,default='draft',track_visibility="onchange" )

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise Warning(_('Cannot be deleted in a case other than draft'))
		return models.Model.unlink(self)


	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		for rec in self:
			#crads deductions
			total_cards_amount = 0.00
			for card in rec.employee_id.cards_line_ids:
				if card.card_id.incentive_type_id == rec.incentive_id.incentive:
					total_cards_amount += card.total
			rec.card = total_cards_amount

			#projects deduction
			total_projects = 0.00
			for project in self.env['hr.projects.request'].search([('employee_id','=',rec.employee_id.id),('state','=','start_payments')]):
				for line in project.installments_line_ids:
					if line.payment_date and rec.incentive_id.date_from and rec.incentive_id.date_to:
						if line.payment_date >= rec.incentive_id.date_from and line.payment_date <= rec.incentive_id.date_to and project.incentive_id == rec.incentive_id.incentive and line.paid == False:
							total_projects += line.amount
			rec.projects = total_projects
			total_loans = 0.00
			hr_loan = rec.env['hr.loan'].search([('employee_id','=',rec.employee_id.id),('state','=','start_payments'),('deduction','=','incentive'),('incentive_id','=',self.incentive.id)])
			loan_lines = []
			for loan in hr_loan:
				for line in loan.line_ids:
					if line.paid == False and line.paid_date: 
						if line.paid == False and line.paid_date >= rec.date_from and line.paid_date <= rec.date_to:
							total_loans += line.paid_amount
			rec.loans = total_loans

			leave_emp = self.env['hr.leave'].search(['&',('employee_id','=',rec.employee_id.id),'|','|','&',('request_date_from','<',rec.incentive_id.date_from),('request_date_to','>',rec.incentive_id.date_to),'&',('request_date_from','>=',rec.incentive_id.date_from),('request_date_from','<=',rec.incentive_id.date_to),'&',('request_date_to','>=',rec.incentive_id.date_from),('request_date_to','<=',rec.incentive_id.date_to)])


			days_leave = 0
			leaves_list = []
			for leave in self.incentive_id.deduct_leaves:
				leaves_list.append(leave.id)
			for leave in leave_emp:
				if leave.state == 'validate' and (leave.holiday_status_id.id in leaves_list or leave.holiday_status_id.stop_incentive=='yes'):
					if leave.request_date_from >= rec.incentive_id.date_from and leave.request_date_to <= rec.incentive_id.date_to:
						days_leave += leave.number_of_days_display
					elif leave.request_date_from < rec.incentive_id.date_from:
						different_days = (fields.Date.from_string(rec.incentive_id.date_from)-fields.Date.from_string(leave.request_date_from)).days
						days_leave += leave.number_of_days_display - different_days
					elif leave.request_date_to > rec.incentive_id.date_to:
						different_days = (fields.Date.from_string(leave.request_date_to)-fields.Date.from_string(rec.incentive_id.date_to)).days
						days_leave += leave.number_of_days_display - different_days
	
			if days_leave > 30:
				days_leave = 30
			day_amount = rec.amount/30
			entitlement = day_amount*days_leave
			rec.write({'leave_deduction_amount':str(entitlement)})

			#deduction percentage of evaluation
			evaluations = self.env['monthly.performance'].search([('state','=','approved'),('date_from','=',rec.incentive_id.date_from),('date_to','=',rec.incentive_id.date_to),])
			for evaluation in evaluations:
				for line in evaluation.line_ids:
					if line.employee_id == rec.employee_id:
						rec.deduction_percentage = line.discount_percentage

			rec.deduction_amount = (rec.deduction_percentage * rec.amount)/100


			#violations deduction
			violations_total = 0.00
			for violation in self.env['hr.contravention'].search([('employee_id','=',rec.employee_id.id),('state','=','confirmed'),('date_from','<=',rec.incentive_id.date_from),('date_to','>=',rec.incentive_id.date_to),('type_penalty','in',['discount','warning_and_discount']),('type_discount','=','incentive')]):
				if violation.incentive_discount == 'fixed_amount':
					violations_total += violation.fixed_amount
				elif violation.incentive_discount == 'percentage':
					violations_total += (violation.percentage * rec.amount)/100
				elif violation.incentive_discount == 'by_days':
					violations_total += (rec.amount/30) * violation.days
			rec.violations_deduction = violations_total

			#compute total deductions
			rec.total_deductions = rec.violations_deduction + rec.deduction_amount + rec.card + rec.projects + rec.loans + rec.stamp + rec.tax_id + rec.leave_deduction_amount
			#compute net
			net = rec.amount - rec.total_deductions
			if net < 0:
				net = 0.00
			rec.net = net

	@api.onchange('leave_deduction_amount','deduction_amount','card','projects','violations_deduction','loans','amount','card', 'stamp', 'tax_id')
	def _onchange_leave_deduction_amount(self):
		for rec in self:
			leave_emp = self.env['hr.leave'].search(['&',('employee_id','=',rec.employee_id.id),'|','|','&',('request_date_from','<',rec.incentive_id.date_from),('request_date_to','>',rec.incentive_id.date_to),'&',('request_date_from','>=',rec.incentive_id.date_from),('request_date_from','<=',rec.incentive_id.date_to),'&',('request_date_to','>=',rec.incentive_id.date_from),('request_date_to','<=',rec.incentive_id.date_to)])

			days_leave = 0
			leaves_list = []
			for leave in self.incentive_id.deduct_leaves:
				leaves_list.append(leave.id)
			for leave in leave_emp:
				if leave.state == 'validate' and (leave.holiday_status_id.id in leaves_list or leave.holiday_status_id.stop_incentive=='yes'):
					if leave.request_date_from >= rec.incentive_id.date_from and leave.request_date_to <= rec.incentive_id.date_to:
						days_leave += leave.number_of_days_display
					elif leave.request_date_from < rec.incentive_id.date_from:
						different_days = (fields.Date.from_string(rec.incentive_id.date_from)-fields.Date.from_string(leave.request_date_from)).days
						days_leave += leave.number_of_days_display - different_days
					elif leave.request_date_to > rec.incentive_id.date_to:
						different_days = (fields.Date.from_string(leave.request_date_to)-fields.Date.from_string(rec.incentive_id.date_to)).days
						days_leave += leave.number_of_days_display - different_days
			if days_leave > 30:
				days_leave = 30
			day_amount = rec.amount/30
			entitlement = day_amount*days_leave
			rec.write({'leave_deduction_amount':str(entitlement)})

			#compute total deductions
			rec.total_deductions = rec.violations_deduction + rec.deduction_amount + rec.card + rec.projects + rec.loans + rec.stamp + rec.tax_id + rec.leave_deduction_amount
			#compute net
			net = rec.amount - rec.total_deductions
			if net < 0:
				net = 0.00
			rec.net = net




class hrIncentiveType(models.Model):
	_name = 'incentive.type'
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(required=True, track_visibility="onchange")
	duration = fields.Selection([('monthly','Monthly'),('quarterly','Quarterly'),('midterm','Midterm'),('annual','Annual'),('other','Other')],string='Duration', required=True, track_visibility="onchange")	
	monthly_performance_discount = fields.Boolean(track_visibility="onchange")
	monthly_performance_account = fields.Many2one('account.tax',track_visibility="onchange",)
	account_id = fields.Many2one('account.account',required=True, domain=[('is_group','=','sub_account')], track_visibility="onchange")
	leave_deduction_id = fields.Many2one('account.tax',required=True,track_visibility="onchange")
	is_salary = fields.Boolean()
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)

			

