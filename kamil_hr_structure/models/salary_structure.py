# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from openerp.exceptions import Warning


class salaryStructure(models.Model):
	_name = "salary.structure"
	name = fields.Char(string="Description" ,required =True)
	is_active = fields.Boolean(string='Active', default=True, store=True, readonly=False)
	is_old_structure = fields.Boolean(default=False, store=True, readonly=False)
	appoiontment_type_ids = fields.Many2many('appointment.type', )
	line_ids = fields.One2many("salary.structure.line","detail_id")

	@api.onchange('is_old_structure')
	def _onchange_is_old_structure(self):
		if self.is_old_structure == True:
			if self.env['salary.structure'].search([('id','!=',self._origin.id),('is_old_structure','=',True)]):
				raise Warning(_('Can not add more than one old structure'))
	    

	def update_all_contract(self):
		domain = []
		appoiontment_list = []
		category_list = []
		if self.appoiontment_type_ids:
			for appoiontment in self.appoiontment_type_ids:
				if appoiontment.id not in appoiontment_list:
					appoiontment_list.append(appoiontment.id)

			domain.append(('appoiontment_type','in',appoiontment_list))

		for rec in self.env['hr.contract'].search(domain):
			salary_structure = self.env['salary.structure'].search([('is_active','=',True)],limit=1)
			wage = 0.0
			high_cost = 0.0
			housing_allowance = 0.0
			deportation_allowance = 0.0
			special_bonus = 0.0
			representation_allowance = 0.00
			ironically_removed = 0.0
			primary = 0.00
			if rec.sudo().employee_id.degree_id:
				if salary_structure and rec.sudo().employee_id.degree_id:
					for line in salary_structure.line_ids:
						if line.degree_id.id == rec.sudo().employee_id.degree_id.id:
							high_cost = line.high_cost
							housing_allowance = line.housing_allowance
							deportation_allowance = line.deportation_allowance
							special_bonus = line.special_bonus
							representation_allowance = line.representation_allowance
							ironically_removed = line.ironically_removed
							primary = line.primary_category
							if rec.employee_id.sudo().bonus== 'first_bonus':
								wage = line.primary_category
							if rec.employee_id.sudo().bonus== 'second_bonus':
								wage = line.second_bonus
							if rec.employee_id.sudo().bonus== 'third_bonus':
								wage = line.third_bonus
							if rec.employee_id.sudo().bonus== 'fourth_bonus':
								wage = line.fourth_bonus 
							if rec.employee_id.sudo().bonus== 'fifth_bonus':
								wage = line.fifth_bonus
							if rec.employee_id.sudo().bonus== 'sixth_bonus':
								wage = line.sixth_bonus
							if rec.employee_id.sudo().bonus== 'seventh_bonus':
								wage = line.seventh_bonus
							if rec.employee_id.sudo().bonus== 'eighth_bonus':
								wage = line.eighth_bonus
							if rec.employee_id.sudo().bonus== 'ninth_bonus':
								wage = line.ninth_bonus
				rec.write({'wage':wage})
				rec.write({'high_cost':high_cost})
				rec.write({'housing_allowance':housing_allowance})
				rec.write({'deportation_allowance':deportation_allowance})
				rec.write({'special_bonus':special_bonus})
				rec.write({'representation_allowance':representation_allowance})
				rec.write({'ironically_removed':ironically_removed})
				rec.write({'primary':primary})

	def toggle_active(self):
		if self.is_active == True:
			self.is_active = False
		elif self.is_active == False:
			if self.env['salary.structure'].search([('is_active','=',True)]):
				raise Warning(_("You can't activate more than one salary structure"))
			self.is_active = True

class detailsLine(models.Model):
	_name = "salary.structure.line"
	degree_id = fields.Many2one('functional.degree' , required=True,)
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
	minimum_bonus= fields.Float()
	special_bonus= fields.Float()
	representation_allowance =fields.Float()
	ironically_removed = fields.Float()
	
	detail_id = fields.Many2one('salary.structure' , string= "Details")