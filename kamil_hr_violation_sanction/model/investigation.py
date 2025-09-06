# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from odoo.exceptions import Warning


class hr_investigation(models.Model):
	_name = "hr.investigation"
	_inherit = ['mail.thread','mail.activity.mixin',]
	_description = "Investigation"

	name = fields.Char(readonly=True,track_visibility='onchange')
	date = fields.Date(string="Date", default=lambda self: fields.Date.today(), readonly=True)
	user_id = fields.Many2one('res.users', string="Employee",default=lambda self: self.env.user,track_visibility='onchange')
	employee_no = fields.Integer(default=False , track_visibility='onchange')
	employee_id =fields.Many2one('hr.employee', 'Employee Name',
			required=True , track_visibility='onchange')
	management_id = fields.Many2one("hr.department",string="Management",related='employee_id.unit_id')
	department_id = fields.Many2one('hr.department',string="Department" ,related='employee_id.department_id',)
	functional_degree = fields.Many2one('functional.degree',related='employee_id.degree_id')
	summary_investigation= fields.Text(required=True,)
	state = fields.Selection([
		('draft','Draft'),
		('employee','To Fill By Employee'),
		('filled','Filled By Employee'),
		('done','Aprroved'),
		('reject','rejectd')
	], string="State", default='draft', track_visibility='onchange', copy=False,)
	violation_type = fields.Many2one('investigation.type', string='Violation Type',required=True,)
	
	employee_comments = fields.Text(track_visibility='onchange')
	manager_comments = fields.Text(track_visibility='onchange')
	note  = fields.Text(string='Note')
	
	
	@api.model
	def create(self, values):
		res = super(hr_investigation, self).create(values)
		res.name = res.violation_type.name + ' - '+res.employee_id.name
		return res

	@api.one
	def action_approve(self):
		if self.employee_id.user_id:
			self.env['mail.activity'].create({
				'res_name': 'Investigation',
	            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
	            'note': _(self.violation_type.name),
	            'date_deadline':self.date,
	            'summary': 'Investigation',
	            'user_id': self.employee_id.user_id.id,
	            'res_id': self.id,
	            'res_model_id': self.env.ref('kamil_hr_violation_sanction.model_hr_investigation').id,
	        })

		self.write({
			'state':'employee'
		})
	@api.one
	def action_filled(self):
		if not self.employee_comments:
			raise Warning(_('Please enter your comments'))
		else:
			self.write({
				'state':'filled'
			})
		

	@api.one
	def action_maneger_approve(self):
		self.write({
			'state':'done'
		})
	
	@api.one
	def action_maneger_reject(self):
		if not self.manager_comments:
			raise Warning(_('Please enter rejection reason'))
		else:
			self.write({
				'state':'reject'
				})


	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = False
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)],limit=1).id
			

	@api.onchange('employee_id')
	def change_employee_id(self):
		self.department_id=self.employee_id.department_id

	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.employee_no = False
			self.employee_no = self.employee_id.number


class ViolationLog(models.Model):
	_name = 'violation.log'
	_description = 'History of  Employee violation'
	
	
	name  = fields.Char(string='Name',required=True,)
	investigation_id = fields.Many2one(comodel_name='hr.investigation', string="Investigation")
	date = fields.Date(string='Date',related="investigation_id.date")
	investigation_id_log = fields.Many2one(comodel_name='hr.investigation', string="Investigation")
	violation_type = fields.Many2one('investigation.type',)
	

class ModuleName(models.Model):
	_name = 'investigation.type'
	_description = 'The Employee violation'
	
	
	name  = fields.Char(string='Name',required=True,)
	date = fields.Date(string='Date')
	description = fields.Text()
	expect_decision = fields.Text(string='Decision')
	
	

	

	