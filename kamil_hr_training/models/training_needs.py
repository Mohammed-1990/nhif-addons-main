from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime

class trainingNeeds(models.Model):
	_name='training.needs'
	_inherit = ['mail.thread','mail.activity.mixin']
	
	name=fields.Char(readonly=True, )
	employee_id=fields.Many2one('hr.employee',readonly=True,  required=True, default=lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]))
	employee_no = fields.Char(string="Employee Number", readonly=True, )
	department_id = fields.Many2one('hr.department',readonly=True, )
	functional_id=fields.Many2one("hr.function", readonly=True, )
	date=fields.Date(default=lambda self: fields.Date.today() , readonly=True, )
	employee_notes=fields.Html(track_visibility="onchange")
	training_department_notes=fields.Html(track_visibility="onchange")
	line_ids = fields.One2many("training.needs.line","needs_id")
	state = fields.Selection([
		('draft','Draft'),
		('submitted','It was sent to the training department'),
		('confirmed','Approval of training department'),
		('rejected','Rejected')], string="Status" ,default='draft',track_visibility="onchange" )


	@api.model
	def create(self, values):
		res = super(trainingNeeds, self).create(values)
		res.name = 'طلب احتياج تدريبي للموظف "'+res.employee_id.name+'"'
		return res

	@api.onchange('functional_id')
	def _onchange_functional_idd(self):
		line_list = []
		if self.functional_id:
			for line in self.functional_id.competencie_line_ids:
				line_list.append({'competencie_id':line.competencie_id.id,
					})
			self.line_ids = False
			self.line_ids = line_list


	# @api.onchange('employee_id')
	# def _onchange_employee_id(self):
	# 	if self.employee_id:
	# 		self.employee_no = self.employee_id.number
	# 		self.department_id = self.employee_id.department_id
	# 		self.functional_id = self.employee_id.functional_id


	# @api.onchange('employee_no')
	# def _onchange_employee_no(self):
	# 	if self.employee_no:
	# 		self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)]).id
	# 		self._onchange_employee_id()


	def do_submit(self):
		for line in self.line_ids:
			line.state = 'submitted'
		self.state = 'submitted'

	def do_confirm(self):
		for line in self.line_ids:
			line.state = 'confirmed'
		self.state = 'confirmed'

	def do_reject(self):
		self.state = 'rejected'


class trainingNeedsLine(models.Model):
	_name = 'training.needs.line'
	competencie_id = fields.Many2one('competencie.model', required=True,)
	approved = fields.Boolean(track_visibility="onchange")
	notes = fields.Char(track_visibility="onchange")
	state = fields.Selection([
		('draft','Draft'),
		('submitted','Training department'),
		('confirmed','Confirmed'),], string="Status" ,default='draft',track_visibility="onchange" )

	
	needs_id =fields.Many2one('training.needs')