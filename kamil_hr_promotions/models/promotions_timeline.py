# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date,datetime
from odoo.exceptions import Warning


class promotionsTimeline(models.Model):
	_name = "promotions.timeline"
	_inherit = ['mail.thread','mail.activity.mixin',]
	_description = "Promotions Timeline"
	
	name = fields.Char(required=True,)
	line_ids = fields.One2many('promotions.timeline.line','timeline_id',string='Details',)	
	state = fields.Selection([
		('draft','Draft'),
		('validated','Validated'),
		('cancelled','Cancelled'),], default='draft', track_visibility="onchange")

	def do_validate(self):
		# change state to validated
		if not self.line_ids:
			raise Warning(_('Please! enter details for promotions timeline'))

		if self.env['record.jobs'].search([('state','=','validated')]):
			raise Warning(_('You cannot confirm more than one'))
		self.state = 'validated'

	def do_cancel(self):
		# change state to cancelled
		self.state = 'cancelled'



class promotionsTimelineLine(models.Model):
	_name = "promotions.timeline.line"
	
	category_id = fields.Many2many('functional.category',string='Functional Category', required=True,)
	from_degree_id = fields.Many2one('functional.degree', required=True, )
	to_degree_id = fields.Many2one('functional.degree', required=True,)
	years = fields.Integer('Number of years', required=True,)
	timeline_id = fields.Many2one('promotions.timeline',string='Field Label',)




