from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime



class launch_trayning(models.Model):
	_name = 'launch.training'
	_description= "Launch of the training program"
	_inherit = ['mail.thread','mail.activity.mixin']
	
	name=fields.Char(required=True, string="training program name", track_visibility="onchange")
	date_from = fields.Date(track_visibility="onchange",required=True)
	date_to = fields.Date(track_visibility="onchange",required=True)
	launch_date = fields.Date(default=lambda self: fields.Date.today(),readonly="True",track_visibility="onchange",required=True)
	specialization = fields.Many2one('university.specialization',track_visibility="onchange", required=True)
	university_id = fields.Many2one('university.model',track_visibility="onchange", required=True)
	country =fields.Many2one("res.country", required=True)
	city_id=fields.Many2one('city.city', related='university_id.city_id')
	submission_deadline =fields.Date(track_visibility="onchange")
	age= fields.Integer(string='Maximum age')
	years_number =fields.Integer(string='Less years to work')
	document_ids =fields.Many2many('document.document', string='Certificates')
	other_conditions =fields.Html()
	postgraduate_information = fields.Html()
	country_information = fields.Html()
	compensation_period = fields.Integer()
	extension_rules =fields.Text()
	penal_conditions =fields.Text()
	submissions_count = fields.Integer(compute='submissions')
	evaluation_count = fields.Integer(compute='evaluation_candidates')
	missions_count = fields.Integer(compute='study_missions')
	lines_ids = fields.One2many('launch.training.line','launch_id', string="Financial Benefits")
	required_doc_ids = fields.One2many("required.document",'launch_id')

	state = fields.Selection([
		('draft','Draft'),
		('confirmed','Confirmed'),
		('submission_opened','Open the submission'),
		('closed','Closed'),], string="Status" ,default='draft',track_visibility="onchange" )

	def do_confirm(self):
		if self.age == 0:
			raise Warning(_('The Maximum Age could not be zero'))
		self.state = 'confirmed'

	def do_submission_opened(self):
		self.state = 'submission_opened'

	def do_close(self):
		self.state = 'closed'

	def set_to_draft(self):
		self.state = 'draft'

	def submission_deadline_check(self):
		for rec in self.env['launch.training'].search([]):
			if rec.submission_deadline:
				if rec.submission_deadline < date.today():
					rec.state = 'closed'

	@api.onchange('date_from','date_to')
	def _date_constratin(self):
		if self.date_from and self.date_to and self.date_from > self.date_to:
			raise Warning(_('start date cannot be greater than end date'))

	def submissions(self):
		submissions_obj = self.env['apply.training'].search([('training_program','=',self.id)])
		submissions_list = []
		for expense in submissions_obj:
			submissions_list.append(expense.id)
		self.submissions_count = len(submissions_list)
		return {
			'name': _('Submissions'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'apply.training',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', submissions_list)],
			'context':{'default_training_program':self.id,}
			}

	def evaluation_candidates(self):
		evaluation_obj = self.env['evaluation.candidates'].search([('training_program','=',self.id)])
		evaluation_list = []
		for evaluation in evaluation_obj:
			evaluation_list.append(evaluation.id)
		self.evaluation_count = len(evaluation_list)
		return {
			'name': _('Evaluation Candidates'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'evaluation.candidates',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', evaluation_list)],
			'context':{'default_training_program':self.id,}
			}

	def study_missions(self):
		mission_obj = self.env['study.mission'].search([('training_program','=',self.id)])
		mission_list = []
		for mission in mission_obj:
			mission_list.append(mission.id)
		self.missions_count = len(mission_list)
		return {
			'name': _('Study missions'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'study.mission',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', mission_list)],
			'context':{'default_training_program':self.id,}
			}


class launchTrainingLine(models.Model):
	_name = 'launch.training.line'
	item = fields.Char()
	cash = fields.Float()
	launch_id =fields.Many2one('launch.training')

class RequiredDocument(models.Model):
	_name="required.document"
	document_id = fields.Many2one('document.document', required=True,)
	launch_id = fields.Many2one("launch.training")