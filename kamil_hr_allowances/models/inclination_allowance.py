# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning


class inclinationAllowance(models.Model):
	_inherit = ['mail.thread','mail.activity.mixin']
	_name="inclination.allowance"
	_order = 'id desc'
	
	name = fields.Char(required=True, track_visibility="onchange")
	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)),required=True,)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),required=True,)
	amount = fields.Float(track_visibility="onchange")
	total_amount = fields.Float(compute='_compute_total_amount')
	stamp = fields.Many2one('account.tax')
	line_ids=fields.One2many("inclination.allowance.line","inclination_allowance_id","Employees Allowances", copy=True)
	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits and wages'),
		('personnel','Personnel'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounting','Accounting')], string="Status" ,default='draft',track_visibility="onchange" )
	notes = fields.Html(track_visibility="onchange")
	company_id = fields.Many2one('res.company',string='Branch',default=lambda self: self.env.user.company_id,readonly=True,)


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
		lines_list = []
		stamp = 0.00
		if self.stamp.amount_type=='fixed':
			stamp = self.stamp.amount
		for employee in self.env['hr.employee'].search([('nclination_deserved','=',True),('date_from','<=',self.date_to),('date_to','>=',self.date_to)]):
			lines_list.append({'employee_id':employee.id,
				'amount':self.amount,
				'stamp':stamp,
				'date_from':self.date_from,
				'date_to':self.date_to,

				})

		self.line_ids = False
		self.line_ids = lines_list
		for line in self.line_ids:
			line.get_inclination_allowance()

	def do_submit(self):
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

	def do_general_d_confirm(self):
		# general directorate confirm
		for rec in self:
			for line in rec.line_ids:
				line.state = 'internal_auditor'
		self.state = 'internal_auditor'

	def do_ia_confirm(self):
		#Delete the old rati list
		for rati in self.env['ratification.list'].search([('meal_allowance_id','=',self.id)]):
			rati.write({'state':'canceled'})
			rati.sudo().unlink()

		# internal auditor confirm

		ratification_line = []
		ratification = self.env['ratification.list'].create({'name':'مُسير ('+self.name+')',
			'date':date.today(),
			'from_hr':True,
			'inclination_allowance_id':self.id,
			})
		meal_account = self.env['hr.account.config'].search([],limit=1).inclination_allowance
		for line in self.line_ids:
			#ratification line
			ratification_line.append({
				'name':self.name,
				'partner_id':line.employee_id.partner_id.id,
				'branch_id':line.employee_id.company_id.id,
				'amount':line.amount,
				'account_id':meal_account.id,
				'deduction_ids':[{'tax_id':self.stamp,'name':self.stamp.name,'amount':line.stamp}],
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

class inclinationAllowanceLine(models.Model):
	_name="inclination.allowance.line"
	_rec_name = 'employee_id'
	
	employee_id = fields.Many2one("hr.employee",required=True, domain=[('nclination_deserved','=',True)])
	employee_no = fields.Integer(readonly=True,related='employee_id.number' )
	department_id = fields.Many2one("hr.department",readonly=True, )
	date_from = fields.Date()
	date_to = fields.Date()
	stamp = fields.Float(readonly=True,)
	amount = fields.Float(readonly=True)
	net = fields.Float("Net",readonly=True)
	account_number = fields.Char("Account Number",related='employee_id.bank_account_id.acc_number',readonly=True, )
	inclination_allowance_id = fields.Many2one("inclination.allowance")
	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits and wages'),
		('personnel','Personnel'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounting','Accounting')], string="Status" ,default='draft',track_visibility="onchange" )



	@api.onchange('employee_id','stamp','amount')
	@api.multi
	def get_inclination_allowance(self):
		if self.employee_id:
			self.department_id = self.employee_id.department_id
			if self.amount - self.stamp > 0:
				self.net= self.amount - self.stamp