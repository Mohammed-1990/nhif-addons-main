# *.* coding:utf-8 *.*

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizGeneralConsitions(models.TransientModel):

	_name = 'wiz.general.conditions'
	_description = 'Wiz general conditions'

	book_id = fields.Many2one('tender.book',string='tender')
	condtions_ids = fields.Many2many('pr.general.conditions','wiz_general_conditon_rel')
	select_all = fields.Boolean('Select All')

	@api.model
	def default_get(self, default_fields):
		res = super(WizGeneralConsitions, self).default_get(default_fields)
		vals = []

		book = self.env['tender.book'].browse(self.env.context.get('active_ids'))
		res['condtions_ids'] = [(6, 0, [v.id for v in book.general_conditions_ids])]
		return res

	@api.onchange('select_all')
	def onchange_select_all(self):
		for rec in self.condtions_ids:
			if self.select_all:
				rec.exist = self.select_all
			

	def action_confirm(self):
		book = self.env['tender.book'].browse(self.env.context.get('active_ids'))
		book.write({'general_conditions_ids': [(6,0, [v.id for v in self.condtions_ids])]})
		if book.state == 'draft':
			return book.action_check_general_conditions()
		if book.state == 'general_conditions_selection':
			for line in self.condtions_ids:
				if not line.exist:
					raise UserError(_("This order is not check '%s' exist.") % line.name)
				if not line.attachments:
					raise UserError(_("This order is missing '%s' attachments.") % line.name)
			return book.action_technical_selection()


		