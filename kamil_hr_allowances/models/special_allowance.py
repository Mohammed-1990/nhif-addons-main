# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning


class SpecialAllowance(models.Model):
	_name ="special.allowance"
	_inherit = ['mail.thread','mail.activity.mixin']
	
	name = fields.Char(required=True , track_visibility="onchange")
	job_title_id=fields.Many2one("job.title", required=True , track_visibility="onchange")
	employee_id = fields.Many2one("hr.employee",required=True, track_visibility="onchange")
	date = fields.Date(default=lambda self: fields.Date.today())
	total = fields.Float(compute='_compute_total')
	net = fields.Float(compute='_compute_total')
	stamp = fields.Many2one('account.tax')
	line_ids=fields.One2many("special.allowance.line","special_allowance_id","Details", copy=True)
	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits and wages'),
		('personnel','Personnel'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounting','Accounting')], string="Status" ,default='draft',track_visibility="onchange" )
	notes = fields.Html(track_visibility="onchange")

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise Warning(_('Cannot be deleted in a case other than draft'))
		return models.Model.unlink(self)



	@api.onchange('job_title_id')
	def _onchange_job_title_id(self):
		if self.job_title_id:
			self.employee_id = False
			return {'domain':
						{'employee_id':[('job_title_id','=',self.job_title_id.id), ]}}
	        

	@api.onchange('line_ids','stamp')
	def _compute_total(self):
		for rec in self:
			total = 0.00
			for line in rec.line_ids:
				total += line.amount
			rec.total = total
			rec.net = total - rec.stamp.amount

	def do_submit(self):
		if not self.line_ids:
			raise Warning(_('Please enter allowance details'))
		if self.net <= 0:
			raise Warning(_('Net amount can not be zero'))
		self.state = 'benefits_wages'

	def do_confirm(self):
		self.state = 'personnel'

	def do_personnel_confirm(self):
		self.state = 'general_directorate'

	def do_gd_confirm(self):
		# general directorate confirm
		self.state = 'internal_auditor'

	def do_ia_confirm(self):
		#Delete the old rati 
		for rati in self.env['ratification.ratification'].search([('special_allowance_id','=',self.id)]):
			rati.write({'state':'canceled'})
			rati.sudo().unlink()
		# internal auditor confirm
		deduction_list = []
		if self.stamp and self.stamp.amount != 0:
			deduction_list.append({'tax_id':self.stamp,'name':self.stamp.name,'amount':self.stamp.amount})
		special_allowance = self.env['hr.account.config'].search([],limit=1).special_allowance
		ratification = self.env['ratification.ratification'].create({
			'partner_id':self.employee_id.partner_id.id,
			'state_id':self.employee_id.company_id.id,
			'ratification_type':'salaries_and_benefits',
			'name':self.name,
			'from_hr':True,
			'special_allowance_id':self.id,
			})
		ratification.line_ids = [{'name':self.name,
		'amount':self.total,
		'account_id':special_allowance.id,
		'ratification_id':ratification.id,}]
		ratification.tax_ids = [{'name':self.stamp.name,
		'tax_id':self.stamp.id,
		'amount':self.stamp.amount,
		'deduction_ids':deduction_list,
		'ratification_id':ratification.id,}]
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

	def do_return1(self):
		if self.state == 'benefits_wages':
			self.state = 'draft'
		if self.state == 'personnel':
			self.state = 'benefits_wages'
		if self.state == 'general_directorate':
			self.state = 'personnel'
		if self.state == 'internal_auditor':
			self.state = 'general_directorate'

	def do_return2(self):
		if self.state == 'benefits_wages':
			self.state = 'draft'
		if self.state == 'personnel':
			self.state = 'benefits_wages'
		if self.state == 'general_directorate':
			self.state = 'personnel'
		if self.state == 'internal_auditor':
			self.state = 'general_directorate'

	def do_return3(self):
		if self.state == 'benefits_wages':
			self.state = 'draft'
		if self.state == 'personnel':
			self.state = 'benefits_wages'
		if self.state == 'general_directorate':
			self.state = 'personnel'
		if self.state == 'internal_auditor':
			self.state = 'general_directorate'


class SpecialAllowanceLine(models.Model):
	_name="special.allowance.line"
	allowance = fields.Char(required=True,)
	amount = fields.Float(required=True,)
	special_allowance_id = fields.Many2one("special.allowance")
