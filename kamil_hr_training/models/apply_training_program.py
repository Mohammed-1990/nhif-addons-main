from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class applyTraining(models.Model):
	_name='apply.training'
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char( readonly=True)
	employee_no = fields.Char(string="Employee Number",track_visibility="onchange")
	employee_id=fields.Many2one('hr.employee', required=True,track_visibility="onchange")
	name_eng = fields.Char(required=True,track_visibility="onchange")
	department_id = fields.Many2one('hr.department',readonly=True)
	mobile_phone=fields.Char(track_visibility="onchange")
	work_email =fields.Char(track_visibility="onchange")
	marital=fields.Selection([('single','SINHLE'),('married','Married'),('have_kids','Married  and have kids'),('widowre','Widowre'),('divorced','Divorced')],track_visibility="onchange")
	age=fields.Integer(readonly=True)
	university=fields.Many2one('university.model')
	university_id=fields.Many2one('university.model', readonly=True, )
	graduation_date=fields.Date()
	language_level=fields.Char()
	degree=fields.Char()
	appoiontment_type=fields.Many2one('appointment.type',readonly=True, )
	appoiontment_date=fields.Date(readonly=True)
	functional_id=fields.Many2one("hr.function",readonly=True)
	date_from=fields.Date()
	date_to=fields.Date()
	specialization=fields.Many2one('university.specialization',readonly=True)
	special=fields.Char()
	the_field=fields.Char()
	training_program=fields.Many2one("launch.training", required=True,domain=[('state','=','submission_opened'), ])
	doc_line_id = fields.One2many("document.training","doc_id")
	is_open_training_program = fields.Boolean(default=False)
	approve_program_terms = fields.Boolean(default=False)
	state = fields.Selection([
		('draft','Draft'),
		('submitted','Training Department'),
		('approved','Approved'),
		('rejected','Rejected')], string="Status" ,default='draft',track_visibility="onchange" )

	def unlink(self):
		if self.state not in ['draft','rejected']:
			raise Warning(_('Deletion is only possible if state is draft or rejected'))
		return models.Model.unlink(self)

	def do_send(self):
		if self.training_program.age < self.age:
			raise Warning(_('Maximum age to apply for this program %s'%(self.training_program.age)))
		if self.is_open_training_program == False:
			raise Warning(_('Please see the details of the training program'))
		if self.approve_program_terms == False:
			raise Warning(_('Please agree to the terms of the training program'))
		for doc in self.doc_line_id:
			if not doc.doc:
				raise Warning(_('All required documents must be submitted'))
		self.state = 'submitted'

	@api.model
	def create(self,vals):
		res = super(applyTraining,self).create(vals)
		if res.training_program and res.employee_id:
			res.name = res.training_program.name + ' - ' + res.employee_id.name
		return res

	@api.onchange('training_program','employee_id')
	def onchange_employee(self):
		if self.training_program and self.employee_id:
			self.name = self.training_program.name + ' - ' + self.employee_id.name


	def do_approve(self):
		evaluation = self.env['evaluation.candidates'].create({'training_program':self.training_program.id,
			'employee_id':self.employee_id.id,
			'age':self.age})
		lines = []
		for criteria in self.env['criteria.evaluating'].search([]):
			lines.append({'standard':criteria.id,
				'evaluation_id':evaluation.id,})
		evaluation.line_ids = lines
		self.state = 'approved'

	def do_reject(self):
		self.state = 'rejected'


	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.department_id = self.employee_id.department_id
			self.employee_no = self.employee_id.number
			self.mobile_phone = self.employee_id.mobile_phone
			self.marital = self.employee_id.marital
			self.university = self.employee_id.university.id
			self.appoiontment_type = self.employee_id.appoiontment_type
			self.appoiontment_date = self.employee_id.appoiontment_date
			self.functional_id = self.employee_id.functional_id
			self.age = relativedelta(fields.Date.from_string(fields.Date.today()),fields.Date.from_string(self.employee_id.birthday)).years 
			self.work_email = self.employee_id.work_email
			self.name_eng = self.employee_id.name_eng
			self.graduation_date = self.employee_id.graduation_date

			
	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = False
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)],limit=1).id


	@api.onchange('training_program')
	def _onchange_training_program(self):
		if self.training_program:
			self.university_id = self.training_program.university_id
			self.specialization = self.training_program.specialization
			documents = []
			for doc in self.training_program.required_doc_ids:
				documents.append({'doc_name':doc.document_id,})
			self.doc_line_id = documents

	@api.multi
	def open_training_program(self):
		self.is_open_training_program = True
		return {
			'name': _('Training Program'),
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'launch.training',
			'res_id' : self.training_program.id,
			'domain': [('id', '=', self.training_program.id)],
			'context': {'default_id': self.training_program.id},
			}	

	def do_approve_program_terms(self):
		self.approve_program_terms = True



class document_training(models.Model):
	_name = "document.training"
	doc_name = fields.Many2one('document.document',string="Document Name" , required=True)
	doc = fields.Binary("Document" , )
	doc_id = fields.Many2one("apply.training")