# *.* coding:utf-8 *.*

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseVisitTemplate(models.TransientModel):
	_name = 'tender.visit.template'
	_description = 'Tender visit template'

	visit_line_ids = fields.One2many('tender.visit.line','visit_template_id')
	requisition_id = fields.Many2one('purchase.requisition' , 'Requisition')



	def action_confirm(self):	
		if not self.visit_line_ids:
			raise UserError(_("The visit line is not exist please entered."))	
		val = []
		requisition = self.env['purchase.requisition'].browse(self.env.context.get('active_ids'))
		for rec in self.visit_line_ids:
			val.append((0, 0, {
				'criteria_id':rec.criteria_id.id,
				'required_score':rec.required_score
				}))

		visit = self.env['visit.template']
		visit = visit.create({
					'name':self.env['ir.sequence'].next_by_code('visit.template'),
					'visit_ids': val
					})
		
		self.requisition_id.write({'visit_id': visit.id})
		


		
class VisitLine(models.TransientModel):
	_name = 'tender.visit.line'
	_description = 'Tender visit Line'

	visit_template_id = fields.Many2one('tender.visit.template')

	criteria_id = fields.Many2one('tender.book.visit.criteria')
	required_score = fields.Float('Required Score')
