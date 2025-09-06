# *.* coding:utf-8 *.*

from odoo import models, fields, api

class WizAreaRehabilitaion(models.TransientModel):
	_name = 'wiz.area.rehabilitaion'

	book_id = fields.Many2one('tender.book')
	area_ids = fields.Many2many('area.rehabilitation','wiz_area_rel', string='Area of rehabilitation')

	@api.model
	def default_get(self, default_fields):
		res = super(WizAreaRehabilitaion, self).default_get(default_fields)
		vals = []
		book = self.env['tender.book'].browse(self.env.context.get('active_ids'))
		for line in book.area_rehab_ids:
			vals.append((6, 0, {
					'id':line.id,             
				}))
		res['area_ids'] = vals	
		return res 



	@api.multi
	def action_confirm(self):
		book = self.env['tender.book'].browse(self.env.context.get('active_ids'))
		book.write({'area_rehab_ids': [(6,0, [v.id for v in self.area_ids])]})
		return book.action_qualifier()

