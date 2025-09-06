# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class CommitteeConfiguration(models.Model):
    _name = 'committee.configuration'


    name = fields.Char("Committee Name")
    types = fields.Selection([('purchase','Purchase'),('inventory','Inventory')],string="Committee Type")

    _rec_name = 'name'
	

class KamilHrEmployeeLine(models.Model):
	_name = 'hr.employee.line'

	employee = fields.Many2one('hr.employee',string="Employee", required=True)
	role = fields.Selection([('chairman','Chairman'),('secratary','Secratary'),('member','Member')],string="Position", required=True)
	committee = fields.Many2one('committee.committee')



class CommitteeCommittee(models.Model):
	_name = 'committee.committee'

	committee_type = fields.Many2one('committee.configuration', string="Committee Type", required=True)
	committee_member = fields.One2many('hr.employee.line','committee',string="Committee Members")
	state = fields.Selection([('draft','Draft'),
							  ('active','Active'),
							  ('cancelled','Cancelled'),
							  ('expired','Expired')],string="State",default='draft')
	start_date=fields.Date(string="Start Date", required=True)
	end_date=fields.Date(string="End Date", required=True)

	_rec_name = 'committee_type'

	@api.multi
	def accept_team(self):
		if self.state == 'draft':
			self.write({'state':'active'})

	@api.multi
	def cancel_team(self):
		if self.state in ('draft','active'):
			self.write({'state':'cancelled'})

	@api.multi
	def check_expire_record(self):
		today_date = datetime.now().date()
		records = self.env['committee.committee'].search([])
		for recs in records:
			if recs.end_date < today_date:
				recs.write({'state': 'expired'})

