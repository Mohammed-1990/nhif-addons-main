# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date, datetime, timedelta
from odoo.exceptions import Warning

class StudyTrainingExtension(models.Model):
	_name="study.training.extension"
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(default='/')
	employee_no = fields.Integer(readonly=True, )
	employee_id = fields.Many2one("hr.employee",readonly=True, required=True,default=lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]))
	job_id = fields.Many2one('hr.function', string="Job",related='employee_id.functional_id',)
	department_id=fields.Many2one('hr.department',related='employee_id.department_id')
	study_id = fields.Many2one("study.mission", readonly=True, required=True, )
	from_date = fields.Date(related='study_id.date_from')
	to_date = fields.Date(readonly=True, )
	country = fields.Many2one("res.country",related='study_id.country')
	reason_extension = fields.Text(required=True,track_visibility="onchange")
	document = fields.Binary()
	to_date_extension = fields.Date(required=True,track_visibility="onchange")
	notes = fields.Html()
	state = fields.Selection([
		('draft', 'Draft'),
		('submitted','Has been sent'),
		('dep_training','Department Training Confirm'),
		('dep_hr', 'department HR Confirm'),
		('gm_confirm','General Manger Confirm'),
		('rejected', 'Rejected'),
		],default='draft',track_visibility="onchange")


	@api.onchange('to_date_extension')
	def _onchange_employee(self):
		if self.to_date_extension:
			if self.to_date_extension < self.to_date:
				raise Warning(_("Sorry! Extension End Date Should be greater than Extension Start Date."))

	# @api.onchange('employee_no')
	# def _onchange_employee_no(self):
	# 	if self.employee_no:
	# 		self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)]).id

	# @api.onchange('employee_id')
	# def _onchange_employee_id(self):
	# 	if self.employee_id:
	# 		self.employee_no = self.employee_id.number
	# 		self.study_id = False
	# 		if self.env['study.mission'].search([('employee_id','=',self.employee_id.id),('state','=','confirmed')],):
	# 			study = self.env['study.mission'].search([('employee_id','=',self.employee_id.id),('state','=','confirmed')],)[-1]
	# 			self.study_id = study.id


	@api.onchange('study_id')
	def _onchange_study_id(self):
		if self.study_id:
			self.employee_id = self.study_id.employee_id
			self.employee_no = self.study_id.employee_id.number

			if self.env['study.training.extension'].search([('employee_id','=',self.employee_id.id),('state','=','gm_confirm')]):
				extension = self.env['study.training.extension'].search([('employee_id','=',self.employee_id.id),('state','=','gm_confirm')])[-1]
				self.to_date = extension.to_date_extension
			else:
				self.to_date = self.study_id.date_to

	@api.multi
	def do_submit(self):
		self.write({'state':'submitted'})

	@api.multi
	def dep_training(self):
		self.write({'state':'dep_training'})

	@api.multi
	def dep_hr(self):
		self.write({'state':'dep_hr'})

	@api.multi
	def gm_confirm(self):
		self.write({'state':'gm_confirm'})

	@api.multi
	def do_return(self):
		if self.state == 'submitted':
			self.write({'state':'draft'})
		if self.state == 'dep_training':
			self.write({'state':'submitted'})
		if self.state == 'dep_hr':
			self.write({'state':'dep_training'})
		if self.state == 'gm_confirm':
			self.write({'state':'dep_hr'})

	@api.multi
	def do_reject(self):
		self.write({'state':'rejected'})

class StudyTrainingInterrput(models.Model):
	_name="study.training.interrupt"
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'employee_id'

	employee_no = fields.Char(track_visibility="onchange")
	employee_id = fields.Many2one("hr.employee",required=True,track_visibility="onchange", default=lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]))
	study_id = fields.Many2one("study.mission",required=True,readonly=True, track_visibility="onchange")
	from_date = fields.Date(readonly=True)
	to_date = fields.Date(readonly=True)
	country = fields.Many2one("res.country",readonly=True)
	type_interrupt = fields.Selection([
		('interrupt', 'Interrupt'),
		('cancel','Cancel'),
		],default='interrupt',required=True, string="Type",track_visibility="onchange")
	date = fields.Date(default=lambda self: fields.Date.today(),required=True)
	document = fields.Binary(required=True,track_visibility="onchange")
	reason = fields.Text(required=True)
	notes = fields.Html()
	state = fields.Selection([
		('draft','Draft'),
		('dep_training','Department Training Confirm'),
		('hr_development','Human Resource Development'),
		('general_directorate','General Directorate of Human Resources'),
		('gm_confirm','General Manger'),
		('rejected','Rejected'),
		], string="Status" ,default='draft',track_visibility="onchange" )
	@api.multi
	def do_submit(self):
		self.state = 'dep_training'

	@api.multi
	def hr_development(self):
		self.state = 'hr_development'

	@api.multi
	def general_directorate(self):
		self.state = 'general_directorate'

	@api.multi
	def gm_confirm(self):
		if self.type_interrupt == 'interrupt':
			self.study_id.state = 'interrupted'
		if self.type_interrupt == 'cancel':
			self.study_id.state = 'canceled'
		self.state = 'gm_confirm'

	@api.multi
	def do_reject(self):
		self.write({'state':'rejected'})

	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)]).id
		
	@api.onchange('employee_id')
	def _onchange_employee(self):
		if self.employee_id:
			self.employee_no = self.employee_id.number
			self.study_id = False
			if self.env['study.mission'].search([('employee_id','=',self.employee_id.id),('state','=','confirmed')],):
				study = self.env['study.mission'].search([('employee_id','=',self.employee_id.id),('state','=','confirmed')],)[-1]
				self.study_id = study.id
			self.from_date = self.study_id.date_from
			self.to_date = self.study_id.date_to
			self.country = self.study_id.country

class CriteriaEvaluation(models.Model):
	_name="criteria.evaluation"
	_inherit = ['mail.thread','mail.activity.mixin']
	
	name = fields.Char(required=True, string="Domain name")
	domain_type = fields.Selection([
		('evaluation_coach', 'Evaluation Coach'),
		('evaluation_training_center', 'Evaluation Training Center')],default="evaluation_coach",required=True)

class CriteriaName(models.Model):
	_name = "criteria.name"
	name = fields.Char(required=True)
	scop = fields.Many2one('criteria.evaluation',required=True)
	percentage = fields.Float(default="0.0")

class CoachRecord(models.Model):
	_name="coach.record"
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(required=True, track_visibility="onchange")
	emp_phone = fields.Char(required=True, track_visibility="onchange")
	birthday = fields.Date(track_visibility="onchange")
	email = fields.Char(required=True,track_visibility="onchange")
	address = fields.Char(track_visibility="onchange")
	document = fields.Binary(track_visibility="onchange")
	total_degree= fields.Float(compute='_compute_total_degree')
	evaluation_lines = fields.One2many("coach.record.line","coach_id")
	evaluation_lines2 = fields.One2many("coach.record.line2","coach_id2")
	state = fields.Selection([('draft','Draft'),
		('approved','Approved'),
		('rejected','Rejected')], track_visibility="onchange",default="draft")


	@api.multi
	def approved(self):
		self.state = 'approved'

	@api.multi
	def rejected(self):
		self.state = 'rejected'

	@api.model
	def create(self, values):
	    res = super(CoachRecord, self).create(values)
	    scop_list = []
	    for criteria in self.env['criteria.evaluation'].search([('domain_type','=','evaluation_coach')]):
	    	scop_list.append(criteria)
	    lines_list = []
	    for scop in scop_list:
	    	for criteria in self.env['criteria.name'].search([]):
	    		if criteria.scop == scop:
	    			lines_list.append({'scop':scop.id,
	    				'criteria':criteria.id,
	    				'percentage':criteria.percentage})
	    res.evaluation_lines = lines_list
	    return res

	
	@api.onchange('evaluation_lines')
	def _compute_total_degree(self):
		for rec in self:
			total = 0.00
			for line in rec.evaluation_lines:
				if line.evaluation:
					total += line.percentage
			rec.total_degree = total

		        	
class CoachRecordLine(models.Model):
	_name="coach.record.line"
	_inherit = ['mail.thread','mail.activity.mixin']

	scop = fields.Many2one("criteria.evaluation",readonly=True,  domain=[('domain_type','=','evaluation_coach'), ] , required=True)
	criteria = fields.Many2one("criteria.name", readonly=True,  domain=[('scop','=','scop'),])
	percentage = fields.Float(related='criteria.percentage')
	evaluation = fields.Boolean()
	coach_id = fields.Many2one("coach.record")


	        



class CoachRecordLine2(models.Model):
	_name = 'coach.record.line2'
	course_name = fields.Many2one('program.execution',required=True, readonly=True, )
	rating_ratio = fields.Float()
	notes = fields.Char()
	coach_id2 = fields.Many2one("coach.record")

class TrainingCenter(models.Model):
	_name="training.center"
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(required=True,track_visibility="onchange")
	num_first = fields.Char(track_visibility="onchange")
	num_second = fields.Char(track_visibility="onchange")
	num_third = fields.Char(track_visibility="onchange")
	country = fields.Many2one('res.country',)
	city =fields.Char(track_visibility="onchange")
	email = fields.Char(required=True,track_visibility="onchange")
	address = fields.Char(track_visibility="onchange")
	document = fields.Binary(track_visibility="onchange")
	total_degree= fields.Float(compute='_compute_total_degree')
	evaluation_lines = fields.One2many("training.center.line","training_center_id")
	evaluation_lines2 = fields.One2many("training.center.line2","training_center_id2")
	state = fields.Selection([('draft','Draft'),
		('approved','Approved'),
		('rejected','Rejected')], track_visibility="onchange",default="draft")


	@api.multi
	def approved(self):
		self.state = 'approved'

	@api.multi
	def rejected(self):
		self.state = 'rejected'
	@api.model
	def create(self, values):
	    res = super(TrainingCenter, self).create(values)
	    scop_list = []
	    for criteria in self.env['criteria.evaluation'].search([('domain_type','=','evaluation_training_center')]):
	    	scop_list.append(criteria)
	    lines_list = []
	    for scop in scop_list:
	    	for criteria in self.env['criteria.name'].search([]):
	    		if criteria.scop == scop:
	    			lines_list.append({'scop':scop.id,
	    				'criteria':criteria.id,
	    				'percentage':criteria.percentage})
	    res.evaluation_lines = lines_list
	    return res

	
	@api.onchange('evaluation_lines')
	def _compute_total_degree(self):
		for rec in self:
			total = 0.00
			for line in rec.evaluation_lines:
				if line.evaluation:
					total += line.percentage
			rec.total_degree = total




class TrainingCenterLine(models.Model):
	_name="training.center.line"
	
	scop = fields.Many2one("criteria.evaluation",domain=[('domain_type','=','evaluation_training_center'), ],required=True)
	criteria = fields.Many2one("criteria.name",domain=[('scop','=','scop'),])
	percentage = fields.Float(related='criteria.percentage')
	evaluation = fields.Boolean()
	training_center_id = fields.Many2one("training.center")

class TrainingCenterLine2(models.Model):
	_name="training.center.line2"
	course_name = fields.Many2one('program.execution', required=True,readonly=True, )
	rating_ratio = fields.Float()
	notes = fields.Char()
	training_center_id2 = fields.Many2one("training.center")

class TypesShortTraining(models.Model):
	_name = 'types.short.training'
	name = fields.Char(required=True,)