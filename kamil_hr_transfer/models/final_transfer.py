# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class finalTransfer(models.Model):
	_name = "final.transfer"
	_inherit = ['mail.thread','mail.activity.mixin',]
	
	name = fields.Char(required=True ,track_visibility="onchange")
	job = fields.Char(required=True , track_visibility="onchange")
	enterprise = fields.Char(required=True , track_visibility="onchange")
	date = fields.Date(default=lambda self: fields.Date.today())
	job_id = fields.Many2one('hr.function',required=True ,track_visibility="onchange")
	unit_id = fields.Many2one('hr.department',domain=[('type','=','general_administration'), ],)
	branch_id = fields.Many2one("res.company",track_visibility="onchange", required=True,)
	department_id = fields.Many2one('hr.department',domain=[('type','=','department'), ])
	category_fun_id = fields.Many2one('functional.category',track_visibility="onchange")
	job_title_id = fields.Many2one('job.title',track_visibility="onchange")
	degree_id = fields.Many2one('functional.degree',track_visibility="onchange")
	date_from = fields.Date()
	date_to = fields.Date()
	appoiontment_type = fields.Many2one('appointment.type',)
	job_no = fields.Many2one('record.jobs.line', string="Job number in the jobs record")
	
	line_ids = fields.One2many('final.transfer.line','final_transfer_id','Extension')

	_sql_constraints = [('movements_name_uniqe', 'unique (name)','Sorry! you can not create for the same name')]


	state = fields.Selection([
		('draft','Draft'),
		('submitted','Sumbitted'),
		('confirmed','Confirmed'),
		],default='draft',)


	@api.onchange('branch_id')
	@api.multi
	def get_unit_department(self):
		branchs = self.env['hr.department'].search([])
		#('employee_id','=',self.employee_id.id)
		if self.branch_id:
			for branch in branchs:
				return{
					'domain':{
						'unit_id':[('company_id','=',self.branch_id.id)]
					}
				}

	@api.onchange('unit_id')
	@api.multi
	def get_unit_department(self):
		branchs = self.env['hr.department'].search([])
		if self.unit_id:
			for branch in branchs:
				return{
				       'domain':{
				       		'department_id':[('parent_id','=',self.unit_id.id)]
				       }
				}
	




	def do_submit(self):
		# change state to sumbitted
		self.state = 'submitted'

	def do_confirm(self):
		# change state to confirmed

		self.env['hr.employee'].create({
			'name':self.name,
			'company_id':self.branch_id.id,
			'department_id':self.department_id.id,
			'category_id':self.category_fun_id.id,
			'job_title_id':self.job_title_id.id,
			'degree_id':self.degree_id.id,
			'functional_id':self.job_id.id,
			'appoiontment_type': self.appoiontment_type.id,
			})

		self.state = 'confirmed'


class finalTransferLine(models.Model):
	_name = 'final.transfer.line'

	extension_date = fields.Date()
	extension_end_date = fields.Date(required=True,)
	document = fields.Binary(required=True,)
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')], default='draft')
	final_transfer_id = fields.Many2one('final.transfer')
	
	def do_confirm(self):
		# change state to confirmed

		self.env['hr.employee'].search([('name','=',self.final_transfer_id.name)],limit=1).termination_date = self.extension_end_date
		self.state = 'confirmed'
