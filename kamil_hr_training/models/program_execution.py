from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime

class programExecution(models.Model):
	_name = 'program.execution'
	_inherit = ['mail.thread','mail.activity.mixin']


	name = fields.Char(required=True,)
	training_programs = fields.Many2one('training.course.design',track_visibility="onchange")
	country =fields.Many2one("res.country",track_visibility="onchange")
	city_id=fields.Many2one('city.city', track_visibility="onchange")
	training_type = fields.Many2one('types.short.training',track_visibility="onchange")
	discharge_type = fields.Selection([('morning','Morning'),('evening','Evening'),('whole','Whole')],track_visibility="onchange")
	program_type = fields.Selection([('internal','Internal'),('external','External')],track_visibility="onchange",)
	date_from = fields.Date(track_visibility="onchange")
	date_to = fields.Date(track_visibility="onchange")
	hour_from = fields.Float(track_visibility="onchange")
	hour_to = fields.Float(track_visibility="onchange")
	training_center = fields.Many2one('training.center',track_visibility="onchange")
	coach = fields.Many2one('coach.record',track_visibility="onchange")
	currency = fields.Many2one('res.currency',track_visibility="onchange")
	attachment = fields.Binary(track_visibility="onchange")
	funding_type =fields.Selection([('subjectively','Subjectively'),('financier','Financier'),('both','Both')],required=True,default='subjectively',track_visibility="onchange")
	financier_name = fields.Char(track_visibility="onchange")
	total_cost = fields.Float(compute='compute_amounts', readonly=True, )
	total_fund_cost = fields.Float(compute='compute_amounts')
	total_financing_cost = fields.Float(compute='compute_amounts')
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)

	line_ids = fields.One2many("participants.participants","participants_id")
	line_id = fields.One2many("cost.cost","cost_id")
	
	state = fields.Selection([('draft', 'Draft'),('td_confirm', 'Training Department'),('hr_confirm', 'Human Resource'),('gm_confirm','GM/BM'),('accounting','Accounting'),('rejected', 'Rejected')],"Status", default="draft",track_visibility="onchange")

	@api.onchange('date_from','date_to')
	@api.multi
	def _date(self):
		if self.date_to and self.date_from:
			if self.date_from > self.date_to:
				raise Warning(_("Sorry! The start date cannot be greater than the end date"))
	@api.multi
	def confirm(self):
		self.write({'state':'td_confirm'})

	@api.multi
	def td_confirm(self):
		self.write({'state':'hr_confirm'})

	@api.multi
	def hr_confirm(self):
		self.write({'state':'gm_confirm'})

	
	@api.multi
	def gm_confirm(self):
		ratification = self.env['ratification.ratification'].create({
			'state_id':self.create_uid.company_id.id,
			'name':'مصروفات ' + ( self.name ),
			})
		ratification_list = []
		for line in self.line_id:
			ratification_list.append({'name':line.item_name,
				'amount':line.amount,
				'ratification_id':ratification.id,})
		
		ratification.line_ids = ratification_list
		self.write({'state':'accounting'})


	@api.multi
	def do_reject(self):
		self.write({'state':'rejected'})

	@api.multi
	def do_reject1(self):
		self.write({'state':'rejected'})

	@api.multi
	def do_reject2(self):
		self.write({'state':'rejected'})

	@api.multi
	def do_return(self):
		self.write({'state':'draft'})

	@api.multi
	def do_return1(self):
		self.write({'state':'td_confirm'})

	@api.multi
	def do_return2(self):
		self.write({'state':'hr_confirm'})

	@api.onchange('line_id')
	def compute_amounts(self):
		for rec in self:
			total_financing_cost = 0.00
			total_fund_cost = 0.00
			for line in rec.line_id:
				if line.financier == 'financier':
					total_financing_cost += line.amount
				if line.financier == 'subjectively':
					total_fund_cost += line.amount
			rec.total_financing_cost = total_financing_cost
			rec.total_fund_cost = total_fund_cost
			rec.total_cost = rec.total_financing_cost + rec.total_fund_cost

	@api.onchange('training_programs')
	def _onchange_training_programs(self):
		if self.training_programs:
			self.date_from = self.training_programs.date_from
			self.date_to = self.training_programs.date_to
			lines = []
			for line in self.training_programs.line_ids:
				lines.append({'employee_id':line.employee_id.id,})
			self.line_ids = False
			self.line_ids = lines
	        

	@api.onchange('line_ids')
	def _onchange_line_ids(self):
		for rec in self:
			employees_list = []
			for line in rec.line_ids:
				if line.employee_id in employees_list:
					raise Warning(_('Can not add ( %s ) more than one time' %line.employee_id.name))
				employees_list.append(line.employee_id)
	    

class programExecutionLine(models.Model):
	_name = 'participants.participants'
	employee_id = fields.Many2one('hr.employee', required=True)
	department_id = fields.Many2one('hr.department',readonly=True, related='employee_id.department_id')
	degree_id = fields.Many2one('functional.degree', readonly=True, related='employee_id.degree_id')
	job_id = fields.Many2one('hr.function', readonly=True, related='employee_id.functional_id')
	participants_id = fields.Many2one('program.execution')



class costLine(models.Model):
	_name = 'cost.cost'
	item_name = fields.Char(required=True,)
	financier = fields.Selection([('subjectively','Subjectively'),('financier','Financier')],required=True,default='subjectively')
	amount = fields.Float(required=True,)
	cost_id = fields.Many2one('program.execution')


class surveyInherit(models.Model):
	_inherit = 'survey.survey'

	training_programs = fields.Many2one('program.execution', domain=[('state','=','gm_confirm'), ])
	is_training = fields.Boolean()
