# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date, datetime, timedelta
from odoo.exceptions import Warning

class SupportTraining(models.Model):
	_name="support.training"
	name = fields.Char(required=True)


class TrainingExpenses(models.Model):
	_name ="training.expenses"
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(required=True)
	study_mission = fields.Many2one('study.mission',string='Study Training', domain=[('state','=','confirmed'), ], track_visibility="onchange", readonly=True, )
	mission_state =fields.Selection([
		('extension','Extension'),
		('cut','Cut'),
		('cancellation','Cancellation')], track_visibility="onchange")

	employee_no = fields.Char("Employee Number",track_visibility="onchange", readonly=True,  )
	employee_id = fields.Many2one("hr.employee",track_visibility="onchange",)
	department_id = fields.Many2one("hr.department",readonly=True)
	job_id = fields.Many2one("hr.function",string="Job",readonly=True)
	line_ids = fields.One2many("training.expenses.line","training_expenses_id")
	training_program = fields.Char(related='study_mission.training_program.name')
	university_id = fields.Many2one('university.model',related='study_mission.training_program.university_id')
	country =fields.Many2one("res.country",related='study_mission.training_program.country')
	city_id=fields.Many2one('city.city', related='study_mission.training_program.city_id')
	specialization = fields.Many2one('university.specialization', related='study_mission.training_program.specialization')
	total_amount = fields.Float(compute='_compute_total_amount')

	state = fields.Selection([
		('draft','Draft'),
		('confirmed','Confirmed'),
		('accounting','Accounting'),], string="Status" ,default='draft',track_visibility="onchange" )

	def unlink(self):
		if self.state != 'draft':
			raise Warning(_('Deletion is only possible if state is draft'))
		return models.Model.unlink(self)


	def do_confirm(self):
		if self.total_amount == 0.00:
			raise Warning(_('The total amount can not be zero'))
		self.state = 'confirmed'
	
	def do_accounting(self):
		ratification = self.env['ratification.ratification'].create({
			'partner_id':self.employee_id.partner_id.id,
			'partner_id':self.employee_id.partner_id.id,
			'name':self.name
			})
		ratification_lines = []
		for line in self.line_ids:
			if line.notes:
				name = line.support_type.name +' - '+str(line.notes)
			else:
				name = line.support_type.name
			ratification_lines.append({'name':name ,
				'amount':line.support_value,
				'ratification_id':ratification.id,})

		ratification.line_ids = ratification_lines
		self.state = 'accounting'


	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.study_mission:
			self.employee_no = self.employee_id.number
			self.department_id = self.employee_id.department_id
			self.job_id = self.employee_id.functional_id
			self.study_mission = False
			if self.env['study.mission'].search([('employee_id','=',self.employee_id.id),('state','=','confirmed')],):
				study = self.env['study.mission'].search([('employee_id','=',self.employee_id.id),('state','=','confirmed')],)[-1]
				self.study_mission = study.id

	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)]).id


	@api.onchange('line_ids')
	def _compute_total_amount(self):
		for rec in self:
			total = 0.00
			for line in rec.line_ids:
				total += line.support_value
			rec.total_amount = total

	

class TrainingExpensesLine(models.Model):
	_name = "training.expenses.line"
	support_type = fields.Many2one("support.training",required=True)
	support_value = fields.Float(required=True)
	document = fields.Binary()
	notes = fields.Char("Notes")
	training_expenses_id = fields.Many2one('training.expenses')




class internalShortTraining(models.Model):
	_name="internal.short.training"

	amount = fields.Float()
	expenses_id=fields.Many2one("training.setting")

class internalTallTraining(models.Model):
	_name="internal.tall.training"
	status = fields.Selection([
		('no' , 'No one'),
		('wife' , 'Wife only'),
		('wife_children','Wife and Children')] , default='no', string="Escorts")
	amount = fields.Float()
	expenses_id=fields.Many2one("training.setting")

class externalShortTraining(models.Model):
	_name="external.short.training"

	country = fields.Many2one("res.country")
	amount = fields.Float()
	currency = fields.Many2one("res.currency")
	expenses_id=fields.Many2one("training.setting")

class externalTallTraining(models.Model):
	_name="external.tall.training"

	country = fields.Many2one("res.country")
	status = fields.Selection([
		('no' , 'No one'),
		('wife' , 'Wife only'),
		('wife_children','Wife and Children')] , default='no', string="Escorts")
	amount = fields.Float()
	currency = fields.Many2one("res.currency")
	expenses_id=fields.Many2one("training.setting")



class TrainingSetting(models.Model):
	_name = "training.setting"

	name=fields.Char(required=True)
	internal_short_lines = fields.One2many("internal.short.training","expenses_id")
	internal_tall_lines = fields.One2many("internal.tall.training","expenses_id")
	external_short_lines = fields.One2many("external.short.training","expenses_id")
	external_tall_lines = fields.One2many("external.tall.training","expenses_id")

