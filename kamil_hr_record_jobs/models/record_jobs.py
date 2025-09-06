# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import Warning


class RecordJob(models.Model):
	_name="record.jobs"
	name=fields.Char("Record Job",required=True,)
	line_ids=fields.One2many("record.jobs.line","record_jobs_id","Details", copy=True)
	functions_count = fields.Integer(compute='functions')
	record_type = fields.Selection([('record_inside','Record Inside'),('record_outside','Record Outside')], required=True,)

	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('archived','Archived')], default='draft')


	@api.multi
	def functions(self):
		functions_obj = self.env['record.jobs.line'].search([('record_jobs_id','=',self.id)])
		functions_list = []
		for function in functions_obj:
			functions_list.append(function.id)
		self.functions_count = len(functions_list)
		return {
			'name': _('Functions'),
			'view_type': 'form',
			'view_mode': 'tree',
			'res_model': 'record.jobs.line',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', functions_list)],
			}

	def do_confirm(self):
		if not self.line_ids:
			raise Warning(_('Please enter functions details'))
		if self.env['record.jobs'].search([('state','=','confirmed')]):
			raise Warning(_('Sorry! you can\'t confirmed two jobs records, please archived other jobs records to confirmed this'))
		self.state = 'confirmed'

	def do_archived(self):
		self.name = self.name + ' "مؤرشف" '
		self.state = 'archived'


class RecordJobLine(models.Model):
	_name="record.jobs.line"
	_rec_name = 'job_number'

	job_number = fields.Char("Job Number", required=True,)
	number = fields.Char("Number")
	job = fields.Many2one("functional.record","Function", required=True,)
	section = fields.Char("Section")
	employee_id = fields.Many2one("hr.employee","Employee Name")
	employee_degree = fields.Many2one("functional.degree",string="Employee degree", required=True,)
	date = fields.Text("Date")
	current_salary = fields.Integer("Current Salary")
	notes = fields.Text("Notes")
	record_jobs_id = fields.Many2one("record.jobs")

	@api.onchange('employee_id','employee_degree')
	def _onchange_emp_date(self):
		salary_structure = self.env['salary.structure'].search([('is_active','=',True)],limit=1)
		if self.employee_id:
			date_str = ""
			if self.employee_id.birthday:
				date_str += "تاريخ الميلاد="+","+str(self.employee_id.birthday)
			if self.employee_id.appoiontment_date:
				date_str += "تاريخ التعيين="+","+str(self.employee_id.appoiontment_date)
			if self.employee_id.entry_date:
				date_str += "تاريخ الالتحاق="+","+str(self.employee_id.entry_date)

			self.date = date_str
			self.employee_degree = self.employee_id.degree_id
		for line in salary_structure.line_ids:
			if line.degree_id.id == self.employee_id.degree_id.id:
				if self.employee_id.bonus== 'first_bonus':
					self.current_salary = line.primary_category
				if self.employee_id.bonus== 'second_bonus':
					self.current_salary = line.second_bonus
				if self.employee_id.bonus== 'third_bonus':
					self.current_salary = line.third_bonus
				if self.employee_id.bonus== 'fourth_bonus':
					self.current_salary = line.fourth_bonus 
				if self.employee_id.bonus== 'fifth_bonus':
					self.current_salary = line.fifth_bonus
				if self.employee_id.bonus== 'sixth_bonus':
					self.current_salary = line.sixth_bonus
				if self.employee_id.bonus== 'seventh_bonus':
					self.current_salary = line.seventh_bonus
				if self.employee_id.bonus== 'eighth_bonus':
					self.current_salary = line.eighth_bonus
				if self.employee_id.bonus== 'ninth_bonus':
					self.current_salary = line.ninth_bonus
		# self.date = self.employee_id.appoiontment_date
			# self.degree_id = self.employee_id.degree_id
			# self.current_salary = self.employee_id

		# degree_list = []
		# for sal in Salary:
		# 	if sal.employee_degree not in degree_list:
		# 		degree_list.append(sal.employee_degree)

		# for sal in Salary:
		# 	if sal.employee_degree == Salary.employee_degree and line.sal == job:
		# 	self.current_salary = sal.primary_category
			# print("\n")
			# self.date =self.employee_id.appoiontment_date