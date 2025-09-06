# -*- coding: utf-8 -*-

from openerp import models, fields, api,_
from odoo.exceptions import  Warning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class hrProjects(models.Model):
	_name = 'hr.projects'
	_order = "id desc"
	_inherit = ['mail.thread','mail.activity.mixin']
	
	name = fields.Char(required=True,track_visibility="onchange")
	amount = fields.Float('Max Amount',required=True,track_visibility="onchange")
	total_amount = fields.Float('Total Amount', readonly=True, compute='_compute_total_amount', track_visibility="onchange")
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
	max_quantity = fields.Integer(required=True, default=1,track_visibility="onchange")
	no_month = fields.Integer(string="No Of installments (By Months)", default=1,required=True,track_visibility="onchange")
	number_varieties = fields.Boolean('Number from varieties', default=False,track_visibility="onchange")
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('closed','Closed')], default='draft',track_visibility="onchange")
	line_ids = fields.One2many('hr.projects.line','projects_id',string='Projects Lines',)
	incentive_id = fields.Many2one("incentive.type", required=True, domain=[('duration','=','monthly'), ],track_visibility="onchange")
	deduct_account = fields.Many2one('account.tax',track_visibility="onchange")
	
	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise Warning(_('Project request cannot be deleted in a case other than draft'))
		return models.Model.unlink(self)

	def do_confirm(self):
		self.state = 'confirmed'

	def do_close(self):
		self.state = 'closed'

	def set_to_draft(self):
		self.state = 'draft'

	@api.onchange('line_ids')
	def _compute_total_amount(self):
		for rec in self:
			total = 0.00
			for line in rec.line_ids:
				total += line.amount
			rec.total_amount = total

	@api.onchange('payment_start_date')
	def _onchange_payment_start_date(self):
		if self.payment_start_date and self.payment_start_date < date.today():
			raise Warning(_('Payment start date cannot be less than today'))        

class hrProjectsLines(models.Model):
	_name = 'hr.projects.line'
	name = fields.Char('Varietie name', required=True,track_visibility="onchange")
	amount = fields.Float('Amount',required=True,track_visibility="onchange")
	max_quantity = fields.Integer(required=True, default=1)
	no_month = fields.Integer(string="No Of installments (By Months)", default=1,required=True,track_visibility="onchange")
	projects_id = fields.Many2one('hr.projects', string="HR Projects", ondelete='cascade')
	















