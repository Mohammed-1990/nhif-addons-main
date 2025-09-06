from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime


class inevitableSettings(models.Model):
	_name = 'inevitable.settings'

	name = fields.Char(required=True,)
	degree_id = fields.Many2one('functional.degree', required=True,)
	line_ids = fields.One2many('inevitable.settings.line','line_id')

	@api.model
	def create(self, values):
		res = super(inevitableSettings, self).create(values)
		if self.env['inevitable.settings'].search([('degree_id','=',res.degree_id.id),('id','!=',res.id)]):
			raise Warning(_('The inevitable training for the class has been prepared "%s"')%(res.degree_id.name))

		return res

class inevitableSettingsLine(models.Model):
	_name = 'inevitable.settings.line'

	name = fields.Char(required=True,)
	line_id = fields.Many2one('inevitable.settings.line')

class inevitableTraining(models.Model):
	_name = 'inevitable.training'
	_inherit = ['mail.thread','mail.activity.mixin']

	name =fields.Char(default="/")
	degree_id = fields.Many2one('functional.degree', required=True,track_visibility="onchange")
	training_program = fields.Many2one('inevitable.settings.line', required=True,track_visibility="onchange")
	country =fields.Many2one("res.country",track_visibility="onchange")
	city_id=fields.Many2one('city.city',track_visibility="onchange")
	training_type = fields.Many2one('types.short.training')
	discharge_type = fields.Selection([('morning','Morning'),('evening','Evening'),('whole','Whole')],track_visibility="onchange")
	date_from = fields.Date()
	date_to = fields.Date()
	hour_from = fields.Float()
	hour_to = fields.Float()
	training_center = fields.Many2one('training.center')
	coach = fields.Many2one('coach.record')
	currency = fields.Many2one('res.currency')
	attachment = fields.Binary()
	funding_type =fields.Selection([('self','Self'),
		('funded','Funded'),
		('both','Both')])
	financier_name = fields.Char()
	total_cost = fields.Float(compute='compute_amounts')
	total_fund_cost = fields.Float(compute='compute_amounts')
	total_financing_cost = fields.Float(compute='compute_amounts')


	line_ids = fields.One2many("inevitable.training.line","participants_id")
	line_id = fields.One2many("cost.line","cost_id")
	
	state = fields.Selection([('draft', 'Draft'),('td_confirm', 'Training Department'),('hr_confirm', 'Human Resource'),('gm_confirm','GM/BM'),('rejected', 'Rejected'),('rejected1', 'Rejected1')],"States", default="draft")


	@api.onchange('date_from','date_to')
	@api.multi
	def _date(self):
		if self.date_to and self.date_from:
			if self.date_from > self.date_to:
				raise Warning(_("Sorry! The start date cannot be greater than the end date"))


	@api.onchange('degree_id')
	def _onchange_degree_id(self):
		
		inevitable = self.env['inevitable.settings'].search([('degree_id','=',self.degree_id.id)],limit=1).id
		return {'domain':{'training_program':[('line_id','=',inevitable)]}}

	@api.onchange('training_program')
	def _onchange_training_program(self):
		
		employees = self.env['hr.employee'].search([('degree_id','=',self.degree_id.id)])
		inevitables = self.env['inevitable.training'].search([('degree_id','=',self.degree_id.id),('training_program','=',self.training_program.id),('state','=','gm_confirm')])
		employees_list = []
		for employee in employees:
			flag = 0
			for inevitable in inevitables:
				for line in inevitable.line_ids:
					if line.employee_id == employee:
						flag = 1
			if flag == 0:
				employees_list.append({'employee_id':employee.id,})
		self.line_ids = employees_list



		
	        

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





class inevitableTrainingLine(models.Model):
	_name = 'inevitable.training.line'
	employee_id = fields.Many2one('hr.employee',required=True,)
	department_id = fields.Many2one('hr.department', readonly=True, )
	degree_id = fields.Many2one('functional.degree', readonly=True, )
	job_id = fields.Many2one('hr.function', readonly=True, )
	participants_id = fields.Many2one('inevitable.training')

	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.department_id = self.employee_id.department_id
			self.degree_id = self.employee_id.degree_id
			self.job_id = self.employee_id.functional_id

class costLine(models.Model):
	_name = 'cost.line'
	item_name = fields.Char()
	financier = fields.Char()
	amount = fields.Float()
	cost_id = fields.Many2one('inevitable.training')