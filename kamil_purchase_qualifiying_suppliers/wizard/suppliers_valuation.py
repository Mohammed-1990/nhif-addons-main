# -*-  coding:utf-8 -*-
from odoo import models, fields, api,_


class Valuation(models.TransientModel):
	_name = 'suppliers.valuation'
	_description = 'Suppliers Valuation'

	name = fields.Char(default='Suppliers Valuation')
	area_ids = fields.Many2many('area.rehabilitation', domain=lambda self:self._domain_area())
	book_ids = fields.Many2many('book.filter')


	def _domain_area(self):
		request = self.env['purchase.requisition'].browse(self.env.context.get('active_id'))
		return [('id','in',[v.area_rehabilitation_id.id for v in request.area_rehabilitation_line_ids])]



	@api.onchange('area_ids')
	def _onchange_area_ids(self):
		tender = self.env['purchase.requisition'].search([('tender_book_ids','in',[self._context.get('active_id')])])
		domain = [('requisition_id','=',tender.id)]
		if self.area_ids:
			domain.append(('area_rehab_ids','in',self.area_ids.ids))
		res = {}
		res['domain'] = {'book_ids':domain}
		return res


	def filter_area(self):
		tender = self.env['purchase.requisition'].browse(self._context.get('active_id'))
		self.env['book.filter'].search([]).unlink()

		domain = [('requisition_id','=',tender.id)]
		if self.area_ids:
			domain.append(('area_rehab_ids','in',self.area_ids.ids))
		book = self.env['tender.book'].search(domain)
		val = []
		for line in book:
			value = ''
			state = _('Unqualifier')
			move_posted_check = False
			if line.state not in ['general_conditions_selection','technical_selection','qualifier']:
				value = _('Not matching')
			else:
				value = _('Matching')
			if line.state == 'qualifier':
				move_posted_check = True
				state = _('Qualifier')
			val.append((0, 0, {
				'book_id':line.id,
				'general_conditions_selection':value,
				'partner_id':line.partner_id.id,
				'move_posted_check':move_posted_check,
				'state': state
				}))


		self.book_ids = val



class BookFilter(models.TransientModel):
	_name = 'book.filter'

	book_id = fields.Many2one('tender.book')
	visit_result = fields.Float(related='book_id.visit_result')
	general_conditions_selection = fields.Char()
	area_rehab_ids = fields.Many2many('area.rehabilitation', related='book_id.area_rehab_ids')
	partner_id = fields.Many2one('res.partner')
	state = fields.Char('State', default='Unqualifier')
	move_check = fields.Boolean(default=False)
	move_posted_check = fields.Boolean(default=False)




	@api.multi
	def create_move(self, post_move=True):
		for rec in self:
			rec.move_posted_check = not rec.move_posted_check
			book = self.env['tender.book'].search([('id','=',rec.book_id.id)])
			if rec.move_posted_check:
				book.action_qualifier()
				self.state = 'Qualifier'
			else : 
				book.action_unqualifier()
				self.state = 'Unqualifier'

		