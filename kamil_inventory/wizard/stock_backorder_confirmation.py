# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class StockBackorderConfirmation(models.TransientModel):
	_inherit = 'stock.backorder.confirmation'
	

	@api.one
	def _process(self, cancel_backorder=False):
		res = super(StockBackorderConfirmation,self)._process()
		need_request_id = [pick.need_request_id.id for pick in self.pick_ids ][0]
		for pick_id in self.pick_ids:
			backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', pick_id.id)])
			backorder_pick.write({'need_request_id':need_request_id})
		return res 
