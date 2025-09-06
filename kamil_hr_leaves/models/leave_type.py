# -*- coding: utf-8 -*-
from odoo import models, fields, api

class leavesType(models.Model):
	_inherit = 'hr.leave.type'

	name = fields.Char('Leave Type', required=True,)

	allocation_type = fields.Selection([
        ('fixed', 'Fixed by HR'),
        ('no', 'No allocation')],
        default='fixed', string='Balance',)

	timesheet_generate = fields.Boolean('Generate Timesheet', default=False, help="If checked, when validating a leave, timesheet will be generated in the Vacation Project of the company.")

	documents = fields.Boolean('Requires attaching documents')
	document = fields.Many2many('document.document',string="Documents Names")


	union_leave = fields.Boolean('Trade union leave')

	
	available_gender = fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , default='no', string="Is it for a specific gender")

	gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default="male")

	available_marital = fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , default='no', string="Is it for a specific marital")

	marital = fields.Selection([('single','SINHLE'),('married','Married'),('widowre','Widowre'),('divorced','Divorced')])



	religion = fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , default='no', string='Is it a specific religion')
	religion_id = fields.Many2many('religion.model',)
	
	can_cut = fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , default='no')
	
	save_remaining = fields.Selection([
		('yes' , 'Yes'),
		('no' , 'No')] , string="Can save the remaining" , default='no')

	unpaid = fields.Boolean('Is Unpaid', default=False)

	can_saved = fields.Selection([('yes','Yes'),('no','No')],string="Can be saved", default='no')
	duration = fields.Integer("Duration of preservation in months")
	request_duration = fields.Integer("Maximum request duration by months")
	stop_incentive = fields.Selection([('yes','Yes'),('no','No')],"Stop the incentive",default='no')
	can_acting = fields.Selection([('yes','Yes'),('no','No')],"Can Acting",default='no')
	appoiontment_type=fields.Many2many('appointment.type',track_visibility="onchange")
	annually = fields.Boolean()
	local = fields.Boolean()
	allocate_duration = fields.Integer(string="Allocation Days")

	@api.onchange('annually')
	def onchange_annually(self):
		self.local = False
		


