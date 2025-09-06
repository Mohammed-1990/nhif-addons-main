# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
import math
import calendar
from datetime import date,datetime
from dateutil.relativedelta import relativedelta	


class RemovingDifferences(models.Model):
	_name="removing.differences"
	_inherit = ['mail.thread','mail.activity.mixin',]
	_order = "id desc"

	# @api.model
	# def year_selection(self):
	#     year = 2000 # replace 2000 with your a start year
	#     year_list = []
	#     while year != 2030: # replace 2030 with your end year
	#         year_list.append((str(year), str(year)))
	#         year += 1
	#     return year_list

	# year = fields.Selection(
	#     year_selection,
	#     string="Year",
	#     default="2019", 
	# 	)


	name = fields.Char(track_visibility="onchange", required=True)
	promotions_number = fields.Char(track_visibility="onchange")
	employee_id = fields.Many2one("hr.employee",string="Employee",required=True,track_visibility="onchange")
	num_emp = fields.Char("Employee Number" ,required=True,track_visibility="onchange")
	department_id = fields.Many2one("hr.department",readonly=True)
	current_degree = fields.Many2one("functional.degree", track_visibilit="onchange" ,string="old degree")
	upgrade_degree = fields.Many2one("functional.degree", track_visibilit="onchange")
	upgrade_date = fields.Date(string="Due date")
	implementation_date = fields.Date(string="Date of Exception")
	document = fields.Binary("Document",)
	notes = fields.Html(track_visibilit="onchange")
	days = fields.Integer(store=True)
	financial_difference = fields.Float()
	no_of_months = fields.Integer()
	bonus_amount = fields.Float()
	state = fields.Selection([
		('draft','Draft'),
		('submitted','Benefits and Fees Department'),
		('confirmed','Personnel'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('accounts','Accounts'),], 
		string="Status" ,default='draft',track_visibility="onchange" )
	type = fields.Selection([('promotion','Promotion'),('annual_bonus','Annual bonus'),('qualification_bonus','Qualification bonus'),('social_bonus','Social bonus'),('meal_allowance','Meal allowance'),('alternative_allowance','Alternative allowance')],track_visibility="onchange",)
	promotion_type = fields.Selection([
		('first_class','First Class'),
		('second_class','Second Class')],track_visibility="onchange", )
	first_bonus = fields.Selection([
		('first_bonus','First Bonus'),
		('second_bonus','Second Bonus'),
		('third_bonus','Third Bonus'),
		('fourth_bonus','Fourth Bonus'),
		('fifth_bonus','Fifth Bonus'),
		('sixth_bonus','Sixth Bonus'),
		('seventh_bonus','Seventh Bonus'),
		('eighth_bonus','Eighth Bonus'),
		('ninth_bonus','Ninth Bonus')
		], track_visibility="onchange")
	second_bonus = fields.Selection([
		('first_bonus','First Bonus'),
		('second_bonus','Second Bonus'),
		('third_bonus','Third Bonus'),
		('fourth_bonus','Fourth Bonus'),
		('fifth_bonus','Fifth Bonus'),
		('sixth_bonus','Sixth Bonus'),
		('seventh_bonus','Seventh Bonus'),
		('eighth_bonus','Eighth Bonus'),
		('ninth_bonus','Ninth Bonus')
		], track_visibility="onchange")
	allowance_type=fields.Many2one('allowances.allowances',track_visibility="onchange")
	first_qualification=fields.Many2one('qualifcation.type',track_visibility="onchange")
	second_qualification=fields.Many2one('qualifcation.type',track_visibility="onchange")
	meal_amount = fields.Float()
	line_ids = fields.One2many('removing.differences.line','line_id',string="Line ids")

	@api.onchange('num_emp')
	def _onchange_num_emp(self):
		if self.num_emp:
			self.employee_id = False
			self.employee_id = self.env['hr.employee'].search([('number','=',self.num_emp)],limit=1).id
			self.department_id = self.employee_id.department_id

	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.num_emp = False
			self.num_emp = self.employee_id.number
			self.department_id = self.employee_id.department_id
			self.current_degree = self.employee_id.degree_id
			if self.type == 'promotion':
				if self.env['hr.promotions'].search([('employee_id','=',self.employee_id.id),('state','=','approved')]):
					promotion_emp=self.env['hr.promotions'].search([('employee_id','=',self.employee_id.id),('state','=','approved')])[-1]
					self.current_degree = promotion_emp.current_degree_id
					self.upgrade_degree = promotion_emp.new_degree_id
					self.implementation_date = promotion_emp.exection_date
					self.upgrade_date= promotion_emp.promotion_date
				else:
					self.current_degree = False
					self.upgrade_degree = False
					self.implementation_date = False
					self.upgrade_date = False



	@api.onchange('employee_id','upgrade_date','implementation_date','promotion_type','type','bonus_amount','first_bonus','second_bonus','allowance_type','meal_amount')
	def get_different_days(self):
		differences_total=0.0
		self.days = 0.00
		self.financial_difference = 0.00
		if self.upgrade_date and self.implementation_date:
			if self.implementation_date < self.upgrade_date:
				raise Warning(_("Sorry!! The upgrade date cannot be greater than the execution date"))

			dif_month = self.implementation_date.month - self.upgrade_date.month + 12*(self.implementation_date.year - self.upgrade_date.year)
			if dif_month > 36:
				raise Warning(_("The Perform the upgradecan not be carried out after more than 36 months"))

			different_days = (fields.Date.from_string(self.implementation_date)-fields.Date.from_string(self.upgrade_date)).days
			days = 0
			if self.upgrade_date.month == self.implementation_date.month and self.upgrade_date.year ==  self.implementation_date.year :
				days=0
			elif self.implementation_date.month == date.today().month:
				month_date = self.implementation_date - relativedelta(months=1) 
				month_date = month_date + relativedelta(day=31)
				r = relativedelta(self.implementation_date, self.upgrade_date)
				months = r.months +  12 * r.years
				day  = 0
				if self.upgrade_date.day != 1:
					day = 30 - self.upgrade_date.day 
					r = relativedelta(month_date, self.upgrade_date)
					months = r.months
				days = months * 30 + day
			else:
				month_days = 0
				upgrade_date = self.upgrade_date
				implementation_date = self.implementation_date
				if self.upgrade_date.day != 1:
					day = self.upgrade_date.day
					if self.upgrade_date.day == 31:
						day = 30
					elif self.upgrade_date.month == 2:
						day = 30
					month_days += 30 - day 
					upgrade_date = self.upgrade_date + relativedelta(day=31)
				if self.implementation_date.day != 1:
					day = self.implementation_date.day
					if self.implementation_date.day == 31:
						day = 30
					month_days += day 
					implementation_date = self.implementation_date.replace(day=1)
				r = relativedelta(implementation_date, upgrade_date)
				days = r.months * 30 + month_days			
				
			self.days = 0.00
			self.days = abs(days)
			
		if self.type == 'promotion' or self.type == 'alternative_allowance':
			if self.promotion_type == 'first_class':
				if self.env['hr.payslip'].search([('employee_id','=',self.employee_id.id),('state','=','done')]):
					before_last_payslip = self.env['hr.payslip'].search([('employee_id','=',self.employee_id.id),('state','=','done')])[-2]
					last_payslip = self.env['hr.payslip'].search([('employee_id','=',self.employee_id.id),('state','=','done')])[-1]
					amount = 0.00
					lines_list = []
					for rule in self.employee_id.contract_id.struct_id.rule_ids:
						old_total = 0.00
						new_total = 0.00
						for line in before_last_payslip.line_ids:
							if line.salary_rule_id.id == rule.id:
								old_total = line.total
						for line in last_payslip.line_ids:
							if line.salary_rule_id.id == rule.id:
								new_total = line.total
						differnce_amount = new_total - old_total
						one_day_value = differnce_amount / 30
						amount += one_day_value * self.days
						lines_list.append({'rule':rule.id,
							'old_total':old_total,
							'new_total':new_total,
							'differnce_amount':differnce_amount,
							'one_day_value':one_day_value,
							'amount':one_day_value * self.days,})

					self.line_ids = False					
					self.line_ids = lines_list	
					self.financial_difference = amount				
			else:
				incentives = self.env['hr.incentive'].search(['|','|','&',('date_from','<',self.upgrade_date),('date_to','>',self.implementation_date),'&',('date_from','>=',self.upgrade_date),('date_from','<=',self.implementation_date),'&',('date_to','>=',self.upgrade_date),('date_to','<=',self.implementation_date)])
				differences_total = 0.00
				for incentive in incentives:
					incentive_amount = deserved_amount = 0.00
					if incentive.calculation_method == 'fixed_degree':
						for line in incentive.line_ids:
							if line.employee_id.id == self.employee_id.id:
								incentive_amount = line.amount
								for degree_line in incentive.degree_line_ids:
									if self.upgrade_degree in degree_line.degree_ids:
										deserved_amount = degree_line.amount
								break;

					if incentive.calculation_method == 'salary':
						for line in incentive.line_ids:
							if line.employee_id.id == self.employee_id.id:
								incentive_amount = line.salary_amount
								last_payslip = self.env['hr.payslip'].search([('employee_id','=',line.employee_id.id),('state','=','done')])[-1]
								for line in last_payslip.line_ids:
									if line.salary_rule_id == incentive.salary_rule:
										deserved_amount = line.total
										break;
								break;						
					differences_total += deserved_amount - incentive_amount
				self.financial_difference = differences_total

		if self.type == 'annual_bonus':
			first_bonus_amount = second_bonus_amount = 0.00
			if self.first_bonus and self.second_bonus:
				salary_structure = self.env['salary.structure'].search([('is_active','=',True)],limit=1)
				for line in salary_structure.line_ids:
					if line.degree_id.id == self.employee_id.degree_id.id:
						if self.first_bonus:
							if self.first_bonus== 'first_bonus':
								first_bonus_amount = line.primary_category
							if self.first_bonus== 'second_bonus':
								first_bonus_amount = line.second_bonus
							if self.first_bonus== 'third_bonus':
								first_bonus_amount = line.third_bonus
							if self.first_bonus== 'fourth_bonus':
								first_bonus_amount = line.fourth_bonus 
							if self.first_bonus== 'fifth_bonus':
								first_bonus_amount = line.fifth_bonus
							if self.first_bonus== 'sixth_bonus':
								first_bonus_amount = line.sixth_bonus
							if self.first_bonus== 'seventh_bonus':
								first_bonus_amount = line.seventh_bonus
							if self.first_bonus== 'eighth_bonus':
								first_bonus_amount = line.eighth_bonus
							if self.first_bonus== 'ninth_bonus':
								first_bonus_amount = line.ninth_bonus

						if self.second_bonus:
							if self.second_bonus== 'first_bonus':
								second_bonus_amount = line.primary_category
							if self.second_bonus== 'second_bonus':
								second_bonus_amount = line.second_bonus
							if self.second_bonus== 'third_bonus':
								second_bonus_amount = line.third_bonus
							if self.second_bonus== 'fourth_bonus':
								second_bonus_amount = line.fourth_bonus 
							if self.second_bonus== 'fifth_bonus':
								second_bonus_amount = line.fifth_bonus
							if self.second_bonus== 'sixth_bonus':
								second_bonus_amount = line.sixth_bonus
							if self.second_bonus== 'seventh_bonus':
								second_bonus_amount = line.seventh_bonus
							if self.second_bonus== 'eighth_bonus':
								second_bonus_amount = line.eighth_bonus
							if self.second_bonus== 'ninth_bonus':
								second_bonus_amount = line.ninth_bonus

			difference = second_bonus_amount - first_bonus_amount
			self.bonus_amount = difference
			if self.promotion_type == 'first_class':
				self.no_of_months = int(self.days / 30)
				self.financial_difference = self.no_of_months * self.bonus_amount
			elif self.promotion_type == 'second_class':
				last = 0.00
				if self.upgrade_date and self.upgrade_date.day != 1:
					last_day = calendar.monthrange(self.upgrade_date.year,self.upgrade_date.month)[1]
					first_date = datetime.strptime(str(1)+str(self.upgrade_date.month)+str(self.upgrade_date.year), '%d%m%Y').date()
					last_date = datetime.strptime(str(last_day)+str(self.upgrade_date.month)+str(self.upgrade_date.year), '%d%m%Y').date()
					incentives = self.env['hr.incentive'].search(['|','|','&',('date_from','<',first_date),('date_to','>',last_date),'&',('date_from','>=',first_date),('date_from','<=',last_date),'&',('date_to','>=',first_date),('date_to','<=',last_date)])
					no_months = 0.00
					for incentive in incentives:
						incentive_amount = deserved_amount = 0.00
						if incentive.calculation_method == 'salary':
							for line in incentive.line_ids:
								if line.employee_id.id == self.employee_id.id:
									no_months += line.incentive_id.no_months
									break;		

					month_days = 30 - self.upgrade_date.day
					self.financial_difference = no_months * ((self.bonus_amount/30)*month_days)

					incentives = self.env['hr.incentive'].search(['|','|','&',('date_from','<',self.upgrade_date),('date_to','>',self.implementation_date),'&',('date_from','>=',self.upgrade_date),('date_from','<=',self.implementation_date),'&',('date_to','>=',self.upgrade_date),('date_to','<=',self.implementation_date)])
					no_months = 0.00
					for incentive in incentives:
						if incentive.date_from != first_date and incentive.date_to != last_date:
							if incentive.calculation_method == 'salary':
								for line in incentive.line_ids:
									if line.employee_id.id == self.employee_id.id:
										no_months += line.incentive_id.no_months
										break;						
					self.financial_difference += no_months * self.bonus_amount
				else:
					incentives = self.env['hr.incentive'].search(['|','|','&',('date_from','<',self.upgrade_date),('date_to','>',self.implementation_date),'&',('date_from','>=',self.upgrade_date),('date_from','<=',self.implementation_date),'&',('date_to','>=',self.upgrade_date),('date_to','<=',self.implementation_date)])
					no_months = 0.00
					for incentive in incentives:
						if incentive.calculation_method == 'salary':
							for line in incentive.line_ids:
								if line.employee_id.id == self.employee_id.id:
									no_months += line.incentive_id.no_months
									break;						
					self.financial_difference = no_months * self.bonus_amount


		if self.type == 'social_bonus':
			self.bonus_amount = self.allowance_type.amount
			if self.promotion_type == 'first_class':
				self.financial_difference = (self.bonus_amount/30) * self.days
			elif self.promotion_type == 'second_class':
				last = 0.00
				if self.upgrade_date.day != 1:
					last_day = calendar.monthrange(self.upgrade_date.year,self.upgrade_date.month)[1]
					first_date = datetime.strptime(str(1)+str(self.upgrade_date.month)+str(self.upgrade_date.year), '%d%m%Y').date()
					last_date = datetime.strptime(str(last_day)+str(self.upgrade_date.month)+str(self.upgrade_date.year), '%d%m%Y').date()
					incentives = self.env['hr.incentive'].search(['|','|','&',('date_from','<',first_date),('date_to','>',last_date),'&',('date_from','>=',first_date),('date_from','<=',last_date),'&',('date_to','>=',first_date),('date_to','<=',last_date)])
					no_months = 0.00
					for incentive in incentives:
						incentive_amount = deserved_amount = 0.00
						if incentive.calculation_method == 'salary':
							for line in incentive.line_ids:
								if line.employee_id.id == self.employee_id.id:
									no_months += line.incentive_id.no_months
									break;		

					month_days = 30 - self.upgrade_date.day
					self.financial_difference = no_months * ((self.bonus_amount/30)*month_days)

					incentives = self.env['hr.incentive'].search(['|','|','&',('date_from','<',self.upgrade_date),('date_to','>',self.implementation_date),'&',('date_from','>=',self.upgrade_date),('date_from','<=',self.implementation_date),'&',('date_to','>=',self.upgrade_date),('date_to','<=',self.implementation_date)])
					no_months = 0.00
					for incentive in incentives:
						if incentive.date_from != first_date and incentive.date_to != last_date:
							if incentive.calculation_method == 'salary':
								for line in incentive.line_ids:
									if line.employee_id.id == self.employee_id.id:
										no_months += line.incentive_id.no_months
										break;						
					self.financial_difference += no_months * self.bonus_amount
				else:
					incentives = self.env['hr.incentive'].search(['|','|','&',('date_from','<',self.upgrade_date),('date_to','>',self.implementation_date),'&',('date_from','>=',self.upgrade_date),('date_from','<=',self.implementation_date),'&',('date_to','>=',self.upgrade_date),('date_to','<=',self.implementation_date)])
					no_months = 0.00
					for incentive in incentives:
						if incentive.calculation_method == 'salary':
							for line in incentive.line_ids:
								if line.employee_id.id == self.employee_id.id:
									no_months += line.incentive_id.no_months
									break;						
					self.financial_difference = no_months * self.bonus_amount

		if self.type == 'qualification_bonus':
			self.bonus_amount = self.second_qualification.amount - self.first_qualification.amount
			if self.promotion_type == 'first_class':
				self.financial_difference = (self.bonus_amount/30) * self.days
			elif self.promotion_type == 'second_class':
				last = 0.00
				if self.upgrade_date and self.upgrade_date.day != 1:
					last_day = calendar.monthrange(self.upgrade_date.year,self.upgrade_date.month)[1]
					first_date = datetime.strptime(str(1)+str(self.upgrade_date.month)+str(self.upgrade_date.year), '%d%m%Y').date()
					last_date = datetime.strptime(str(last_day)+str(self.upgrade_date.month)+str(self.upgrade_date.year), '%d%m%Y').date()
					incentives = self.env['hr.incentive'].search(['|','|','&',('date_from','<',first_date),('date_to','>',last_date),'&',('date_from','>=',first_date),('date_from','<=',last_date),'&',('date_to','>=',first_date),('date_to','<=',last_date)])
					no_months = 0.00
					for incentive in incentives:
						incentive_amount = deserved_amount = 0.00
						if incentive.calculation_method == 'salary':
							for line in incentive.line_ids:
								if line.employee_id.id == self.employee_id.id:
									no_months += line.incentive_id.no_months
									break;		

					month_days = 30 - self.upgrade_date.day
					self.financial_difference = no_months * ((self.bonus_amount/30)*month_days)

					incentives = self.env['hr.incentive'].search(['|','|','&',('date_from','<',self.upgrade_date),('date_to','>',self.implementation_date),'&',('date_from','>=',self.upgrade_date),('date_from','<=',self.implementation_date),'&',('date_to','>=',self.upgrade_date),('date_to','<=',self.implementation_date)])
					no_months = 0.00
					for incentive in incentives:
						if incentive.date_from != first_date and incentive.date_to != last_date:
							if incentive.calculation_method == 'salary':
								for line in incentive.line_ids:
									if line.employee_id.id == self.employee_id.id:
										no_months += line.incentive_id.no_months
										break;						
					self.financial_difference += no_months * self.bonus_amount
				else:
					incentives = self.env['hr.incentive'].search(['|','|','&',('date_from','<',self.upgrade_date),('date_to','>',self.implementation_date),'&',('date_from','>=',self.upgrade_date),('date_from','<=',self.implementation_date),'&',('date_to','>=',self.upgrade_date),('date_to','<=',self.implementation_date)])
					no_months = 0.00
					for incentive in incentives:
						if incentive.calculation_method == 'salary':
							for line in incentive.line_ids:
								if line.employee_id.id == self.employee_id.id:
									no_months += line.incentive_id.no_months
									break;						
					self.financial_difference = no_months * self.bonus_amount

		if self.type == 'meal_allowance':
			self.financial_difference =  (self.meal_amount/30)*self.days 

		
	def do_submit(self):
		if self.financial_difference == 0:
			raise Warning(_('Financial difference can not be zero'))
		self.state = 'submitted'

	def do_general_directorate(self):
		self.state = 'confirmed'

	def do_hr_general_directorate(self):
		self.state = 'general_directorate'

	def do_confirm(self):
		self.state = 'internal_auditor'

	def do_return(self):
		if self.state == 'submitted':
			self.state = 'draft'
		if self.state == 'confirmed':
			self.state = 'submitted'
		if self.state == 'general_directorate':
			self.state = 'confirmed'
		if self.state == 'internal_auditor':
			self.state = 'general_directorate'

	def do_return1(self):
		if self.state == 'submitted':
			self.state = 'draft'
		if self.state == 'confirmed':
			self.state = 'submitted'
		if self.state == 'general_directorate':
			self.state = 'confirmed'
		if self.state == 'internal_auditor':
			self.state = 'general_directorate'

	def do_return2(self):
		if self.state == 'submitted':
			self.state = 'draft'
		if self.state == 'confirmed':
			self.state = 'submitted'
		if self.state == 'general_directorate':
			self.state = 'confirmed'
		if self.state == 'internal_auditor':
			self.state = 'general_directorate'

	def do_return3(self):
		if self.state == 'submitted':
			self.state = 'draft'
		if self.state == 'confirmed':
			self.state = 'submitted'
		if self.state == 'general_directorate':
			self.state = 'confirmed'
		if self.state == 'internal_auditor':
			self.state = 'general_directorate'

	def do_accounting(self):
		#Delete the old rati 
		for rati in self.env['ratification.ratification'].search([('removing_differences_id','=',self.id)]):
			rati.write({'state':'canceled'})
			rati.sudo().unlink()

		ratification = self.env['ratification.ratification'].create({
			'partner_id':self.employee_id.partner_id.id,
			'state_id':self.employee_id.company_id.id,
			'name':self.name,
			'ratification_type':'salaries_and_benefits',
			'from_hr':True,
			'removing_differences_id':self.id,

			})
		if self.type == 'promotion' or self.type == 'alternative_allowance':
			line_ids_list = []
			tax_ids_list = []
			if self.promotion_type == 'first_class':
				for line in self.line_ids:
					if line.rule.account_id:
						line_ids_list.append({
							'name':line.rule.name,
							'partner_id':self.employee_id.partner_id.id,
							'branch_id':self.employee_id.company_id.id,
							'amount':line.amount,
							'account_id':line.rule.account_id.id,
							'analytic_account_id':line.rule.account_id.parent_budget_item_id.id,
							'ratification_list_id':ratification.id,
							'company_id' : self.env['res.company'].search([('is_main_company','=',True)])[0].id,
							})
					else:
						if line.rule.tax_id:
							tax_ids_list.append({'name':line.rule.name,
								'partner_id':self.employee_id.partner_id.id,
								'tax_id':line.rule.tax_id.id,
								'amount':abs(line.amount),
								})
				ratification.line_ids = line_ids_list
				ratification.tax_ids = tax_ids_list
		else:
			remove_diffrences = self.env['hr.account.config'].search([],limit=1).remove_diffrences
			ratification.line_ids = [{
				'name':self.name,
				'amount':self.financial_difference,
				'account_id':remove_diffrences.id,
				'ratification_id':ratification.id,}]
		self.state = 'accounts'

class RemovingDifferencesLine(models.Model):
	_name="removing.differences.line"

	rule = fields.Many2one('hr.salary.rule')
	old_total = fields.Float()
	new_total = fields.Float()
	differnce_amount = fields.Float(compute='compute_amounts')
	one_day_value = fields.Float(compute='compute_amounts',)
	amount = fields.Float(compute='compute_amounts')
	line_id = fields.Many2one('removing.differences')


	def compute_amounts(self):
		for rec in self:
			rec.differnce_amount = rec.new_total - rec.old_total 
			rec.one_day_value = rec.differnce_amount / 30 
			rec.amount = rec.one_day_value * rec.line_id.days 



	

	




