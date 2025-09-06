# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class workInjuries(models.Model):
	_name = "work.injuries"
	_inherit = ['mail.thread','mail.activity.mixin',]
	name = fields.Char('Injurie Number',readonly=True,)
	date = fields.Date(default=lambda self: fields.Date.today())
	employee_no = fields.Integer('Employee No')
	employee_id = fields.Many2one('hr.employee' , required=True,track_visibility="onchange")
	job_id = fields.Many2one('hr.function' , readonly=True,related='employee_id.functional_id', track_visibility="onchange")
	unit_id = fields.Many2one('hr.department', string="Unit",track_visibility="onchange",related="employee_id.unit_id")
	department_id = fields.Many2one('hr.department' , readonly=True, related='employee_id.department_id', track_visibility="onchange")
	cause_injury = fields.Text(required=True, track_visibility="onchange")
	type_injury = fields.Text(required=True, track_visibility="onchange")
	medical_report = fields.Binary("Medical report")
	note = fields.Text()

	@api.model 
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('sequence.work.injuries')
		
		return super(workInjuries, self).create(vals)

	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = False
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)]).id

	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.employee_no = False 
			self.employee_no = self.employee_id.number
