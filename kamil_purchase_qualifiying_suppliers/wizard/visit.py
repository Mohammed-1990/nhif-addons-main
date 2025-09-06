# *.* coding:utf-8 *.*
from odoo import models, fields, api
from datetime import datetime


class Visit(models.TransientModel):
	
	_name = 'book.visit'
	_description ='Book Visit'

	year = fields.Char('Year', default=datetime.now().year, readonly=True)
	book_id = fields.Many2one('tender.book')
	partner_id = fields.Many2one('res.partner', related='book_id.partner_id')
	visit_line_ids = fields.One2many('book.visit.line', 'visit_id')

	@api.model
	def default_get(self, default_fields):
		res = super(Visit, self).default_get(default_fields)
		vals = []
		book = self.env['tender.book'].browse(self.env.context.get('active_id'))
		for line in book.requisition_id.visit_id.visit_ids:
			vals.append((0 ,0, {
					'criteria_id':line.criteria_id.id,
					'required_score': line.required_score
				}))
		res['visit_line_ids'] = vals
		return res

	@api.multi
	def create_field_visit_report(self):
		val =[]
		book = self.env['tender.book'].browse(self.env.context.get('active_id'))

		for rec in self.visit_line_ids:
			val.append((0,0,{
					'criteria_id':rec.criteria_id.id,
					'required_score':rec.required_score,
					'obtained_score':rec.obtained_score,
					'note':rec.note
				}))
		tender_book_visit = self.env['tender.book.visit']
		visit = tender_book_visit.create({
					'sequence':self.env['ir.sequence'].next_by_code('tender.book.visit'),
					'year':self.year,
					'partner_id':self.partner_id.name,
					'book_id':self.book_id.id,
					'visit_line_ids': val

					})
		book.write({'visit_id':visit.id,'visit_result':sum([v.obtained_score for v in self.visit_line_ids])})
		# return self.book_id.action_confirm_book()
		

		
class VisitLine(models.TransientModel):

	_name = 'book.visit.line'
	_description = 'book visit line'

	visit_id = fields.Many2one('book.visit')
	visit_template_id = fields.Many2one('field.visit.template')
	criteria_id = fields.Many2one('tender.book.visit.criteria')
	required_score = fields.Float('Required Score')
	obtained_score = fields.Float('Obtained Score')
	note = fields.Text('Notes') 
				
