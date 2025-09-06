# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning

class warning(models.Model):
	_name = 'warning.warning'
	_inherit = ['mail.thread','mail.activity.mixin']
	_description = "warning"
	_rec_name = 'employee_id'

	employee_no = fields.Integer(default=False,track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee','Employee',required=True,track_visibility='onchange')
	date = fields.Date(default=lambda self: fields.Date.today(), track_visibility='onchange')
	current_location = fields.Many2one('hr.department',related='employee_id.department_id',track_visibility='onchange')
	functional_degree = fields.Many2one('functional.degree',related='employee_id.degree_id',track_visibility='onchange')
	type_id = fields.Many2one('warning.type',string='Warning Type',required=True,track_visibility='onchange')
	warning_text = fields.Html(track_visibility='onchange')
	reason_refuse = fields.Html("the reason of refuse",track_visibility='onchange')

	submitted = fields.Boolean()
	state = fields.Selection([('draft','Draft'),('employment_department','Employment Department'),('hrm_confirm','Human Resource Management'),('gm_hr_confirm','General Administration for Human Resources'),('rejected','Rejected')], default='draft',track_visibility='onchange')

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
			

	@api.multi
	def employment_department(self):
		self.write({'state':'employment_department'})

	@api.multi
	def hrm_confirm(self):
		self.write({'state':'hrm_confirm'})

	@api.multi
	def gm_hr_confirm(self):
		if self.employee_id.user_id:
			self.env['mail.activity'].create({
				'res_name': self.type_id.name,
				'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
				'note': self.type_id.name,
				'date_deadline':self.date,
				'summary': 'warning',
				'user_id': self.employee_id.user_id.id,
				'res_id': self.id,
				'res_model_id': self.env.ref('kamil_hr_violation_sanction.model_warning_warning').id,
			})
		self.write({'state':'gm_hr_confirm'})

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
	def create(self, values):
		res = super(warning, self).create(values)
		res.name = res.type_id.name +' - '+res.employee_id.name
		return res



class warningType(models.Model):
	_name = 'warning.type'

	name = fields.Char(required=True,)