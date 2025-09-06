# -*- coding: utf-8 -*-

from odoo import models, fields, api

class hrDepartment(models.Model):
	_inherit =  "hr.department"
	name = fields.Char('Department Name', required=True, track_visibility='onchange')
	parent_id = fields.Many2one('hr.department', string='Parent Department', index=True, track_visibility='onchange')
	type = fields.Selection([('department','Department'),('sub_management','Sub - management'),('general_administration','General Administration'),('branch','Branch'),
		('executive_unit','Executive unit'),('center','Center'),
		('lab','Lab'),('pharmacy','Pharmacy'),('general_manger','General Manger')], required=True, track_visibility='onchange')
