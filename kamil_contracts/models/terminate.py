# -*- coding: utf-8 -*-

from odoo import models, fields, api


class KamilContractProjectTerminationRequest(models.Model):
	_name = 'kamil.contracts.termination_requests'
	_description = 'Contract Termination'
	_order = 'id desc'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']	
	
	# @api.multi
	# def button_submit(self):
	# 	for rec in self:
	# 		rec.contract_id.contract_period = rec.contract_id.contract_period +  rec.Period

	# 	rec.write({'state': 'done'})

	# function of history
	@api.multi
	def history_term_project(self):
		return{
			'name': (''),
			'domain':[],
			'view_type':'form',
			'res_model':'kamil.contract.project.termination_request',
			'view_id':False,
			'view_mode':'tree,form',
			'type':'ir.actions.act_window',
		}

	# state = fields.Selection([('draft', 'draft'),('done', 'Done'), ], 'Status', readonly=True, copy=False, required=True, default='submit', track_visibility="always")        
	name = fields.Char('Name', track_visibility="always", readonly=True)

	contract_id = fields.Many2one('kamil.contracts.contract','Reffrence', required=True, track_visibility="always")
	
	contracts_date = fields.Date('Contract Date', default=lambda self: fields.Date.today(), track_visibility="always")

	subject = fields.Char('Subject', track_visibility="always")
	the_body_of_the_message = fields.Html()	
	applicant = fields.Many2one('res.users',string='Applicant Name', required=True, default= lambda self: self.env.user, track_visibility="always")
	# app_name=fields.Char(related='applicant.name')
	# adjective = fields.Many2one('hr.function',related="applicant.functional_id", readonly=True)
	attachment_ids = fields.One2many('kamil.contracts.termination.attachments','attachment_id',string='Attachment', track_visibility="always")
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	ter=fields.Char('Termination of /')
	# Period = fields.Integer(size=2, string=' termination Period')
	# attachment = fields.Binary()
	state = fields.Selection([('draft', 'Draft'),
		('req_term','Termination request'),
		('manager','GM Approval'),
		('legal_study','Legal Study'),
		('committe','Committe'),
		('terminated','Terminated'),
		('cancel','Canceled') ], 'Status', default='draft', track_visibility="always")


	@api.multi
	def req_term(self):
		self.write({'state':'req_term'}) 
		self.name=str(self.ter)+str(self.contract_id.name)+' Contract'

	@api.multi
	def manager(self):
		self.write({'state':'manager'}) 
	@api.multi
	def legal_study(self):
		self.write({'state':'legal_study'}) 

	@api.multi
	def committe(self):
		self.write({'state':'committe'}) 


	@api.multi
	def terminated(self):
		self.write({'state':'terminated'}) 

		for rec in self:
			self.contract_id.contract_end_date=self.contracts_date
			self.contract_id.state='terminated'
		


	@api.multi
	def cancel(self):
		self.write({'state':'cancel'}) 


class kamilContractAttachments(models.Model):
	_name = 'kamil.contracts.termination.attachments'

	attachment_name = fields.Char(string='Attachment Name', required=True, track_visibility="always")
	attachment_id =fields.Many2one('kamil.contracts.termination_requests', track_visibility="always", ondelete='restrict')
	attachment = fields.Binary( track_visibility="always")
	