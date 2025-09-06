# -*- coding:utf-8 -*-
from odoo import models, fields, api	


class Collection(models.Model):
	_inherit = 'collection.collection'

	scrap_id = fields.Many2one('scrap.request','Scrap')
	scrap_line_id = fields.Many2one('scrap.request.line')


	# @api.multi
	# def do_audit(self):
	# 	res = super(Collection, self).do_audit()
	# 	if self.is_tender:
	# 		if self.scrap_id:
	# 			if self.tender_type == 'scrap':
	# 				self.scrap_id.prepare_book(self.partner_id, self.scrap_id, self.id)
	# 	return res
	# 	