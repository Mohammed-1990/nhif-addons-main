from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime



class evaluation_candidates(models.Model):
	_name='evaluation.candidates'
	_inherit = ['mail.thread','mail.activity.mixin']
	
	name=fields.Char()
	training_program =fields.Many2one('launch.training',required=True)
	specialization = fields.Many2one('university.specialization', related='training_program.specialization')
	university_id = fields.Many2one('university.model',related='training_program.university_id')
	city_id=fields.Many2one('city.city', related='training_program.city_id')
	age = fields.Integer(readonly=True,)
	employee_id= fields.Many2one('hr.employee',required=True)
	department_id=fields.Many2one('hr.department',related='employee_id.department_id')
	job_id = fields.Many2one('hr.function', string="Job",related='employee_id.functional_id')
	qualification_type = fields.Many2one('qualifcation.type',related='employee_id.appointment_qualification')
	total_degree = fields.Float(compute='_compute_total_degree')
	line_ids = fields.One2many("evaluation.candidates.line","evaluation_id")
	state = fields.Selection([
		('draft','Draft'),
		('approved','Approved'),
		('rejected','Rejected'),], string="Status" ,default='draft',track_visibility="onchange" )

	def do_approved(self):
		mission = self.env['study.mission'].create({'training_program':self.training_program.id,
			'employee_id':self.employee_id.id,})
		mission.onchange_training_program()
		mission.onchange_employee_id()
		if self.total_degree == 0:
			raise Warning(_("The overall score of the evaluation cannot be zero"))
		self.state = 'approved'

	def do_rejected(self):
		self.state = 'rejected'

	def do_cancel(self):
		mission = self.env['study.mission'].search([('training_program','=',self.training_program.id),('employee_id','=',self.employee_id.id)]).unlink()
		self.state = 'draft'
	@api.model
	def create(self, values):
		res = super(evaluation_candidates, self).create(values)
		res.name = 'تقييم المرشح '+' ( '+res.employee_id.name+' ) '+' للبرنامج التدريبي '+res.training_program.name
		return res

	@api.onchange('line_ids')
	def _compute_total_degree(self):
		for rec in self:
			total = 0.00
			for line in rec.line_ids:
				if line.evaluation == True:
					total += line.ratio
			rec.total_degree = total


class evaluationCandidatesLine(models.Model):
	_name = 'evaluation.candidates.line'
	standard = fields.Many2one('criteria.evaluating',required=True)
	ratio = fields.Float(related='standard.percentage', readonly=True, )
	evaluation = fields.Boolean()
	evaluation_id = fields.Many2one("evaluation.candidates")