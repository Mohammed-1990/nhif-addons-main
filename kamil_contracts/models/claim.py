# -*- coding: utf-8 -*-

from odoo import models, fields, api

class KamilContractExtensionRequest(models.Model):
	_name = 'kamil.contracts.claim'
	_description = 'Contract claim'
	_order = 'id desc'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']
	
	name = fields.Selection([('purchase_management','Purchase Management'),('administrative_affairs','Administrative Affairs'),('planning_department','Planning Department')])
	contract_id = fields.Many2one('kamil.contracts.project','Reffrence')
	administration_concerned = fields.Selection([('purchase_management','Purchase Management'),('administrative_affairs','Administrative Affairs'),('planning_department','Planning Department')])
	subject = fields.Char('subject')
	the_body_of_the_message = fields.Html()	
	applicant = fields.Char('Applicant')
	adjective = fields.Char('Adjective')
	Period = fields.Date()
	attachment = fields.Binary()
	claim_ids = fields.One2many('kamil.contracts.claim_lines','claim_contract_id','kamil.contracts.claim')
	state = fields.Selection([('purchasing_committee','Purchasing Committee'),('managing_director','Managing Director'),('committee_president','Committee President'),('sub_administration','Sub Administration')])
	panalty_ids = fields.One2many('kamil.contracts.project.panalty_lines','proj_contract_id','kamil.contracts.claim')

class claim_lines(models.Model):
	_name = 'kamil.contracts.claim_lines'

	name = fields.Char('Name')
	amount = fields.Float('Amount')
	date = fields.Datetime('Date', default=lambda self: fields.Datetime.now())
	state = fields.Char('State', default="Submit")
	percentage = fields.Integer('Percentage%')
	panalty_basis = fields.Selection([('cont_per','Contract %'),('phase_per','Phase %'),('fixed_amont','Fixed amount')])
	claim_contract_id = fields.Many2one('kamil.contracts.claim')

	# _sql_constraints = [('claim_lines_name_uniqe', 'unique (name)','Sorry ! you can not create same name')]

# class panalty_clause(models.Model):
# 	_name = 'kamil.contracts.project.panalty_lines'

# 	panalty_name = fields.Char('Name')
# 	panalty_amount = fields.Float('Amount')
# 	affect_date = fields.Date('Date')
# 	active = fields.Boolean('Active')
# 	percentage = fields.Integer('Percentage%')
# 	proj_contract_id = fields.Many2one('kamil.contracts.project')
