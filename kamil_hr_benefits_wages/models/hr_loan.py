# -*- coding: utf-8 -*-

from openerp import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class HrLoan(models.Model):
	_name = 'hr.loan'
	_inherit = ['mail.thread','mail.activity.mixin']
	_description= "Employee Loan"
	_order = "id desc"


	def unlink(self):
		for rec in self:
			if rec.state not in ['draft', 'refuse', 'refuse1']:
				raise Warning(_('Cannot be deleted in a case other than draft or refuse1'))
		return models.Model.unlink(self)
	

	@api.onchange('line_ids','loan_amount','no_month')	        		
	def _compute_amount(self):
		for loan in self:
			total_paid_amount = 0.00
			if loan.no_month > 0:
				loan.installment_amount = loan.loan_amount / loan.no_month
			flag = 0
			for line in loan.line_ids:
				if line.paid == True:
					total_paid_amount +=line.paid_amount
				elif line.paid == False:
					flag = 1
			if flag == 0 and self.line_ids:
				loan.state = 'paid'
			
			balance_amount =loan.loan_amount - total_paid_amount
			loan.total_amount = loan.loan_amount
			loan.balance_amount = balance_amount
			loan.total_paid_amount = total_paid_amount
			if loan.balance_amount == 0.00 and self.line_ids:
				loan.state = 'paid'
		
	name = fields.Char(readonly=True,track_visibility='onchange')
	user_id = fields.Many2one(
        'res.users', string='Requestor', default=lambda self: self.env.user)
	date = fields.Date(string="Date Request", default=lambda self: fields.Date.today(),track_visibility='onchange')
	employee_no = fields.Integer(string='Employee No',track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee', string="Employee", required=True,default=lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]),track_visibility='onchange')
	department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,track_visibility='onchange' )
	functional_id=fields.Many2one("hr.function", related='employee_id.functional_id', readonly=True,track_visibility='onchange')
	loan_amount = fields.Float(track_visibility='onchange')
	installment_amount = fields.Float(readonly=True,)
	total_amount = fields.Float(readonly=True,)
	total_paid_amount = fields.Float(readonly=True,)
	balance_amount = fields.Float(readonly=True,)
	loan_type = fields.Many2one('loan.type',  string="Loan Type", index=True,required=True,track_visibility='onchange')
	no_month = fields.Integer(string="No Of installments (By Months)", default=1,)
	register_payment_date = fields.Date(readonly=True, )
	payment_start_date = fields.Date(string="Start Date of Payment", track_visibility='onchange')
	last_net_salary = fields.Float(readonly=True, track_visibility='onchange')
	last_net_incentive = fields.Float(readonly=True, )
	color = fields.Boolean()
	line_ids = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", )
	deduction = fields.Selection([('salary','Salary'),('incentive','Incentive')],string="Deduction On", track_visibility='onchange',)
	incentive_id = fields.Many2one("incentive.type", domain=[('duration','=','monthly'), ],track_visibility="onchange")
	notes = fields.Html()
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)

	state = fields.Selection([
		('draft','Draft'),
		('general_manager','General manager/Branch Manager'),
		('committee_of_loans','Committee of loans'),
		('accounting','Accounting'),
		('done_registered_payment','Done register payment'),
		('start_payments','Start Payments'),
		('paid','Paid'),
		('refuse','Refuse'),
		('refuse1','Refuse1')
	], string="State", default='draft', track_visibility='onchange', copy=False,)
	
	@api.model
	def create(self, values):
		res = super(HrLoan, self).create(values)
		res.name = res.loan_type.name + ' - ' + res.employee_id.name
		return res


	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = False
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)],limit=1).id

	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			if self.loan_type:
				self.name = self.loan_type.name + ' - ' + self.employee_id.name
			self.employee_no = False
			self.employee_no = self.employee_id.number
			self._compute_net_salary()


	def _compute_net_salary(self):
		self.last_net_salary = 0.00
		if self.env['hr.payslip'].search([('employee_id','=',self.employee_id.id),('state','=','done')]):
			last_slip = self.env['hr.payslip'].search([])[-1]
			for line in last_slip.line_ids:
				if line.code == 'الاجمالى':
					self.last_net_salary = line.total

		self.last_net_incentive = 0.00
		if self.env['hr.incentive'].search([('incentive','=',self.incentive_id.id),('state','=','accounting')]):
			last_slip = self.env['hr.incentive'].search([('incentive','=',self.incentive_id.id),('state','=','accounting')])[-1]
			for line in last_slip.line_ids:
				if line.employee_id == self.employee_id:
					self.last_net_incentive = line.net

	@api.onchange('loan_type')
	def _onchange_loan_type(self):
		self.no_month = self.loan_type.no_month
		self.loan_amount = self.loan_type.max_amount

	@api.onchange('loan_amount')
	def _onchange_loan_amount(self):
		if self.loan_amount > self.loan_type.max_amount:
			raise Warning(_("The loan amount cannot be more than max amount %s ")%(self.loan_type.max_amount))
	
	@api.one
	def action_refuse(self):
		self.state = 'refuse'

	@api.one
	def action_refuse1(self):
		self.state = 'refuse1'


	@api.one
	def action_set_to_draft(self):
		self.state = 'draft'

	@api.multi
	def action_submit(self):
		self.compute_loan_line()
		self.state = 'general_manager'
		
	@api.one
	def action_gm_approve(self):
		self.state = "committee_of_loans"

	@api.one
	def action_committee_approve(self):
		self.compute_loan_line()
		ratification = self.env['ratification.ratification'].create({
			'partner_id':self.employee_id.partner_id.id,
			'state_id':self.employee_id.company_id.id,
			'ratification_type':'employee_loan',
			'name':self.loan_type.name+' للموظف '+self.employee_id.name,
			'loan_id':self.id,
			'date':date.today(),
			})
		ratification.line_ids = [{'name':self.loan_type.name+' للموظف '+self.employee_id.name,
		'amount':self.loan_amount,
		'account_id':self.loan_type.account_id.id,
		'analytic_account_id':self.loan_type.account_id.parent_budget_item_id.id,
		'the_type':'accounts_receivable',
		'ratification_id':ratification.id,}]
		self.state = "accounting"

	@api.one
	def action_start_payments(self):
		self.onchange_payment_start_date()
		self.state = "start_payments"
	
		
	
	def compute_loan_line(self):
		#loan amount != 0
		if self.loan_amount == 0:
			raise Warning(_("The loan amount cannot be zero"))

		for loan in self:
			amount_per_month = loan.loan_amount / loan.no_month
			loan.installment_amount = amount_per_month
			if loan.installment_amount > loan.last_net_salary:
				loan.color = True
			else:
				loan.color = False
			line_list = []
			for i in range(1, loan.no_month + 1):
				line_list.append({
					'paid_amount': amount_per_month,
					'employee_id': loan.employee_id.id,
					'payment_method':'system',
					'loan_id':loan.id})
			loan.line_ids = False
			loan.line_ids = line_list
			



	@api.onchange('payment_start_date')
	def onchange_payment_start_date(self):
		if self.payment_start_date:
			if self.payment_start_date < self.register_payment_date:
				raise Warning(_('Payments start date cannot be less than register payment date'))
			for loan in self:
				date_start_str = datetime.strptime(str(loan.payment_start_date),'%Y-%m-%d')
				amount_per_month = loan.loan_amount / loan.no_month
				for line in loan.line_ids:
					line.write({'paid_date':date_start_str.date()})
					date_start_str = date_start_str + relativedelta(months = 1)

			
			
class hr_loan_line(models.Model):
	_name="hr.loan.line"
	_description = "Employee Loans Lines"
		
	paid_date = fields.Date(string="Payment Date", readonly=True, )
	employee_id = fields.Many2one('hr.employee', readonly=True, )
	paid_amount= fields.Float(string="Amount", readonly=True, )
	paid = fields.Boolean(string="Paid",)
	payment_attachment = fields.Many2many('ir.attachment', attachment=True)

	notes = fields.Text()
	payment_method = fields.Selection([('system','System'),('manually','Manually')], default='system', required=True,)
	loan_id = fields.Many2one('hr.loan', string="Loan", ondelete='cascade')
	
	payroll_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)


class hr_loan_type(models.Model):
	_name = 'loan.type'
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(required=True,track_visibility='onchange')
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
	no_month = fields.Integer(string="No Of Month", default=1,required=True,track_visibility='onchange')
	max_amount = fields.Float('Max Amount',required=True,track_visibility='onchange')
	account_id = fields.Many2one('account.account', required=True, track_visibility='onchange',domain=[('is_group','=','sub_account')])
	deduct_account_id = fields.Many2one('account.tax',track_visibility='onchange', required=True,)

	loan_id = fields.One2many('hr.loan','loan_type', string="Loan")

	@api.model
	def create(self, values):
		res = super(hr_loan_type, self).create(values)
		if res.max_amount == 0:
			raise Warning(_('Max amount of loan can not be zero'))
		return res







	
	




















