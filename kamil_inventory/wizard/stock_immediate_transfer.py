# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
	_inherit = 'stock.immediate.transfer'

	text_str = fields.Text()
	
	# @api.model
	def default_get(self, default_fields):
		res = super(StockImmediateTransfer, self).default_get(default_fields)
		stock_picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
		text = ""
		if self.env.context.get('state',False) == 'initial':
			# text = _("You have not recorded confirm quantities yet, by clicking on apply system will process all the initial quantities 0.0 .")
			raise UserError( _('You can not connfirm request because all initial quantities is 0.0 !!'))
		else:
			if self.env.context.get('state',False):
				# text = _("You have not recorded confirm quantities yet, by clicking on apply system will process all the quality quantities 0.0 .")
				raise UserError(_('You can not connfirm request because all quality quantities is 0.0 !!'))

			else:
				# text = _("You have not recorded done quantities yet, by clicking on apply system will process all the reserved quantities 0.0 .")
				raise UserError(_('You can not connfirm request because all reserved quantities is 0.0 !!'))

		return res 

	# def process(self):
	# 	for picking in self.pick_ids:
	# 		if picking.custome_state == 'initial' and picking.picking_type_id.code == 'incoming':
	# 			raise UserError(text)
	# 		if picking.custome_state == 'quality' and picking.picking_type_id.code == 'incoming':
	# 			raise UserError(text)
	# 		if picking.state == 'assigned' and picking.picking_type_id.code == 'outgoing':
	# 			raise UserError(text)
	# 			picking.state = 'done'
	# 			picking.need_request_id.state = 'done'
	# 			return False
	# 	return super(StockImmediateTransfer,self).process()
