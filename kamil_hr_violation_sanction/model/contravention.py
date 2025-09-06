# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning



class hrContravention(models.Model):
	_name = "hr.contravention"
	_inherit = ['mail.thread','mail.activity.mixin']
	
	name = fields.Char(readonly=True)
	employee_no = fields.Integer(default=False,track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee' , required=True,track_visibility='onchange')
	date = fields.Date(default=lambda self: fields.Date.today())
	managment_id = fields.Many2one("hr.department",string="Managment",related='employee_id.unit_id')
	department_id = fields.Many2one("hr.department",related='employee_id.department_id')
	degree_id = fields.Many2one('functional.degree',related='employee_id.degree_id')
	summary_contravention= fields.Text(required=True,track_visibility='onchange')
	type_penalty =  fields.Selection([
		('warning' , 'Attention'),
		('discount' , 'Discount'),
		('warning_and_discount','Attention & Discount'),
		('reduce_degree','Reduce Degree'),('termination','Termination')] ,)
	attachment = fields.Binary()

	reason_refuse = fields.Html("the reason of refuse",track_visibility='onchange')
	

	warning_type_id = fields.Many2one('warning.type',track_visibility='onchange')
	warning_text = fields.Html(string="Warning Text",track_visibility='onchange')
	summary_committees=  fields.Html(string="Summary of committees decision")
	accounting_type=fields.Selection([('realization','Realization'),('accounting_repairmen','Accounting repairmen'),('agazi_accounting','Agazi Accounting')])
	current_degree = fields.Many2one('functional.degree')
	new_degree =fields.Many2one('functional.degree')
	type_discount = fields.Selection([
		('salary' , 'From salary '),
		('incentive','Incentive')] , default='salary')
	number_of_days = fields.Integer()
	incentive = fields.Many2one('incentive.type', domain=[('monthly_performance_discount','=','active'), ])
	incentive_discount = fields.Selection([
		('by_days' , 'By days'),
		('fixed_amount' , 'Fixed amount'),
		('percentage','Percentage')] ,)
	fixed_amount = fields.Float()
	percentage = fields.Float()
	days = fields.Float()
	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)), required=True,track_visibility='onchange')
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True,track_visibility='onchange')


	state = fields.Selection([('draft','Draft'),('employment_department','Employment Department'),('hrm_confirm','Human Resource Management'),('gm_hr_confirm','General Administration for Human Resources'),('rejected','Rejected')], default='draft')
	

	@api.onchange('date_from','date_to')
	def _date_constratin(self):
		if self.date_from > self.date_to and self.date_from and self.date_to:
			raise Warning(_('start date cannot be greater than end date'))


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

	@api.multi
	def employment_department(self):
		self.write({'state':'employment_department'})

	@api.multi
	def hrm_confirm(self):
		self.write({'state':'hrm_confirm'})

	@api.multi
	def gm_hr_confirm(self):
		if self.type_penalty == 'reduce_degree':
			self.employee_id.degree_id=self.new_degree

		elif self.type_penalty == 'warning':
			self.env['warning.warning'].create({'employee_id':self.employee_id.id,
				'employee_no':self.employee_no,
				'date':self.date,
				'type_id':self.warning_type_id.id,
				'warning_text':self.warning_text,})
		elif self.type_penalty == 'termination':
			self.env['termination.service'].create({'employee_id':self.employee_id.id,
				'employee_no':self.employee_id.number,
				'managment_id':self.employee_id.unit_id.id,
				'department_id':self.employee_id.department_id.id,
				'date':self.date,
				'reason':_('Termination'),})
		self.write({'state':'gm_hr_confirm'})

	# @api.multi
	# def action_reject(self):
	# 	if self.reason_refuse:
	# 		raise Warning(_('Please enter rejection reason'))
	# 	self.state = 'rejected'


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




	@api.model 
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('sequence.hr.contravention')
		
		return super(hrContravention, self).create(vals)

class ContraventionType(models.Model):
	_name = 'hr.contravention.type'

	name = fields.Char(required=True,)
