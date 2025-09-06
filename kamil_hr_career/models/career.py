# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class new(models.Model):
	_name = 'evaluation.criteria'
	name = fields.Char(required=True,)

class monthlyPerformance(models.Model):
	_name = 'monthly.performance'
	name = fields.Char(required=True,)
	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)), required=True,)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True,)
	eligible = fields.Selection([
        ('branchs', 'Branchs'),
        ('employees', 'Employees'),
        ('departments', 'Departments'),
        ('appointment_types', 'Appointment Type'),
    ],string='Eligible', required=True,)
	company_ids = fields.Many2many('res.company', string='Branchs')
	employee_ids = fields.Many2many('hr.employee', string="Employees")
	department_ids = fields.Many2many('hr.department', string="Departments")
	appointment_type_ids = fields.Many2many('appointment.type', string="Appointment types")
	normative = fields.Integer()
	hours_allowed = fields.Integer()
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
	state = fields.Selection([
		('draft','Draft'),
		('career','Career'),
		('sub_manager','Human Resources Sub-Manager'),
		('general_directorate','General Directorate of Human Resources'),
		('approved','Approved')], string="Status" ,default='draft',track_visibility="onchange" )
	notes = fields.Html()
	line_ids = fields.Many2many('monthly.performance.line','line_id')

	def do_submit(self):
		self.state = 'career'


	def do_career_confirm(self):
		self.state = 'sub_manager'
	
	def do_sm_confirm(self):
		# sub manager confirm
		self.state = 'general_directorate'
	
	def do_gd_confirm(self):
		# general directorate confirm
		self.state = 'approved'

	def do_return(self):
		if self.state == 'career':
			self.state = 'draft'
		if self.state == 'sub_manager':
			self.state = 'career'
		if self.state == 'general_directorate':
			self.state = 'sub_manager'
	
	def do_return1(self):
		if self.state == 'career':
			self.state = 'draft'
		if self.state == 'sub_manager':
			self.state = 'career'
		if self.state == 'general_directorate':
			self.state = 'sub_manager'

	def do_return2(self):
		if self.state == 'career':
			self.state = 'draft'
		if self.state == 'sub_manager':
			self.state = 'career'
		if self.state == 'general_directorate':
			self.state = 'sub_manager'
	
	def compute_lines(self):
		if self.normative == 0:
			raise Warning(_("The normative cannot be zero"))
		domain = []
		if self.eligible == 'branchs':
			ids_list = []
			for company in self.company_ids:
				ids_list.append(company.id)
			domain.append(('company_id','in',ids_list))
		if self.eligible == 'employees':
			ids_list = []
			for employee in self.employee_ids:
				ids_list.append(employee.id)
			domain.append(('id','in',ids_list))
		if self.eligible == 'departments':
			ids_list = []
			for department in self.department_ids:
				ids_list.append(department.id)
			domain.append(('department_id','child_of',ids_list))
		if self.eligible == 'appointment_types':
			ids_list = []
			for appointment in self.appointment_type_ids:
				ids_list.append(appointment.id)
			domain.append(('appoiontment_type','in',ids_list))

		lines_list = []
		for employee in self.env['hr.employee'].search(domain):
			leaves = self.env['hr.leave'].search(['&',('employee_id','=',employee.id),'|','|','&',('request_date_from','<',self.date_from),('request_date_to','>',self.date_to),'&',('request_date_from','>=',self.date_from),('request_date_from','<=',self.date_to),'&',('request_date_to','>=',self.date_from),('request_date_to','<=',self.date_to)])
				
			days_leave = 0
			for leave in leaves:
				if leave.state == 'validate':
					if leave.request_date_from >= self.date_from and leave.request_date_to <= self.date_to:
						days_leave += leave.number_of_days_display
					elif leave.request_date_from < self.date_from:
						different_days = (fields.Date.from_string(self.date_from)-fields.Date.from_string(leave.request_date_from)).days
						days_leave += leave.number_of_days_display - different_days
					elif leave.request_date_to > self.date_to:
						different_days = (fields.Date.from_string(leave.request_date_to)-fields.Date.from_string(self.date_to)).days
						days_leave += leave.number_of_days_display - different_days
			if days_leave > 20:
				days_leave = 22

			#=============== get employee permissions 
			hours_permissions = 0
			permissions = self.env['permission.request'].search([('employee_id','=',employee.id),('permission_date','>=',self.date_from),('permission_date','<=',self.date_to),('state','=','career')])
			for permission in permissions:
				hours_permissions += permission.hours_number_permission
				

			#=============== get employee trainings 
			trainings = self.env['program.execution'].search(['|','&',('date_from','>=',self.date_from),('date_from','<=',self.date_to),'&',('date_to','>=',self.date_from),('date_to','<=',self.date_to),('state','=','accounting')])

			training_hours = 0.00
			for training in trainings:
				different_days = (fields.Date.from_string(training.date_to)-fields.Date.from_string(training.date_from)).days
				for line in training.line_ids:
					if line.employee_id == employee:
						for train in range(different_days+1):
							training_hours +=  training.hour_to - training.hour_from

			#=============== get employee missions 
			missions = self.env['missions.assigned'].search(['|','&',('date_from','>=',self.date_from),('date_from','<=',self.date_to),'&',('date_to','>=',self.date_from),('date_to','<=',self.date_to)])
			days_mission = 0
			for mission in missions:
				different_days = (fields.Date.from_string(mission.date_to)-fields.Date.from_string(mission.date_from)).days
				if mission.team_leader == employee:
					for miss in range(different_days+1):
						days_mission += 1
				else:
					for line in mission.line_ids:
						if line.employee_id == employee:
							for miss in range(different_days+1):
								days_mission += 1

			#technichal performane
			technical_performance_ratio = 0.00
			technical = self.env['technical.performance'].search(['&',('employee_id','=',employee.id),'|','&',('date_from','>=',self.date_from),('date_from','<=',self.date_to),'&',('date_to','>=',self.date_from),('date_to','<=',self.date_to),('state','=','confirm')], limit=1)

			if technical:
				technical_performance_ratio = technical.total_evaluation

				
				
			lines_list.append({'employee_id':employee.id,
				'normative':self.normative,
				'hours_allowed':self.hours_allowed,
				'hours_leave':days_leave*8,
				'hours_permissions':hours_permissions,
				'trainings':training_hours,
				'missions':days_mission*8,
				'technical_performance_ratio':technical_performance_ratio,
				})
			

		self.line_ids = False
		self.line_ids = lines_list
		for line in self.line_ids:
			line._get_details()


class monthlyPerformance(models.Model):
	_name = 'monthly.performance.line'

	employee_id = fields.Many2one('hr.employee', required=True,readonly=True)
	unit_id = fields.Many2one('hr.department', readonly=True, related='employee_id.unit_id')
	job_title_id=fields.Many2one("job.title", readonly=True, related='employee_id.job_title_id')
	normative = fields.Integer(readonly=True, )
	hours_allowed = fields.Integer(readonly=True)
	hours_leave = fields.Integer(readonly=True)
	hours_permissions = fields.Integer(readonly=True)
	trainings = fields.Integer(readonly=True)
	missions = fields.Integer(readonly=True)
	total_hours = fields.Float(readonly=True, )
	system_attend = fields.Integer()
	attendance_hours = fields.Float(readonly=True, )
	absence_ratio = fields.Float(readonly=True,digits=(6,2) )
	technical_performance_ratio = fields.Integer()
	discount_percentage = fields.Float(readonly=True, digits=(6,2) )
	total_ratio = fields.Float(readonly=True, digits=(6,2))
	notes = fields.Char()
	line_id = fields.Many2one('monthly.performance')

	@api.onchange('normative','hours_allowed','hours_leave','hours_permissions','trainings','missions','system_attend','technical_performance_ratio')
	def _get_details(self):
		self.total_hours = self.hours_allowed + self.hours_leave + self.hours_permissions + self.trainings + self.missions
		self.attendance_hours = self.total_hours + self.system_attend
		self.absence_ratio = ((self.normative - self.attendance_hours)/(self.normative))*35
		self.discount_percentage =  self.absence_ratio + (65-self.technical_performance_ratio)
		self.total_ratio = 100 - self.discount_percentage


class indicatorsPerformance(models.Model):
	_name='indicators.performance'
	_inherit = ['mail.thread','mail.activity.mixin',]
	name=fields.Char(required=True,track_visibility="onchange")
	standard = fields.Many2one('evaluation.criteria',track_visibility="onchange")
	percentage = fields.Float(required=True,track_visibility="onchange")
	indicator_type= fields.Selection([
		('sub','Sub'),
		('main','Main'),
		] , default='main',track_visibility="onchange")
	indicator_text = fields.Text(track_visibility="onchange")
	line_ids = fields.One2many("sub.indicators","sub_indicators_id")

	@api.onchange('line_ids')
	def _onchange_line_ids(self):
		total = 0
		for line in self.line_ids:
			total += line.percentage
		if total > self.percentage:
			raise Warning(_('The total percentages of sub-activities cannot exceed the percentage of the main activity'))

	        

class subIndicators(models.Model):
	_name='sub.indicators'
	indicator_name = fields.Many2one('indicators.performance',domain=[('indicator_type','=','sub'), ], )
	standard = fields.Many2one('evaluation.criteria', related='indicator_name.standard', readonly=True, )
	percentage = fields.Float(related='indicator_name.percentage', readonly=True, )
	indicator_text = fields.Text(related='indicator_name.indicator_text', readonly=True, )
	sub_indicators_id = fields.Many2one('indicators.performance', readonly=True, )

class technicalPerformance(models.Model):
	_name= 'technical.performance'
	_inherit = ['mail.thread','mail.activity.mixin',]
	_order = 'id desc'

	name=fields.Char(readonly=True,track_visibility="onchange")
	employee_id = fields.Many2one('hr.employee', required=True,track_visibility="onchange")
	employee_no = fields.Integer()
	unit_id = fields.Many2one('hr.department', readonly=True, related='employee_id.unit_id',track_visibility="onchange")
	department_id = fields.Many2one('hr.department', readonly=True, related='employee_id.department_id',track_visibility="onchange")
	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)), required=True,track_visibility="onchange")
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True,track_visibility="onchange")
	total_evaluation = fields.Float(compute='_compute_total_evaluation',track_visibility="onchange")
	activities_line_ids = fields.One2many("activities.activities","performance_id")
	evaluation_line_ids =fields.One2many("technical.evaluation.line","performance_id")
	state = fields.Selection([
		('draft', 'Draft'),
		('direct_manger', 'Direct Manger'),
		('dep_manger','Department Manger Confirm'),
		('confirm','Confirmed')
		],default='draft',track_visibility="onchange")

	def unlink(self):
		if self.state != 'draft':
			raise Warning(_('Deletion is only possible if state is draft'))
		return models.Model.unlink(self)

	def action_send(self):
		if not self.activities_line_ids:
			raise Warning(_('Please enter activities details'))
		self.write({'state':'direct_manger'})

	def action_direct_manger(self):
		self.write({'state':'dep_manger'})

	def action_dep_manger(self):
		self.write({'state':'confirm'})

	def action_return(self):
		self.write({'state':'draft'})

	def action_return1(self):
		self.write({'state':'direct_manger'})

	def action_return_career_path(self):
		self.write({'state':'draft'})



	@api.model
	def create(self, vals):
		res = super(technicalPerformance, self).create(vals)
		month = datetime.strftime(datetime.strptime(str(date.today()), "%Y-%m-%d"), "%m")
		year = datetime.strftime(datetime.strptime(str(date.today()), "%Y-%m-%d"), "%Y")
		res.name = res.employee_id.name +' / '+month+'-'+year
		indicators = self.env['indicators.performance'].search([('indicator_type','=','main')])
		line_list = []
		if not indicators:
			raise Warning(_('Please contact the performance department to prepare performance indicators for the system'))
		for indicator in indicators:
			line_list.append({'activity':indicator,
				'weight':indicator.percentage,
				'performance_id':res.id,})
		res.evaluation_line_ids = line_list
		return res

	@api.onchange('date_from','date_to')
	def _date_constratin(self):
		if self.date_from > self.date_to and self.date_from and self.date_to:
			raise Warning(_('start date cannot be greater than end date'))

	@api.onchange('activities_line_ids')
	def _onchange_activities_line_ids(self):
		activity_list = []
		for activity_line in self.activities_line_ids: 
			if activity_line.activity not in activity_list:
				activity_list.append(activity_line.activity)
		for activity in activity_list:
			total_weight = 0.00
			for activity_line in self.activities_line_ids: 
				if activity_line.activity.id == activity.id:
					total_weight += activity_line.weight
			if total_weight > activity.percentage:
				raise Warning(_('activitys weights cannot exceed the main activity weight'))


		for evaluation_line in self.evaluation_line_ids: 
			total = 0.00
			for activity_line in self.activities_line_ids:
				if activity_line.activity == evaluation_line.activity:
					total += activity_line.evaluation
			evaluation_line.evaluation = total



	@api.onchange('evaluation_line_ids')
	def _compute_total_evaluation(self):
		for rec in self:
			total = 0.00
			for line in rec.evaluation_line_ids:
				total += line.evaluation
			rec.total_evaluation = total

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


class Evaluation(models.Model):
	_name = 'technical.evaluation.line'
	name = fields.Char(readonly=True, string="Numer")
	activity = fields.Many2one('indicators.performance',readonly=True ,domain=[('indicator_type','=','main'), ], )
	weight = fields.Float(related='activity.percentage',string="Activity weight" ,readonly=True, )
	evaluation = fields.Float()
	notes = fields.Text()
	performance_id = fields.Many2one("technical.performance", ondelete='cascade')
	attachment = fields.Many2many('ir.attachment' ,  attachment=True )

	@api.onchange('evaluation')
	def _onchange_evaluation(self):
		for rec in self:
			if rec.evaluation > rec.weight:
				raise Warning(_('Evaluation cannot exceed the activitys weight'))
   
	
class Activities(models.Model):
	_name='activities.activities'
	
	activity = fields.Many2one('indicators.performance', domain=[('indicator_type','=','main'), ], )
	main_activity = fields.Char(required=True,)
	sub_activity= fields.Char(required=True,)
	weight = fields.Float(string="Activity weight" )
	date_from = fields.Date()
	date_to = fields.Date()
	evaluation = fields.Float()
	execution_date=fields.Date()
	notes = fields.Text()
	performance_id = fields.Many2one("technical.performance", ondelete='cascade')
	attachment = fields.Many2many('ir.attachment' ,  attachment=True )

	@api.onchange('evaluation')
	def _onchange_evaluation(self):
		for rec in self:
			if rec.evaluation > rec.weight:
				raise Warning(_('Evaluation cannot exceed the activitys weight'))

	# @api.onchange('weight')
	# def _onchange_weight(self):
	# 	# for rec in self:
	# 	total_weight = 0.00
	# 	print('***********')
	# 	print('***********')
	# 	print('self.performance_id.id ',self.performance_id.id)
	# 	# for line in rec.performance_id.activities_line_ids:
	# 	for line in self.env['activities.activities'].search([('performance_id','=',self.performance_id.id)]):
	# 		total_weight += line.weight
	# 		print('line.id ',line.id,'  line.weight ',line.weight)
	# 	print('***********')
	# 	print('***********')
	# 	print('total_weight ',total_weight)
	# 	print('***********')
	# 	print('***********')
	# 	total_weight += self.weight
	# 	print('total_weight ',total_weight)
	# 	print('self.activity.percentage  ',self.activity.percentage)
		
	# 	if total_weight > self.activity.percentage:
	# 		raise Warning(_('activitys weights cannot exceed the activity weight'))

class evaluatingMerits(models.Model):
	_name = 'evaluating.merits'
	_inherit = ['mail.thread','mail.activity.mixin']
	_description = 'Evaluating merits'

	name = fields.Char('Numer',readonly=True, )
	employee_no = fields.Integer('Employee No')
	employee_id = fields.Many2one('hr.employee', required=True)
	department_id =fields.Many2one('hr.department',readonly=True,related='employee_id.department_id')
	job_id = fields.Many2one('hr.function',related='employee_id.functional_id')
	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)), required=True,)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True,)
	line_ids = fields.One2many("evaluation.evaluation","evaluation_line_id")
	state = fields.Selection([('draft', 'Draft'),('employee_notification','Employee notification'),('sub_manager_confirm', 'Sub-Manager Confirm'),('General_department_confirm','General department Confirm'),('career','Career')],"States", default="draft")

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('sequence.evaluating.merits')
		return super(evaluatingMerits, self).create(vals)


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
	
	@api.onchange('job_id')
	def _onchange_job_id(self):
		line_list = []
		for line in self.job_id.competencie_line_ids:
			line_list.append({'merit':line.competencie_id.id,
				'required_level':line.required_degree,
				})
		self.line_ids = False
		self.line_ids = line_list

	@api.multi
	def employee_notification(self):
		#notify employee
		if self.employee_id.user_id:
			self.env['mail.activity'].create({
				'res_name': _('Evaluating merits'),
	            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
	            'date_deadline':date.today(),
	            'summary': 'Evaluating merits',
	            'user_id': self.employee_id.user_id.id,
	            'res_id': self.id,
	            'res_model_id': self.env.ref('kamil_hr_career.model_evaluating_merits').id,
	        })
		self.write({'state':'employee_notification'})

	@api.multi
	def employee_confirm(self):
		self.write({'state':'employee_confirm'})

	@api.multi
	def sub_manager_confirm(self):
		self.write({'state':'sub_manager_confirm'})

	@api.multi
	def General_department_confirm(self):
		self.write({'state':'General_department_confirm'})

	@api.multi
	def career(self):
		self.write({'state':'career'})



	@api.onchange('date_from','date_to')
	def _date_constratin(self):
		if self.date_from and self.date_to and self.date_from > self.date_to:
			raise Warning(_('start date cannot be greater than end date')) 





class Evaluation(models.Model):
	_name = 'evaluation.evaluation'
	merit = fields.Many2one('competencie.model')
	required_level = fields.Float(readonly=True, )
	employee_level = fields.Float(required=True, )
	gap = fields.Boolean(readonly=True,)
	gap_percentage = fields.Float(readonly=True,)
	evaluation_line_id = fields.Many2one("evaluating.merits")


	@api.onchange('employee_level')
	def _onchange_employee_level(self):
		for rec in self:
			if rec.employee_level and rec.required_level:
				gap_percentage = 100 -((rec.employee_level/rec.required_level)*100)
				if gap_percentage > 0:
					rec.gap_percentage = gap_percentage
					rec.gap = True

class PermissionType(models.Model):
	_name = 'permission.type'
	name = fields.Char(required=True)



class Permission(models.Model):
	_name = 'permission.request'
	_inherit = ['mail.thread','mail.activity.mixin',]
	_rec_name = 'employee_id'
	employee_no = fields.Integer('Employee No',track_visibility="onchange")
	employee_id = fields.Many2one('hr.employee', required=True, track_visibility="onchange")
	department_id =fields.Many2one('hr.department',readonly=True,related='employee_id.department_id')
	permission_type = fields.Many2one('permission.type', track_visibility="onchange" ,required=True,)
	permission_date = fields.Date(default=lambda self: fields.Date.today(), readonly=True, )
	hours_form = fields.Float()
	hours_to = fields.Float()
	hours_number_permission = fields.Integer(compute='_compute_total_hours',string="Total Hours")
	permission_reason = fields.Html(track_visibility="onchange")
	attachment = fields.Binary()
	state = fields.Selection([('draft','Draft'),('head_department_confirm','Head Department Confirm'),('branch_manager_confirm', 'Branch Manager Confirm'),('director_public_confirm', 'Director Public Confirm'),('hr','HR')],"States", default="draft",track_visibility="onchange")


	@api.multi
	def head_department_confirm(self):
		self.write({'state':'head_department_confirm'})

	@api.multi
	def branch_manager_confirm(self):
		self.write({'state':'branch_manager_confirm'})

	
	@api.multi
	def director_public_confirm(self):
		self.write({'state':'director_public_confirm'})

	@api.multi
	def hr(self):
		self.write({'state':'hr'})

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

	@api.depends('hours_form','hours_to')
	def _compute_total_hours(self):
		for rec in self:
			rec.hours_number_permission = rec.hours_to - rec.hours_form

			return True

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise Warning(_('Permission cannot be deleted in a case other than draft'))
		return models.Model.unlink(self)



