# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class hrPromotions(models.Model):
	_name="hr.promotions"
	_inherit = ['mail.thread','mail.activity.mixin',]
	_description = "Employee Promotions"
	
	name = fields.Char(readonly=True, string="Number")
	employee_no = fields.Integer(string='Employee No', help='Can search by employee number', )
	employee_id = fields.Many2one('hr.employee',string='Employee Name', required=True,)
	department_id = fields.Many2one('hr.department',string='Employee Department', related='employee_id.department_id')
	job_title = fields.Many2one('job.title',string='Job Title', related='employee_id.job_title_id')
	promotion_date = fields.Date(string='Promotion Date', required=True,track_visibility="onchange")
	exection_date = fields.Date(string='Exection Date', required=True,track_visibility="onchange")
	current_degree_id = fields.Many2one('functional.degree', readonly=True, track_visibility="onchange")
	new_degree_id = fields.Many2one('functional.degree', required=True,track_visibility="onchange")
	current_bonus = fields.Selection([
		('first_bonus','First Bonus'),
		('second_bonus','Second Bonus'),
		('third_bonus','Third Bonus'),
		('fourth_bonus','Fourth Bonus'),
		('fifth_bonus','Fifth Bonus'),
		('sixth_bonus','Sixth Bonus'),
		('seventh_bonus','Seventh Bonus'),
		('eighth_bonus','Eighth Bonus'),
		('ninth_bonus','Ninth Bonus')
		],readonly=True,)
	new_bonus = fields.Selection([
		('first_bonus','First Bonus'),
		('second_bonus','Second Bonus'),
		('third_bonus','Third Bonus'),
		('fourth_bonus','Fourth Bonus'),
		('fifth_bonus','Fifth Bonus'),
		('sixth_bonus','Sixth Bonus'),
		('seventh_bonus','Seventh Bonus'),
		('eighth_bonus','Eighth Bonus'),
		('ninth_bonus','Ninth Bonus')
		],required=True,default='first_bonus',track_visibility="onchange")
	
	job_no = fields.Many2one('record.jobs.line',required=True, string="Job number in the jobs record", track_visibility="onchange")
	section = fields.Char("Section",related='job_no.section')
	employee_degree = fields.Many2one("functional.degree",string="Employee degree",related='job_no.employee_degree')


	state = fields.Selection([
		('draft','Draft'),
		('personnel','Personnel'),
		('sub_manager','Human Resources Sub-Manager'),
		('general_directorate','General Directorate of Human Resources'),
		('approved','Approved')], string="Status" ,default='draft',track_visibility="onchange" )
	notes = fields.Html(track_visibility="onchange")

	def do_submit(self):
		self.state = 'personnel'


	def do_personnel_confirm(self):
		self.state = 'sub_manager'
	
	def do_sm_confirm(self):
		# sub manager confirm
		self.state = 'general_directorate'
	
	def do_gd_confirm(self):
		# general directorate confirm
		''' -change state to confirmed
			-notify employee 
			-change employee degree to new degree'''

		self.employee_id.degree_id = self.new_degree_id
		self.employee_id.last_promotion_date = self.promotion_date
		self.employee_id.last_bonus_date = self.promotion_date
		self.employee_id.bonus = self.new_bonus
		self.employee_id.update_contract()

		for line in self.env['record.jobs'].search([('state','=','confirmed')],limit=1).line_ids:
			if line.employee_id == self.employee_id:
				line.employee_id = False
			if line.job_number == self.job_no.job_number:
				line.employee_id = self.employee_id.id
			
		#notify employee
		if self.employee_id.user_id:
			self.env['mail.activity'].create({
				'res_name': 'Employee Promotion',
	            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
	            'date_deadline':self.exection_date,
	            'summary': 'تمت ترقيتك في تاريخ ' + str(self.exection_date),
	            'user_id': self.employee_id.user_id.id,
	            'res_id': self.id,
	            'res_model_id': self.env.ref('kamil_hr_promotions.model_hr_promotions').id,
	        })
		self.state = 'approved'

	def do_return(self):
		if self.state == 'personnel':
			self.state = 'draft'
		if self.state == 'sub_manager':
			self.state = 'personnel'
		if self.state == 'general_directorate':
			self.state = 'sub_manager'
	@api.model 
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('sequence.hr.promotion')
		
		return super(hrPromotions, self).create(vals)

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
			self.current_degree_id = self.employee_id.degree_id
			self.current_bonus = self.employee_id.bonus

	@api.onchange('new_degree_id')
	def _get_job_no(self):
		ids_list = []
		if self.new_degree_id:
			record_job = self.env['record.jobs'].search([('state','=','confirmed')],limit=1)
			for line in record_job.line_ids:
				if not line.employee_id and line.employee_degree == self.new_degree_id: 
					ids_list.append(line.id)
			return {'domain':{'job_no':[('id','in',ids_list),('record_jobs_id','=',record_job.id)]}}




