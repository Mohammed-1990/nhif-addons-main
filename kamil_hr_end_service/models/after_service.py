# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import date
from odoo.exceptions import Warning


class afterService(models.Model):
	_name = "after.service"
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'employee_id'

	employee_no = fields.Integer(readonly=True,)
	employee_id = fields.Many2one('hr.employee' , domain=[('active','=', False)],track_visibility="onchange")
	date = fields.Date(default=lambda self: fields.Date.today(),track_visibility="onchange")
	job_id = fields.Many2one('hr.function' , readonly=True,related='employee_id.functional_id',track_visibility="onchange")
	department_id = fields.Many2one('hr.department',related='employee_id.department_id', readonly=True,track_visibility="onchange")
	degree_id = fields.Many2one('functional.degree',track_visibility="onchange")
	cash_alternative =fields.Selection([('fixed','Fixed amount'),('salary','Salary'),], default='fixed',track_visibility="onchange")
	amount = fields.Integer(default=0)
	salary_amount = fields.Float( readonly=True, )
	salary_amount2 = fields.Float( readonly=True, )
	number_months = fields.Float(track_visibility="onchange")
	merit_cash_alternative = fields.Float(compute='compute_values') 

	salary_rule = fields.Many2one('hr.salary.rule',track_visibility="onchange")
	baggage_relay = fields.Selection([('fixed','Fixed amount'),('salary','Salary'),], default='fixed',track_visibility="onchange")
	amount2 = fields.Float()
	number_months2 = fields.Float('Number Months',track_visibility="onchange")
	merit_baggage_relay = fields.Float(compute='compute_values') 

	salary_rule2 = fields.Many2one('hr.salary.rule',track_visibility="onchange")



	end_service_rewards = fields.Float(required=True,)

	total_amount = fields.Float(compute='compute_values')
	



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
	
	
	@api.model
	def create(self, values):
		res = super(afterService, self).create(values)
		if self.env['after.service'].search([('employee_id','=',res.employee_id.id),('id','!=',res.id)]):
			raise Warning(_('Cannot create more than one record for this employee'))

		return res

	def do_submit(self):
		self.compute_values()
		if self.total_amount == 0:
			raise Warning(_('Total amount can not be zero'))
		self.state = 'benefits_wages'

	def do_confirm(self):
		self.state = 'personnel'

	def do_personnel_confirm(self):
		self.state = 'general_directorate'

	def do_gd_confirm(self):
		# general directorate confirm
		self.state = 'internal_auditor'

	def do_ia_confirm(self):
		ratification = self.env['ratification.ratification'].create({'name':'فوائد ما بعد الخدمة للموظف/ة ('+self.employee_id.name+')',
			'partner_id':self.employee_id.partner_id.id,
			'state_id':self.employee_id.company_id.id,
			'ratification_type':'salaries_and_benefits',
			'company_id' : self.env['res.company'].search([('is_main_company','=',True)])[0].id,
			})
		config_account = self.env['hr.account.config'].search([('company_id','=',self.env['res.company'].search([('is_main_company','=',True)])[0].id)],limit=1)
		merit_cash_alternative = config_account.merit_cash_alternative
		merit_baggage_relay = config_account.merit_baggage_relay
		end_service_rewards = config_account.end_service_rewards

		ratification_lines = []
		if self.merit_cash_alternative != 0:
			ratification_lines.append({'amount':self.merit_cash_alternative,
				'account_id':merit_cash_alternative.id,
				'analytic_account_id':merit_cash_alternative.parent_budget_item_id.id,
				'name':'بديل نقدي',
				'ratification_id':ratification.id,
				'company_id' : self.env['res.company'].search([('is_main_company','=',True)])[0].id,})
		if self.merit_baggage_relay != 0:
			ratification_lines.append({'amount':self.merit_baggage_relay,
				'account_id':merit_baggage_relay.id,
				'analytic_account_id':merit_baggage_relay.parent_budget_item_id.id,
				'name':'ترحيل الأمتعة',
				'ratification_id':ratification.id,
				'company_id' : self.env['res.company'].search([('is_main_company','=',True)])[0].id,})
		if self.end_service_rewards != 0:
			ratification_lines.append({'amount':self.end_service_rewards,
				'account_id':end_service_rewards.id,
				'analytic_account_id':end_service_rewards.parent_budget_item_id.id,
				'name':'مكافأت نهايه الخدمه',
				'ratification_id':ratification.id,
				'company_id' : self.env['res.company'].search([('is_main_company','=',True)])[0].id,})


		ratification.line_ids = ratification_lines
		self.state = 'accounting'

	def do_return(self):
		if self.state == 'benefits_wages':
			self.state = 'draft'
		if self.state == 'personnel':
			self.state = 'benefits_wages'
		if self.state == 'general_directorate':
			self.state = 'personnel'
		if self.state == 'internal_auditor':
			self.state = 'general_directorate'


	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.employee_no = False 
			self.employee_no = self.employee_id.number
			self.degree_id = self.employee_id.degree_id

	@api.onchange('degree_id')
	def _onchange_degree_id(self):
		structure = self.env['salary.structure.line'].search([('degree_id','=',self.degree_id.id)],limit=1)
		self.amount = structure.primary_category + structure.high_cost + structure.housing_allowance + structure.deportation_allowance


	@api.onchange('amount','number_months','salary_rule','amount2','number_months2','salary_rule2','end_service_rewards')
	def compute_values(self):
		for rec in self:
			if rec.cash_alternative == 'fixed':
				rec.merit_cash_alternative = rec.amount
			elif rec.cash_alternative == 'salary':
				if self.env['hr.payslip'].search([('employee_id','=',rec.employee_id.id)]):
					payslip = self.env['hr.payslip'].search([('employee_id','=',rec.employee_id.id)])[-1]
					for line in payslip.line_ids:
						if line.salary_rule_id == rec.salary_rule:
							rec.salary_amount =  line.total 
							rec.merit_cash_alternative = rec.salary_amount * rec.number_months
			
			if rec.baggage_relay == 'fixed':
				rec.merit_baggage_relay = rec.amount2 
			elif rec.baggage_relay == 'salary':
				if self.env['hr.payslip'].search([('employee_id','=',rec.employee_id.id)]):
					payslip = self.env['hr.payslip'].search([('employee_id','=',rec.employee_id.id)])[-1]
					for line in payslip.line_ids:
						if line.salary_rule_id == rec.salary_rule2:
							rec.salary_amount2 =  line.total 
							rec.merit_baggage_relay = rec.salary_amount2 * rec.number_months2

			rec.total_amount = rec.merit_cash_alternative + rec.merit_baggage_relay + rec.end_service_rewards