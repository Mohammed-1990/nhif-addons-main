# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
import math
import calendar
from datetime import date,datetime
from dateutil.relativedelta import relativedelta	


################### Data####################
class HRContract(models.Model):
	_name ="hr.contract"
	_inherit = "hr.contract"
	employee_id = fields.Many2one("hr.employee")
	degree_id = fields.Many2one('functional.degree')
	department_id = fields.Many2one('hr.department', related='employee_id.department_id')
	functional_id = fields.Many2one('hr.function', related='employee_id.functional_id')
	primary = fields.Float()
	primary_category = fields.Float()
	second_bonus= fields.Float()
	third_bonus= fields.Float()
	fourth_bonus= fields.Float()
	fifth_bonus= fields.Float()
	sixth_bonus= fields.Float()
	seventh_bonus= fields.Float()
	eighth_bonus= fields.Float()
	ninth_bonus= fields.Float()
	high_cost= fields.Float(string='High cost of living')
	housing_allowance= fields.Float()
	deportation_allowance= fields.Float()
	special_bonus= fields.Float()
	socail_amount = fields.Float()
	education_amount = fields.Float()
	representation_allowance =fields.Float()
	ironically_removed = fields.Float()
	appoiontment_type = fields.Many2one('appointment.type', related='employee_id.appoiontment_type')
	category_id = fields.Many2one('functional.category', related='employee_id.category_id', string="Functional Category")


	
class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	@api.model
	def create(self,vals):
		res = super(HrEmployee,self).create(vals)
		salary_structure = self.env['salary.structure'].search([('is_active','=',True)],limit=1)
		wage = 0.0
		high_cost = 0.0
		housing_allowance = 0.0
		deportation_allowance = 0.0
		representation_allowance = 0.0
		ironically_removed = 0.0
		special_bonus = 0.0
		socail_amount = 0.0
		education_amount = 0.0
		primary = 0.00
		for soical in res.allowances_lines:
			if soical.amount:
				socail_amount = soical.amount
		for edcuction in res.education_lines:
			if edcuction.amount:
				education_amount = edcuction.amount

		if res.degree_id:
			if salary_structure and res.degree_id:
				for line in salary_structure.line_ids:
					if line.degree_id.id == res.degree_id.id:
						high_cost = line.high_cost
						housing_allowance = line.housing_allowance
						deportation_allowance = line.deportation_allowance
						special_bonus = line.special_bonus
						representation_allowance = line.representation_allowance
						ironically_removed = line.ironically_removed
						primary = line.primary_category

						if res.bonus== 'first_bonus':
							wage = line.primary_category
						if res.bonus== 'second_bonus':
							wage = line.second_bonus
						if res.bonus== 'third_bonus':
							wage = line.third_bonus
						if res.bonus== 'fourth_bonus':
							wage = line.fourth_bonus 
						if res.bonus== 'fifth_bonus':
							wage = line.fifth_bonus
						if res.bonus== 'sixth_bonus':
							wage = line.sixth_bonus
						if res.bonus== 'seventh_bonus':
							wage = line.seventh_bonus
						if res.bonus== 'eighth_bonus':
							wage = line.eighth_bonus
						if res.bonus== 'ninth_bonus':
							wage = line.ninth_bonus


					

		values={}
		values.update({'employee_id':res.id,
           'name':'عقد - %s'%res.name,
           'join_date': res.entry_date or date.today(),
           'department_id':res.department_id.id,
           'functional_id':res.functional_id.id,
           'wage':wage,
           'state':'open',
           'high_cost':high_cost,
           'housing_allowance':housing_allowance,
           'deportation_allowance':deportation_allowance,
           'special_bonus':special_bonus,
           'socail_amount' : socail_amount,
           'education_amount' : education_amount,
           'representation_allowance': representation_allowance,
           'ironically_removed': ironically_removed,
           'primary':primary,
           })
		self.env['hr.contract'].create(values)
		return res

	@api.onchange('degree_id','bonus','category_id')
	def update_contract(self):
		salary_structure = self.env['salary.structure'].search([('is_active','=',True)],limit=1)
		wage = 0.0
		high_cost = 0.0
		housing_allowance = 0.0
		deportation_allowance = 0.0
		special_bonus = 0.0
		representation_allowance = 0.00
		ironically_removed = 0.0
		primary = 0.00
		if self.degree_id:
			if salary_structure and self.degree_id:
				for line in salary_structure.line_ids:
					if line.degree_id.id == self.degree_id.id:
						high_cost = line.high_cost
						housing_allowance = line.housing_allowance
						deportation_allowance = line.deportation_allowance
						special_bonus = line.special_bonus
						representation_allowance = line.representation_allowance
						ironically_removed = line.ironically_removed
						primary = line.primary_category
						if self.bonus== 'first_bonus':
							wage = line.primary_category
						if self.bonus== 'second_bonus':
							wage = line.second_bonus
						if self.bonus== 'third_bonus':
							wage = line.third_bonus
						if self.bonus== 'fourth_bonus':
							wage = line.fourth_bonus 
						if self.bonus== 'fifth_bonus':
							wage = line.fifth_bonus
						if self.bonus== 'sixth_bonus':
							wage = line.sixth_bonus
						if self.bonus== 'seventh_bonus':
							wage = line.seventh_bonus
						if self.bonus== 'eighth_bonus':
							wage = line.eighth_bonus
						if self.bonus== 'ninth_bonus':
							wage = line.ninth_bonus

		contract = self.env['hr.contract'].search([('employee_id','=',self._origin.id)],limit=1)
		contract.write({'wage':wage})
		contract.write({'high_cost':high_cost})
		contract.write({'housing_allowance':housing_allowance})
		contract.write({'deportation_allowance':deportation_allowance})
		contract.write({'special_bonus':special_bonus})
		contract.write({'representation_allowance':representation_allowance})
		contract.write({'ironically_removed':ironically_removed})
		contract.write({'primary':primary})


	def update_all_contract(self):
		for rec in self.env['hr.contract'].search([]):
			salary_structure = self.env['salary.structure'].search([('is_active','=',True)],limit=1)
			wage = 0.0
			high_cost = 0.0
			housing_allowance = 0.0
			deportation_allowance = 0.0
			special_bonus = 0.0
			representation_allowance = 0.00
			ironically_removed = 0.0
			primary = 0.00
			if rec.employee_id.degree_id:
				if salary_structure and rec.employee_id.degree_id:
					for line in salary_structure.line_ids:
						if line.degree_id.id == rec.employee_id.degree_id.id:
							high_cost = line.high_cost
							housing_allowance = line.housing_allowance
							deportation_allowance = line.deportation_allowance
							special_bonus = line.special_bonus
							representation_allowance = line.representation_allowance
							ironically_removed = line.ironically_removed
							primary = line.primary_category
							if rec.employee_id.bonus== 'first_bonus':
								wage = line.primary_category
							if rec.employee_id.bonus== 'second_bonus':
								wage = line.second_bonus
							if rec.employee_id.bonus== 'third_bonus':
								wage = line.third_bonus
							if rec.employee_id.bonus== 'fourth_bonus':
								wage = line.fourth_bonus 
							if rec.employee_id.bonus== 'fifth_bonus':
								wage = line.fifth_bonus
							if rec.employee_id.bonus== 'sixth_bonus':
								wage = line.sixth_bonus
							if rec.employee_id.bonus== 'seventh_bonus':
								wage = line.seventh_bonus
							if rec.employee_id.bonus== 'eighth_bonus':
								wage = line.eighth_bonus
							if rec.employee_id.bonus== 'ninth_bonus':
								wage = line.ninth_bonus
			rec.write({'wage':wage})
			rec.write({'high_cost':high_cost})
			rec.write({'housing_allowance':housing_allowance})
			rec.write({'deportation_allowance':deportation_allowance})
			rec.write({'special_bonus':special_bonus})
			rec.write({'representation_allowance':representation_allowance})
			rec.write({'ironically_removed':ironically_removed})
			rec.write({'primary':primary})
					

class HrPayslip(models.Model):
	_name="hr.payslip"
	_inherit = "hr.payslip"



	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.contract_id = self.employee_id.contract_id
			self.functional_id = self.employee_id.contract_id.functional_id
			self.struct_id = self.employee_id.contract_id.struct_id


