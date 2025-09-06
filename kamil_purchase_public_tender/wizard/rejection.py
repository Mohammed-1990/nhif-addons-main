# *.* codinf:utf-8 *.*

from odoo import models, fields, api

class Rejection(models.TransientModel):
	_name = 'book.rejection'

	name = fields.Text()

	@api.multi
	def action_confirm(self):
		self.ensure_one()
		book= self.env['purchase.order'].browse(self.env.context.get('active_id'))
		book.reason = self.name
		return book.button_cancel()

		