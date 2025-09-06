# -*- coding: utf-8 -*-

from openerp import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta



class hrProjectsRequest(models.Model):
	_name = 'hr.projects.request'
	_order = "id desc"
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(default=" ",track_visibility="onchange")
	user_id = fields.Many2one(
        'res.users', string='Requestor', default=lambda self: self.env.user,track_visibility="onchange")
	date = fields.Date(string="Date Request", default=lambda self: fields.Date.today(), readonly=True)
	employee_no = fields.Integer(string='Employee No',track_visibility="onchange")
	employee_id = fields.Many2one('hr.employee', string="Employee", required=True,default=lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]),track_visibility="onchange")
	department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True, )
	functional_id = fields.Many2one("hr.function", related='employee_id.functional_id', readonly=True,)
	project_id = fields.Many2one("hr.projects", required=True, domain=[('state','=','confirmed'), ],track_visibility="onchange")
	number_varieties = fields.Boolean('Number from varieties',related='project_id.number_varieties', readonly=True, )
	amount = fields.Float('Amount',)
	max_quantity = fields.Integer(related='project_id.max_quantity',readonly=True,)
	no_month = fields.Integer(string="No Of Month",)
	required_quantity = fields.Integer()
	total_amount = fields.Float('Total Amount', readonly=True,compute='_compute_total_amount')
	payment_start_date = fields.Date(string="Start Date of Payment",)
	received_date = fields.Date(readonly=True, )
	incentive_id = fields.Many2one("incentive.type", related='project_id.incentive_id', readonly=True, )
	total_paid_amount = fields.Float(compute='_compute_amount')
	balance_amount = fields.Float(compute='_compute_amount')
	last_net_incentive = fields.Float(readonly=True, )
	installment_amount = fields.Float(readonly=True, )
	color = fields.Boolean()
	receipt_attachment = fields.Binary()

	state = fields.Selection([('draft','Draft'),('benefits_wages','Benefits and wages'),('project_manager','Project manager approve approve'),('receipt_confirmation','Receipt confirmation'),('done_registered_payment','Done Receipt confirmation'),('start_payments','Start Payments'),('paid','Paid'),('reject','Reject'),('reject1','Reject1')], default='draft')
	line_ids = fields.One2many('hr.projects.request.line','project_id',string='Projects Lines',)
	installments_line_ids = fields.One2many('project.installments.line','project_id',string='Projects installments Lines',)

	def unlink(self):
		for rec in self:
			if rec.state not in ['draft', 'reject', 'reject1']:
				raise Warning(_('Cannot be deleted in a case other than draft or refuse1'))
		return models.Model.unlink(self)
	

	@api.onchange('received_date','payment_start_date')
	@api.multi
	def _date(self):
		if self.received_date and self.payment_start_date:
			if self.received_date > self.payment_start_date:
				raise Warning(_("Sorry! The start date of the batch cannot be less than the date of receipt"))


	@api.model
	def create(self, values):
		res = super(hrProjectsRequest, self).create(values)
		res.name = res.project_id.name+" - "+res.employee_id.name
		return res

	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = False
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)],limit=1).id

	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			if self.project_id:
				self.name = self.project_id.name+" - "+self.employee_id.name
			self.employee_no = False
			self.employee_no = self.employee_id.number

	@api.onchange('employee_id')
	def _compute_net_incentive(self):
		max_id = 0
		self.last_net_incentive = False
		for incentive in self.env['hr.incentive'].search([('incentive','=',self.incentive_id.id),('state','=','approved')]):
			for line in incentive.line_ids:
				if line.employee_id == self.employee_id and incentive.id > max_id:
					max_id = incentive.id
		print(max_id)
		last_slip = self.env['hr.incentive'].search([('id','=',max_id)])
		for line in last_slip.line_ids:
			if line.employee_id == self.employee_id:
				self.last_net_incentive = line.net


	def action_submit(self):
		self.compute_installments_line()
		self.state = 'benefits_wages'


	def action_confirm(self):
		self.state = 'project_manager'

	def action_approve(self):
		self.state = 'receipt_confirmation'

	def action_receipt_confirmation(self):
		self.received_date = date.today()
		self.state = 'done_registered_payment'

	@api.one
	def action_start_payments(self):
		self.compute_installments_line()
		self.state = "start_payments"

	def action_reject(self):
		self.state = 'reject'

	def action_reject1(self):
		self.state = 'reject1'
	
	@api.depends('line_ids')
	def _onchange_line_ids(self):
		flag = 0
		for line in self.installments_line_ids:
			if line.paid == False:
				flag = 1
		if flag == 0:
			self.state = 'paid'
	        

	@api.onchange('required_quantity','project_id','line_ids')
	def _compute_total_amount(self):
		for rec in self:
			if rec.required_quantity != 0 and rec.project_id and rec.number_varieties == False:
				rec.total_amount = False
				rec.total_amount = rec.required_quantity * rec.amount

			if rec.project_id and rec.number_varieties != False:
				total = 0
				for line in rec.line_ids:
					total += line.total_amount
				rec.total_amount = total


	@api.onchange('project_id')
	def _onchange_project_id(self):
		if self.project_id:
			self.amount = self.project_id.amount
			self.no_month = self.project_id.no_month
		if self.number_varieties == True:
			line_list = []
			for line in self.project_id.line_ids:
				line_list.append({'name':line.name,
					'amount':line.amount,
					'max_quantity':line.max_quantity,
					'no_month':line.no_month,})
			self.line_ids = False
			self.line_ids = line_list

	@api.onchange('required_quantity','amount')
	def _onchange_required_quantity(self):
		if self.amount > self.project_id.amount:
			raise Warning(_("The amount can't be more than project max amount"))

		if self.required_quantity > self.max_quantity:
			raise Warning(_("The required quantity can't be more than available quantity"))

	def compute_installments_line(self):
		self._compute_net_incentive()
		if self.total_amount == 0:
			raise Warning(_("The project amount cannot be zero"))
		if self.payment_start_date:
			if self.payment_start_date < self.received_date:
				raise Warning(_('Payments start date cannot be less than received date'))

			line_list = []
			if self.number_varieties==True: 
				for project in self.line_ids:
					date_start_str = datetime.strptime(str(self.payment_start_date),'%Y-%m-%d')
					amount_per_month = project.total_amount / project.no_month

					for i in range(1, project.no_month + 1):
						line_list.append({
							'varietie_name':project.name,
							'payment_date':date_start_str.date(), 
							'amount': amount_per_month,
							'employee_id': self.employee_id.id,
							'month_number':date_start_str.month,
							'payment_method':'system',
							'project_id':self.id})
						date_start_str = date_start_str + relativedelta(months = 1)
			else:
				date_start_str = datetime.strptime(str(self.payment_start_date),'%Y-%m-%d')
				amount_per_month = self.total_amount / self.no_month
				self.installment_amount = amount_per_month
				if self.installment_amount > self.last_net_incentive:
					self.color = True
				else:
					self.color = False
				for i in range(1, self.no_month + 1):
					line_list.append({
						'varietie_name':self.project_id.name,
						'payment_date':date_start_str.date(), 
						'amount': amount_per_month,
						'employee_id': self.employee_id.id,
						'month_number':date_start_str.month,
						'payment_method':'system',
						'project_id':self.id})
					date_start_str = date_start_str + relativedelta(months = 1)
			self.installments_line_ids = False
			self.installments_line_ids = line_list
		else:
			line_list = []
			if self.number_varieties==True: 
				for project in self.line_ids:
					amount_per_month = project.total_amount / project.no_month

					for i in range(1, project.no_month + 1):
						line_list.append({
							'varietie_name':project.name,
							'amount': amount_per_month,
							'employee_id': self.employee_id.id,
							'project_id':self.id})
			else:
				amount_per_month = self.total_amount / self.no_month
				self.installment_amount = amount_per_month
				if self.installment_amount > self.last_net_incentive:
					self.color = True
				else:
					self.color = False
				for i in range(1, self.no_month + 1):
					line_list.append({
						'varietie_name':self.project_id.name,
						'amount': amount_per_month,
						'employee_id': self.employee_id.id,
						'payment_method':'system',
						'project_id':self.id})
			self.installments_line_ids = False
			self.installments_line_ids = line_list


	@api.one		
	def _compute_amount(self):
		total_paid_amount = 0.00
		for project in self:
			flag = 0
			for line in project.installments_line_ids:
				if line.paid == True:
					total_paid_amount +=line.amount
				elif line.paid == False:
					flag = 1
			if flag == 0:
				self.state = 'paid'
			
			balance_amount =project.total_amount - total_paid_amount
			self.balance_amount = balance_amount
			self.total_paid_amount = total_paid_amount
    

class hrProjectsRequestLines(models.Model):
	_name = 'hr.projects.request.line'

	name = fields.Char('Varietie name',readonly=True)
	amount = fields.Float('Amount', readonly=True, )
	max_quantity = fields.Integer(readonly=True, )
	no_month = fields.Integer(string="No Of Month", readonly=True, )
	required_quantity = fields.Integer()
	total_amount = fields.Float('Total Amount',compute='_compute_total_amount' )
	project_id = fields.Many2one('hr.projects.request', string="HR Projects Request", ondelete='cascade')

	@api.onchange('required_quantity')
	def _onchange_required_quantity(self):
		for rec in self:
			if rec.required_quantity > rec.max_quantity:
				raise Warning(_("The required quantity can't be more than available quantity"))
	@api.onchange('required_quantity')
	def _compute_total_amount(self):
		for rec in self:
			rec.total_amount = rec.amount * rec.required_quantity
	        
	
class projectInstallmentsLine(models.Model):
	_name="project.installments.line"
		
	varietie_name = fields.Char()
	payment_date = fields.Date()
	employee_id = fields.Many2one('hr.employee',)
	amount= fields.Float(string="Amount", )
	paid = fields.Boolean(default=False)
	payment_method = fields.Selection([('system','System'),('manually','Manually')], default='system', required=True,)
	payment_attachment = fields.Binary()
	notes = fields.Text()
	project_id = fields.Many2one('hr.projects.request', string="HR Projects Request", ondelete='cascade')















