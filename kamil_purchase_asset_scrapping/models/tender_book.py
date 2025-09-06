# *.* coding:utf-8 *.*

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TenderBook(models.Model):

	_inherit = 'tender.book'

	scrap_id = fields.Many2one('scrap.request')
	asset_line_ids = fields.One2many('tender.book.asset','book_id','Assets')


	@api.model
	def default_get(self, default_fields):
		res = super(TenderBook, self).default_get(default_fields)
		vals = []
		conditions = []
		if self.env.context.get('active_model') == 'scrap.request':
			book = self.env['scrap.request'].browse(self.env.context.get('active_ids'))
			for rec in book.general_conditions_ids:
				conditions.append((0, 0, {
						'id':rec.id,
						'name':rec.name,
					}))

			res['general_conditions_ids'] = conditions
			res['private_conditions'] = book.private_conditions
		return res 


	@api.onchange('scrap_id')
	def onchange_scrap_id(self):
		if not self.scrap_id:
			return 

		scrap = self.scrap_id
		# Create TB lines if nessasary
		asset_lines = []
		for line in scrap.asset_line_ids:
			asset_lines.append((0, 0, line._prepare_tender_book_line(
				asset=line.asset_id)))
		self.asset_line_ids = asset_lines

	@api.multi
	def action_confirm(self):
		self.write({'state':'done'})

	@api.multi
	def action_cancel(self):
		self.write({'state':'cancel'})


class TenderBookAsset(models.Model):

	_name = 'tender.book.asset'
	_description = 'Tender Book Assets'

	asset_id = fields.Many2one('account.asset.asset', 'Assets')
	book_id = fields.Many2one('tender.book')


		
		
