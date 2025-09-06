# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date,datetime
from odoo.exceptions import Warning


class promotionCriteriaRatios(models.Model):
	_name = "promotion.criteria.ratios"
	_inherit = ['mail.thread','mail.activity.mixin',]
	_description = "Promotions Criteria Ratios"
	
	name = fields.Char(default="نسب معايير الترقي", readonly=True, )
	degree_ratio = fields.Float(required=True,)
	appoiontment_ratio = fields.Float(required=True,)
	line_ids = fields.One2many('promotion.criteria.ratios.line','rations_id',string='Details',)	
	
	@api.model
	def create(self, values):
		res = super(promotionCriteriaRatios, self).create(values)
		if self.env['promotion.criteria.ratios'].search([('id','!=',res.id)]):
			raise Warning(_('Can not create more than one record for configuration'))
		return res

class promotionCriteriaRatiosLine(models.Model):
	_name = "promotion.criteria.ratios.line"
	qualifcation = fields.Many2one('qualifcation.type' ,required=True,)
	ratio = fields.Float( required=True,)
	rations_id = fields.Many2one('promotion.criteria.ratios')