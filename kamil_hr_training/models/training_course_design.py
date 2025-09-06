from odoo import models, fields, api,_
from odoo.exceptions import Warning

class training_course_design(models.Model):
	_name = 'training.course.design'
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(required=True, track_visibility="onchange")
	training_type = fields.Many2one('types.short.training', required=True, track_visibility="onchange")
	date_from = fields.Date(track_visibility="onchange")
	date_to = fields.Date(track_visibility="onchange")
	no_hours = fields.Float(track_visibility="onchange")
	attachment = fields.Binary(track_visibility="onchange")
	program_components = fields.Html(track_visibility="onchange")
	target_of_program = fields.Html(track_visibility="onchange")
	outputs = fields.Html(track_visibility="onchange")
	notes = fields.Html(track_visibility="onchange")
	line_ids = fields.One2many("participants.line","participants_id")
	
	competencie_date_from = fields.Date()
	competencie_date_to = fields.Date()
	competencie_id = fields.Many2many('competencie.model',string='Competencies')
	gap_from = fields.Float('Gap percentage from', required=True,)
	gap_to = fields.Float('To', required=True,)


	competencie_ids = fields.One2many("competencie.design.line","line_id")
	
	state = fields.Selection([('draft', 'Draft'),('td_confirm', 'Training Department'),('hr_confirm', 'Human Resource'),('gm_confirm','GM/BM'),('rejected', 'Rejected'),('rejected1', 'Rejected1')],"States", default="draft", track_visibility="onchange")

	@api.multi
	def td_confirm(self):
		if not self.line_ids:
			raise Warning(_('Please enter participants details'))
		self.write({'state':'td_confirm'})

	@api.multi
	def hr_confirm(self):
		self.write({'state':'hr_confirm'})

	
	@api.multi
	def gm_confirm(self):
		self.write({'state':'gm_confirm'})

	@api.multi
	def do_reject(self):
		self.write({'state':'rejected'})

	@api.multi
	def do_reject1(self):
		self.write({'state':'rejected1'})

	@api.multi
	def do_return(self):
		if self.state == 'td_confirm':
			self.write({'state':'draft'})
		if self.state == 'hr_confirm':
			self.write({'state':'td_confirm'})

	@api.multi
	def do_return1(self):
		if self.state == 'td_confirm':
			self.write({'state':'draft'})
		if self.state == 'hr_confirm':
			self.write({'state':'td_confirm'})



	def get_participants(self):
		domain = []
		if self.competencie_date_from:
			domain.append(('date_from','>=',self.competencie_date_from))
		if self.competencie_date_to:
			domain.append(('date_to','<=',self.competencie_date_to))

		competencies = self.env['evaluating.merits'].search(domain)

		employees = []
		for competencie in competencies:
			for line in competencie.line_ids:
				if self.competencie_id:	
					for com in self.competencie_id:
							if com == line.merit:
								if line.gap_percentage >= self.gap_from and line.gap_percentage <= self.gap_to:
									if competencie.employee_id not in employees:
										employees.append(competencie.employee_id)
				else:
					if line.gap_percentage >= self.gap_from and line.gap_percentage<= self.gap_to:
						if competencie.employee_id not in employees:
							employees.append(competencie.employee_id)

		employee_list = []
		for employee in employees:
			employee_list.append({'employee_id':employee.id})


		self.line_ids = False
		self.line_ids = employee_list

                                




class participantsLine(models.Model):
	_name = 'participants.line'
	employee_id = fields.Many2one('hr.employee', required=True,)
	department_id = fields.Many2one('hr.department',readonly=True, )
	degree_id = fields.Many2one('functional.degree', readonly=True, )
	job_id = fields.Many2one('hr.function', readonly=True, )
	participants_id = fields.Many2one('training.course.design')

	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.department_id = self.employee_id.department_id
			self.degree_id = self.degree_id
			self.job_id = self.employee_id.functional_id
		

class trainingNeedsLine(models.Model):
	_name = 'competencie.design.line'
	competencie_id = fields.Many2one('competencie.model')
	
	line_id =fields.Many2one('training.course.design')