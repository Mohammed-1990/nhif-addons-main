# -*- coding: utf-8 -*-
from odoo import models, fields, api

class leavesType(models.Model):
	_inherit = 'hr.leave.type'
	limited_period = fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , default='no')


	period = fields.Integer('Period')

	should_allocted= fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , default='no')

	doc = fields.Boolean('Attaching Document')
	union_leave = fields.Boolean('Trade union leave')

	can_cut = fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , default='no')
	
	available_gender = fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , default='no')
	type_gender =  fields.Selection([
		('male' , 'Male'),
		('female' , 'Female')] , default='female')

	available_religion = fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , default='no')
	shoot_down = fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , string="You Can Drop the saved leave" , default='no' )

	period_saved = fields.Integer("Period Saved")
	unpaid = fields.Boolean('Is Unpaid', default=False)


class leaveAllocation(models.Model):
	_inherit = "hr.leave.allocation"

	holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('company', 'By Company'),
        ('department', 'By Department'),
        ('category', 'By Employee Tag'),
        ('degree','By Degrees'),
        ('fun_cag',('By Functional Category'))],
        string='Allocation Mode', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category')
	degree_id = fields.Many2one("functional.degree",string='Degree')
	functional_id = fields.Many2one("functional.category", string='Functional Category')

    # @api.onchange('holiday_type')
    # def _onchange_type(self):
    #     if self.holiday_type == 'employee':
    #         if not self.employee_id:
    #             self.employee_id = self.env.user.employee_ids[:1].id
    #         self.mode_company_id = False
    #         self.category_id = False
    #     elif self.holiday_type == 'company':
    #         self.employee_id = False
    #         if not self.mode_company_id:
    #             self.mode_company_id = self.env.user.company_id.id
    #         self.category_id = False
    #     elif self.holiday_type == 'department':
    #         self.employee_id = False
    #         self.mode_company_id = False
    #         self.category_id = False
    #         if not self.department_id:
    #             self.department_id = self.env.user.employee_ids[:1].department_id.id
    #     elif self.holiday_type == 'category':
    #         self.employee_id = False
    #         self.mode_company_id = False
    #         self.department_id = False