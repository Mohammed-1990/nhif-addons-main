# *.*  coding:utf-8 *.*

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError, AccessError


class LimitedTender(models.Model):

	_inherit = 'purchase.requisition'

	recipients_ids = fields.Many2many('res.partner',string='Qualifier Suppliers')

	@api.model
	def create(self, vals):
		if self._context.get('default_type') == 'limited_tender':
			seq_code = 'purchase.requisitioin.limited.tenders' + '-' + str(datetime.now().year) + '-' + '.'
			seq = self.env['ir.sequence'].next_by_code( seq_code )
			if not seq:
				self.env['ir.sequence'].create({
					'name' : seq_code,
					'code' : seq_code,
					'prefix' :  'LT-' +str(datetime.now().year) + '-',
					'number_next' : 1,
					'number_increment' : 1,
					'use_date_range' : True,
					'padding' : 4,
					})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
			vals['sequence'] = seq
		return super(LimitedTender, self).create(vals)


	@api.multi
	def action_confirm_announcment(self):
		if self.type == 'limited_tender':
			if not any(rec.recipients_ids for rec in self):
				raise UserError(_('You have to set at least one qualifier suppliers !'))
		

		return super(LimitedTender, self).action_confirm_announcment()