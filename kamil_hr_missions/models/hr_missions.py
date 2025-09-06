# -*- coding: utf-8 -*-

from openerp import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime


class missionsAssigned(models.Model):
	_name = 'missions.assigned'
	_inherit = ['mail.thread','mail.activity.mixin']
	_description = "Missions"
	_order = "id desc"

	name = fields.Char('Number',readonly=True, copy=False,track_visibility="onchange")
	missions_side = fields.Char(required=True,track_visibility="onchange")
	missions_type = fields.Selection([('inside','Inside State'),('outside','Outside State'),], default='inside', required=True,track_visibility="onchange")
	date_from = fields.Date(required=True,track_visibility="onchange")
	date_to = fields.Date(required=True,track_visibility="onchange")
	team_leader = fields.Many2one('hr.employee' , required=True,track_visibility="onchange")
	mission_purpose = fields.Text(required=True,track_visibility="onchange")
	assigned  = fields.Many2one('res.users', default=lambda self: self.env.user,track_visibility="onchange")
	assigned_date = fields.Date(default=lambda self: fields.Date.today(),track_visibility="onchange")
	statee_id = fields.Many2one('state.model', string="Sstatee" , required=True,track_visibility="onchange")
	notes=fields.Text()
	line_ids = fields.One2many("missions.assigned.line","assigned_id")
	line_ids2 = fields.One2many("missions.assigned.line2","assigned_id2")

	state = fields.Selection([('draft', 'Draft'),('submit','Sumbitted'),('confirmed','Confirmed'),('reject','Reject')],string="Status", default="draft",track_visibility="onchange")
	petty_cash_count = fields.Integer(compute='petty_cash')


	@api.onchange('date_from','date_to')
	@api.multi
	def _date(self):
		if self.date_to and self.date_from:
			if self.date_from > self.date_to:
				raise Warning(_("Sorry! The start date cannot be greater than the end date"))


	@api.multi
	def petty_cash(self):
		petty_cash_obj = self.env['mission.petty'].search([('mission_id','=',self.id)])
		petty_cash_list = []
		for petty in petty_cash_obj:
			petty_cash_list.append(petty.id)
		self.petty_cash_count = len(petty_cash_list)
		return {
			'name': _('Petty cash'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'mission.petty',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', petty_cash_list)],
			'context':{'default_mission_id':self.id,}
			}

	@api.model
	def create(self, values):
		res = super(missionsAssigned, self).create(values)
		res.name = self.env['ir.sequence'].get('missions.assigned.req') +' / ' + res.missions_side
		return res

	@api.multi
	def unlink(self):
		if self.state != 'draft':
			raise Warning(_('The errand assignment cannot be deleted in the non-draft state'))
		return super(missionsAssigned, self).unlink()

	def submit(self):
		self.write({'state':'submit'})

	def reject(self):
		self.write({'state':'reject'})

	def set_to_draft(self):
		self.write({'state':'draft'})

	@api.multi
	def confirm(self):
		#notify employee
		# for line in self.line_ids:
		# 	if line.employee_id.user_id:
		# 		self.env['mail.activity'].create({
		# 			'res_name': _('Missions'),
		#             'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
		#             'date_deadline':date.today(),
		#             'summary': _('Missions'),
		#             'user_id': line.employee_id.sudo().user_id.id,
		#             'res_id': self.id,
		#             'res_model_id': self.env.ref('kamil_hr_missions.model_missions_assigned').id,
		#         })
		
		self.write({'state':'confirmed'})

class missionsAssignedLine(models.Model):
	_name = 'missions.assigned.line'
	employee_id = fields.Many2one('hr.employee', string="Employee", required=True,)
	department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True, )
	degree_id = fields.Many2one("functional.degree", related='employee_id.degree_id', readonly=True,)
	job_title_id = fields.Many2one('job.title', related='employee_id.job_title_id', readonly=True,)
	assigned_id = fields.Many2one('missions.assigned',ondelete='cascade')

class missionsAssignedLine2(models.Model):
	_name ='missions.assigned.line2'
	name = fields.Char(required=True,)
	assigned_id2 = fields.Many2one('missions.assigned',ondelete='cascade')


class missionsCategoriesPetty(models.Model):
	_name = 'missions.categories.petty'
	name = fields.Char(required=True)
	missions_type = fields.Selection([('inside','Inside State'),('outside','Outside State'),], default='inside', required=True,)


	line_ids = fields.One2many("missions.categories.petty.line", "categories_petty_id")

class missionsCategoriesPettyLine(models.Model):
	_name = 'missions.categories.petty.line'
	job_title_id = fields.Many2one('job.title', required=True,)
	petty = fields.Integer(required=True,)
	mission_allowance = fields.Integer(required=True,)
	categories_petty_id = fields.Many2one('missions.categories.petty',ondelete='cascade')

class missionPetty(models.Model):
	_name = 'mission.petty'
	_inherit = ['mail.thread','mail.activity.mixin']
	_order = "id desc"


	def missions_domain(self):
		ids_list = []
		for petty in self.env['mission.petty'].search([]):
			ids_list.append(petty.mission_id.id)
		return [('id','not in',ids_list),('state','=','confirmed')]

	name = fields.Char(readonly=True)
	mission_id = fields.Many2one("missions.assigned", domain=missions_domain ,required=True,)
	no_days = fields.Integer(readonly=True)
	cost_travel_fuel = fields.Float()
	cost_visas = fields.Float()
	means_of_travel = fields.Char()
	departure_fee = fields.Float()
	total = fields.Float(compute='_compute_total')
	visa_cost_officer = fields.Many2one('hr.employee')
	line_ids = fields.One2many("mission.petty.line","petty_id")
	state = fields.Selection([
		('draft','Draft'),
		('submitted','Sumbitted'),
		('confirmed','Accounting'),
		('reject','Reject')],string="Status", default='draft',track_visibility="onchange" )
	petty_cash_clearance_count = fields.Integer(compute='petty_cash_clearance')
	
	@api.model
	def create(self, values):
		res = super(missionPetty, self).create(values)
		if self.env['mission.petty'].search([('mission_id','=',res.mission_id.id),('id','!=',res.id)]):
			raise Warning(_('It is not possible to create more than one incidental for the same mission'))
		res.name = self.env['ir.sequence'].get('mission.petty.req') or ' ' 
		return res

	@api.multi
	def unlink(self):
		if self.state != 'draft':
			raise Warning(_('The petty cannot be deleted in the non-draft state'))
		return super(missionPetty, self).unlink()

	@api.onchange('mission_id')
	def compute_petty_line(self):
		for line in self.line_ids:
			for category in self.env['missions.categories.petty'].search([('missions_type','=',self.mission_id.missions_type)],limit=1):
				for category_line in category.line_ids:
					if category_line.job_title_id == line.job_title_id:
						line.amount = category_line.petty
						line.total = line.amount * self.no_days
		self._compute_total()

	def do_submit(self):
		if not self.line_ids:
			raise Warning(_('Please enter petty cash details'))
		if self.total == 0:
			raise Warning(_('Total can not be zero'))
		self.state = 'submitted'

	def reject(self):
		self.write({'state':'reject'})

	def set_to_draft(self):
		self.write({'state':'draft'})

	def do_confirm(self):
		#ratification
		mission_petty_cash = self.env['hr.account.config'].search([],limit=1).mission_petty_cash
		ratification_line = []
		ratification = self.env['ratification.list'].create({'name':self.name,
			'date':date.today(),
			})
		for line in self.line_ids:
			#ratification line
			amount = line.amount*self.no_days
			if amount > 0:
				if line.employee_id == self.mission_id.team_leader:
					amount += self.cost_travel_fuel + self.departure_fee
				ratification_line.append({
					'name':self.name,
					'partner_id':line.employee_id.partner_id.id,
					'branch_id':line.employee_id.company_id.id,
					'amount':amount,
					'account_id':mission_petty_cash.id,
					'analytic_account_id':mission_petty_cash.parent_budget_item_id.id,
					'ratification_list_id':ratification.id,
					'company_id':line.employee_id.company_id.id,})
		if self.visa_cost_officer:
			ratification_line.append({
				'name':'تكلفه التأشيرات',
				'partner_id':self.visa_cost_officer.partner_id.id,
				'branch_id':self.visa_cost_officer.company_id.id,
				'amount':self.cost_visas,
				'account_id':mission_petty_cash.id,
				'analytic_account_id':mission_petty_cash.parent_budget_item_id.id,
				'analytic_account_id':mission_petty_cash.parent_budget_item_id.id,
				'ratification_list_id':ratification.id,
				'company_id':line.employee_id.company_id.id,})
		ratification.ratification_line_ids = ratification_line
		self.state = 'confirmed'


	@api.onchange('cost_travel_fuel','cost_visas','departure_fee')
	def _compute_total(self):
		for rec in self:
			total = 0.00
			for line in rec.line_ids:
				total += line.total
			rec.total = rec.cost_travel_fuel + rec.cost_visas + rec.departure_fee + total

	@api.onchange('mission_id')
	def _onchange_mission_id(self):
		lines = []
		if self.mission_id:
			lines.append({'employee_id':self.mission_id.team_leader.id,})
			for line in self.mission_id.line_ids:
				lines.append({'employee_id':line.employee_id.id,})
			self.no_days = (self.mission_id.date_to - self.mission_id.date_from).days + 1

		self.line_ids = False
		self.line_ids = lines

class missionPettyLine(models.Model):
	_name = 'mission.petty.line'
	employee_id = fields.Many2one('hr.employee', readonly=True)
	job_title_id = fields.Many2one('job.title', related='employee_id.job_title_id' ,readonly=True, )
	amount = fields.Float(readonly=True, )
	total = fields.Float(readonly=True, )
	petty_id = fields.Many2one('missions.petty',ondelete='cascade')

class missionFiltering(models.Model):
	_name = 'mission.filtering'
	name = fields.Char(readonly=True)
	mission_id = fields.Many2one("missions.assigned", domain=[('state','=','confirmed'), ] ,required=True,)
	petty_id = fields.Many2one('mission.petty', required=True,)
	date = fields.Date(default=lambda self: fields.Date.today(), readonly=True, )
	attachment = fields.Binary()
	petty_amount = fields.Float(related='petty_id.total',readonly=True, string='Petty amount')
	total = fields.Float(readonly=True, )
	line_ids = fields.One2many("mission.filtering.line","filtering_id")
	state = fields.Selection([
		('draft','Draft'),
		('submitted','Sumbitted'),
		('confirmed','Confirmed'),], string="Status" ,default='draft',track_visibility="onchange" )

	@api.model
	def create(self, values):
		
		values['name'] = self.env['ir.sequence'].get('mission.filtering.req') or ' ' 
		return super(missionFiltering, self).create(values)

	@api.onchange('mission_id')
	def _onchange_mission_id(self):
		return {'domain':{'petty_id':[('mission_id','=',self.mission_id.id)]}
		}

	@api.onchange('line_ids')
	def _onchange_line_ids(self):
		total = 0.00
		for line in self.line_ids:
			total += line.amount
		self.total = total


	def do_submit(self):
		if not self.line_ids:
			raise Warning(_('Please enter details'))
		self.state = 'submitted'

	def do_confirm(self):
		self.state = 'confirmed'


class missionFilteringLine(models.Model):
	_name = 'mission.filtering.line'
	item = fields.Char(required=True,)
	amount = fields.Float(required=True,)
	filtering_id = fields.Many2one('mission.filtering')

class MissionExtend(models.Model):
	_name = 'mission.extend'
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'mission_id'

	user_id = fields.Many2one('res.users', string='Requestor', default=lambda self: self.env.user , readonly=True, )
	mission_id = fields.Many2one("missions.assigned" ,required=True,track_visibility="onchange", )
	team_leader = fields.Many2one('hr.employee',related='mission_id.team_leader',readonly=True,track_visibility="onchange")
	area = fields.Char(related='mission_id.missions_side')
	date_from = fields.Date(related='mission_id.date_from')
	date_to = fields.Date(related='mission_id.date_to')
	mission_purpose = fields.Text(related='mission_id.mission_purpose')
	extend_reason = fields.Text(required=True,)
	extend_to = fields.Date(string="Extend To",required=True,track_visibility="onchange")
	reason_refuse = fields.Html(track_visibility="onchange")
	state = fields.Selection([('draft', 'Draft'),('gm_confirm','GM Confirm'),('finance','Finance'),('confirmed','Confirmed'),('rejected','Rejected')],"States", default="draft",track_visibility="onchange")


	@api.multi
	def gm_confirm(self):
		self.write({'state':'gm_confirm'})

	@api.multi
	def finance(self):
		self.write({'state':'finance'})

	@api.multi
	def confirmed(self):
		self.write({'state':'confirmed'})

	@api.multi
	def action_reject(self):
		if not self.env["ir.fields.converter"].text_from_html(self.reason_refuse, 40, 1000, "..."):
			raise Warning(_('Please Enter reason'))
		self.state = 'rejected'

	@api.onchange('extend_to')
	def _onchange_extend_to(self):
		if self.extend_to:
			if self.extend_to < self.date_to:
				raise Warning(_('Sorry! Extension date must be greater than mission end date'))



class missionReport(models.Model):
	_name = 'mission.report'
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'mission_id'
	_order = "id desc"

	name = fields.Char(default='/')
	mission_id = fields.Many2one("missions.assigned", domain=[('state','=','confirmed'), ] ,required=True,)
	team_leader = fields.Many2one('hr.employee',related='mission_id.team_leader',readonly=True, )
	area = fields.Char(related='mission_id.missions_side',)
	date_from = fields.Date(related='mission_id.date_from')
	date_to = fields.Date(related='mission_id.date_to')
	mission_purpose = fields.Text(related='mission_id.mission_purpose')
	report_date = fields.Date(default=lambda self: fields.Date.today() ,readonly=True, )
	mission_details = fields.Text(required=True)
	summary_tasks_completed = fields.Html(required=True)
	state = fields.Selection([
		('draft','Draft'),
		('gm_confirm','Sumbitted'),
		('confirmed','Confirmed'),
		('rejected','Rejected')], string='Status',default='draft',track_visibility="onchange" )

	@api.model
	def create(self, values):
		res = super(missionReport, self).create(values)
		if self.env['mission.report'].search([('id','!=',res.id),('mission_id','=',res.mission_id.id)]):
			raise Warning(_('Can not create more than one report for the same mission'))
	    
		return res



	def gm_confirm(self):
		if not self.env["ir.fields.converter"].text_from_html(self.summary_tasks_completed, 40, 1000, "..."):
			raise Warning(_('Please enter summary of tasks completed'))

		self.state = 'gm_confirm'

	def do_confirm(self):
		self.state = 'confirmed'

	def action_reject(self):
		self.state = 'rejected'

	@api.onchange('report_date','date_to')
	@api.multi
	def _get_report_date(self):
		if self.report_date and self.date_to:
			if self.report_date < self.date_to:
				raise Warning(_("Sorry! A report cannot be created before the end of the Mission"))

class missionAllowance(models.Model):
	_name = 'mission.allowance'
	_inherit = ['mail.thread','mail.activity.mixin']
	_rec_name = 'mission_id'
	_order = "id desc"

	def missions_domain(self):
		reports_ids_list = []
		alw_ids_list = []
		ids_domain_list = []
		for report in self.env['mission.report'].search([('state','=','confirmed')]):
			reports_ids_list.append(report.mission_id.id)
		
		for alw in self.env['mission.allowance'].search([('id','!=',self.id)]):
			alw_ids_list.append(alw.mission_id.id)
		ids_domain_list = list(set(reports_ids_list) - (set(alw_ids_list)))

		return [('id','in',ids_domain_list)]

	name = fields.Char(default='/')
	mission_id = fields.Many2one("missions.assigned", required=True,domain=missions_domain)
	date = fields.Date(default=lambda self: fields.Date.today())
	no_days = fields.Integer(readonly=True, )
	total = fields.Float(compute='_compute_total')
	line_ids = fields.One2many("mission.allowance.line","allowance_id")
	stamp = fields.Many2one('account.tax',track_visibility="onchange")
	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits And Wages'),
		('hr_m','Human Resource Management'),
		('general_hr','General Administration for Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounting','Accounting'),],string="Status", default='draft',track_visibility="onchange" )
	def do_return(self):
		if self.state == 'internal_auditor':
			self.state = 'general_hr'
		elif self.state == 'general_hr':
			self.state = 'hr_m'
		elif self.state == 'hr_m':
			self.state = 'benefits_wages'
		elif self.state == 'benefits_wages':
			self.state = 'draft'

	def benefits_wages(self):
		if not self.line_ids:
			raise Warning(_('Please enter allowance details'))
		if self.total <= 0:
			raise Warning(_('Total amount can not be zero'))
		self.state = 'benefits_wages'

	def hr_m(self):
		self.state = 'hr_m'

	def general_hr(self):
		self.state= 'general_hr'

	def internal_auditor(self):
		self.state='internal_auditor'	

	def send_to_account(self):
		#Delete Old rati
		for rati in self.env['ratification.list'].search([('mission_allowance_id','=',self.id)]):
			rati.write({'state':'canceled'})
			rati.sudo().unlink()

		ratification_line = []
		ratification = self.env['ratification.list'].create({'name':'بدل '+self.mission_id.name,
			'date':date.today(),
			'from_hr':True,
			'mission_allowance_id':self.id,
			})
		mission_allowance = self.env['hr.account.config'].search([],limit=1).mission_allowance
		for line in self.line_ids:
			#ratification line
			if line.net > 0:
				ratification_line.append({
					'name':'بدل '+self.mission_id.name,
					'partner_id':line.employee_id.partner_id.id,
					'branch_id':line.employee_id.company_id.id,
					'amount':line.amount*self.no_days,
					'account_id':mission_allowance.id,
					'analytic_account_id':mission_allowance.parent_budget_item_id.id,
					'ratification_list_id':ratification.id,
					'company_id':line.employee_id.company_id.id,
					'deduction_ids':[{'tax_id':self.stamp,'name':self.stamp.name,'amount':self.stamp.amount,
					}]})
		ratification.ratification_line_ids = ratification_line
		self.state = 'accounting'
	
	@api.onchange('stamp','mission_id')
	def compute_allowance_line(self):
		lines = []
		if self.mission_id:
			lines.append({'employee_id':self.mission_id.team_leader.id,})
			for line in self.mission_id.line_ids:
				lines.append({'employee_id':line.employee_id.id,})
			self.no_days = (self.mission_id.date_to - self.mission_id.date_from).days + 1
		self.line_ids = False
		self.line_ids = lines
		for line in self.line_ids:
			for category in self.env['missions.categories.petty'].search([('missions_type','=',self.mission_id.missions_type)],limit=1):
				for category_line in category.line_ids:
					if category_line.job_title_id == line.job_title_id:
						line.amount = category_line.mission_allowance
						line.no_days = self.no_days
						line.stamp = self.stamp.amount
						line.total = (line.amount * self.no_days)
						line.net =  (line.amount * self.no_days) - line.stamp  


	@api.onchange('line_ids')
	def _compute_total(self):
		for rec in self:
			total = 0.00
			for line in rec.line_ids:
				total += line.net
			rec.total = total

class missionAllowanceLine(models.Model):
	_name = 'mission.allowance.line'
	employee_id = fields.Many2one('hr.employee' ,required=True)
	job_title_id = fields.Many2one('job.title', related='employee_id.job_title_id', readonly=True,)
	amount = fields.Float()
	no_days = fields.Integer(readonly=True, )
	total = fields.Float(readonly=True, )
	stamp = fields.Float()
	net = fields.Float()
	allowance_id = fields.Many2one('mission.allowance',ondelete='cascade')

