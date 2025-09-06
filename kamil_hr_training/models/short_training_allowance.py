# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date, datetime, timedelta
from odoo.exceptions import Warning

class TrainingAllowance(models.Model):
	_name="training.allowance"
	_inherit = ['mail.thread','mail.activity.mixin']
	_description = 'Short Training Allowance'
	
	name = fields.Char(readonly=True,track_visibility="onchange")
	program_execution = fields.Many2one('program.execution',track_visibility="onchange")
	stamp = fields.Many2one('account.tax',track_visibility="onchange")
	date = fields.Date(default=lambda self: fields.Date.today(),track_visibility="onchange")
	no_days = fields.Integer(readonly=True, track_visibility="onchange")
	total = fields.Float(compute='_compute_total')
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
	line_ids = fields.One2many('training.allowance.line','line_id',string="Details")
	state = fields.Selection([
		('draft','Draft'),
		('training_department','Training Department'),
		('general_hr','General Administration for Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounting','Accounting')],string="Status", default='draft',track_visibility="onchange" )

	def do_return(self):
		if self.state == 'internal_auditor':
			self.state = 'general_hr'
		elif self.state == 'general_hr':
			self.state = 'training_department'
		elif self.state == 'training_department':
			self.state = 'draft'

	@api.model
	def create(self,vals):
		res = super(TrainingAllowance,self).create(vals)
		if res.program_execution:
			res.name = 'بدل تدريب ( '+ res.program_execution.name+' )'
		return res

	@api.onchange('program_execution','stamp')
	def compute_allowance_line(self):
		self.name = False
		self.line_ids = False
		if self.program_execution:
			self.name = 'بدل تدريب ( '+ self.program_execution.name+' )'
			lines = []
			if self.program_execution:
				if self.program_execution.date_to and self.program_execution.date_from:
					self.no_days = (self.program_execution.date_to - self.program_execution.date_from).days + 1
				settings = self.env['training.allowance.settings'].search([],limit=1)
				amount = 0.00
				for line in settings.line_ids:
					if line.from_day <= self.no_days and line.to_day >= self.no_days:
						amount = line.amount
				lines = []
				for line in self.program_execution.line_ids:
					lines.append({
						'employee_id':line.employee_id.id,
						'job_title_id': line.employee_id.job_title_id.id ,
						'no_days':self.no_days,
						'amount':amount,
						'total': self.no_days * amount,
						'stamp':self.stamp.amount,
						'net':self.no_days * amount - self.stamp.amount,
						})
				self.line_ids = lines

	@api.onchange('line_ids')
	def _compute_total(self):
		for rec in self:
			total = 0.00
			for line in rec.line_ids:
				total += line.net
			rec.total = total

	def training_department(self):
		if not self.line_ids:
			raise Warning(_('Total amount can not be zero'))
		self.state = 'training_department'

	def general_hr(self):
		self.state = 'general_hr'

	def internal_auditor(self):
		self.state='internal_auditor'	

	def send_to_account(self):
		#Delete the old rati list
		 
		for rati in self.env['ratification.list'].search([('training_allowance_id','=',self.id)]):
			rati.write({'state':'canceled'})
			rati.sudo().unlink()
		training_allowance = self.env['hr.account.config'].search([],limit=1).training_allowance

		ratification_line = []
		ratification = self.env['ratification.list'].create({'name':self.name,
			'date':date.today(),
			'from_hr':True,
			'training_allowance_id':self.id,
			})
		for line in self.line_ids:
			#ratification line
			ratification_line.append({
				'name':self.name,
				'partner_id':line.employee_id.partner_id.id,
				'branch_id':self.company_id.id,
				'account_id':training_allowance.id,
				'analytic_account_id':training_allowance.parent_budget_item_id.id,
				'amount':line.total,
				'ratification_list_id':ratification.id,
				'company_id':self.company_id.id,
				'deduction_ids':[{'tax_id':self.stamp,'name':self.stamp.name,'amount':self.stamp.amount}]})
		ratification.ratification_line_ids = ratification_line
		self.state = 'accounting'

class TrainingAllowanceLine(models.Model):
	_name="training.allowance.line"

	employee_id = fields.Many2one('hr.employee',)
	job_title_id = fields.Many2one('job.title',readonly=True,)
	amount = fields.Float()
	no_days = fields.Integer(readonly=True, )
	total = fields.Float(readonly=True, )
	stamp = fields.Float()
	net = fields.Float()
	line_id = fields.Many2one('training.allowance')




class TrainingAllowanceSettings(models.Model):
	_name="training.allowance.settings"
	
	name = fields.Char(readonly=True, default=_('Short Training Allowance Settings'))
	line_ids = fields.One2many('training.allowance.settings.line','line_id',string="Details")


class TrainingAllowanceSettingsLine(models.Model):
	_name="training.allowance.settings.line"

	from_day = fields.Integer(required=True)
	to_day = fields.Integer(required=True)
	amount = fields.Integer(required=True)
	line_id = fields.Many2one('training.allowance.settings')
