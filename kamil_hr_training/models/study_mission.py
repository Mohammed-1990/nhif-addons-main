from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime



class study_mission(models.Model):
	_name='study.mission'
	_inherit = ['mail.thread','mail.activity.mixin']
	
	name = fields.Char(readonly=True)
	training_program =fields.Many2one('launch.training',required=True, track_visibility="onchange")
	employee_no = fields.Integer(string="Employee Number",track_visibility="onchange")
	employee_id =fields.Many2one('hr.employee', required=True,track_visibility="onchange")
	department_id = fields.Many2one('hr.department',readonly=True,track_visibility="onchange")
	functional_id=fields.Many2one("hr.function",readonly=True,track_visibility="onchange")
	children_number=fields.Integer(string="children Number",track_visibility="onchange")
	escorts=fields.Selection([
		('no','no one'),
		('wife','Wife only'),
		('wife_children','Wife and children'),

		] , default='no', track_visibility="onchange")
	date_from = fields.Date(track_visibility="onchange")
	date_to = fields.Date(track_visibility="onchange")
	specialization = fields.Many2one('university.specialization', readonly=True, track_visibility="onchange")
	university_id = fields.Many2one('university.model',readonly=True, track_visibility="onchange")
	country =fields.Many2one("res.country",readonly=True, track_visibility="onchange")
	doc_line_id = fields.One2many("mission.document","doc_id")
	expenses_count = fields.Integer(compute='study_expenses')
	extension_count = fields.Integer(compute='study_extension')
	interrupt_count = fields.Integer(compute='study_interrupt')
	notes = fields.Html(track_visibility="onchange")
	state = fields.Selection([('draft', 'Draft'),
		('submitted', 'Confirm'),
		('gm_confirm','G Manager Confirm'),
		('university_apply','Apply to the University'),
		('institution_approval', 'Approval of the educational institution'),
		('ntc_approval', 'National Training Council Approval'),
		('legal_contract','Legal Contract'),
		('confirmed','Confirmed'),
		('rejected','Rejected'),
		('interrupted','Interrupted'),
		('canceled','Canceled')],"States", default="draft",track_visibility="onchange")

	def unlink(self):
		if self.state not in ['draft','rejected']:
			raise Warning(_('Deletion is only possible if state is draft or rejected'))
		return models.Model.unlink(self)

	@api.onchange('employee_id')
	def onchange_employee_id(self):
		if self.employee_id:
			self.employee_no = False
			self.employee_no = self.employee_id.number
			self.department_id = self.employee_id.department_id
			self.functional_id = self.employee_id.functional_id



	@api.onchange('date_from','date_to')
	@api.multi
	def _date(self):
		if self.date_to and self.date_from:
			if self.date_from > self.date_to:
				raise Warning(_("Sorry! The start date cannot be greater than the end date"))

	

	@api.onchange('training_program')
	def onchange_training_program(self):
		if self.training_program:
			self.country = self.training_program.country
			self.university_id = self.training_program.university_id
			self.specialization = self.training_program.specialization
			self.date_from = self.training_program.date_from
			self.date_to = self.training_program.date_to

	        
	@api.multi
	def study_expenses(self):
		study_expenses_obj = self.env['training.expenses'].search([('study_mission','=',self.id)])
		study_expenses_list = []
		for expense in study_expenses_obj:
			study_expenses_list.append(expense.id)
		self.expenses_count = len(study_expenses_list)
		return {
			'name': _('Study Expenses'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'training.expenses',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', study_expenses_list)],
			'context':{'default_study_mission':self.id,'default_employee_id':self.employee_id.id,}
			}

	@api.multi
	def study_extension(self):
		study_extension_obj = self.env['study.training.extension'].search([('study_id','=',self.id)])
		study_extension_list = []
		for extension in study_extension_obj:
			study_extension_list.append(extension.id)
		self.extension_count = len(study_extension_list)
		return {
			'name': _('Study Extension'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'study.training.extension',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', study_extension_list)],
			'context':{'default_study_id':self.id,'default_employee_id':self.employee_id.id,}
			}

	@api.multi
	def study_interrupt(self):
		study_interrupt_obj = self.env['study.training.interrupt'].search([('study_id','=',self.id)])
		study_interrupt_list = []
		for interrupt in study_interrupt_obj:
			study_interrupt_list.append(interrupt.id)
		self.interrupt_count = len(study_interrupt_list)
		return {
			'name': _('Study Interrupt'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'study.training.interrupt',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', study_interrupt_list)],
			'context':{'default_study_id':self.id,'default_employee_id':self.employee_id.id,}
			}

	@api.multi
	def open_contract(self):
		print('******')
		print('******')
		print('******')
		print('******')
		print('******')
		print('******')
		print(self.env['kamil.contracts.contract'].search([('study_mission','=',self.id)],limit=1).id)
		print('******')
		print('******')
		print('******')
		print('******')
		print('******')
		print('******')
		print('******')
		print('******')
		return {
			'name': _('Contact'),
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'kamil.contracts.contract',
			'res_id' : self.env['kamil.contracts.contract'].search([('study_mission','=',self.id)],limit=1).id,
			'context': {'default_create':False},
			}	


	@api.multi
	def do_submit(self):
		self.write({'state':'submitted'})
		
	@api.multi
	def gm_confirm(self):
		self.write({'state':'gm_confirm'})
	
	@api.multi
	def university_apply(self):
		self.write({'state':'university_apply'})


	@api.multi
	def institution_approval(self):
		self.write({'state':'institution_approval'})

	@api.multi
	def ntc_approval(self):
		self.write({'state':'ntc_approval'})

	@api.multi
	def create_contract(self):
		self.write({'state':'legal_contract'})
		return {
			'name': _('Contact'),
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'kamil.contracts.contract',
			'context': {
				'default_name':self.name,
				'default_contract_type':'Training',
				'default_ntfs':self.env.user.company_id.id,
				'default_contract_start_date':self.date_from,
				'default_contract_end_date':self.date_to,
				'default_second_party_ch':self.employee_id.partner_id.id,
				'default_second_party_name':self.employee_id.partner_id.id,
				'default_study_mission':self.id,
				},
			}


	@api.multi
	def action_reject(self):
		self.state = 'rejected'

	@api.multi
	def action_reject1(self):
		self.state = 'rejected'


	@api.model
	def create(self, values):
		res = super(study_mission, self).create(values)
		res.name = res.training_program.name + ' - ' + res.employee_id.name
		return res


class mission_document(models.Model):
	_name = "mission.document"
	document_id = fields.Many2one('document.document', required=True, string="Document name")
	doc = fields.Binary("Document" , required=True)
	doc_id = fields.Many2one("study.mission")
	