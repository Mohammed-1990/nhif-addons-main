# *.* coding:utf-8 *.*

from odoo import models, fields, api

class FieldsVisitTemplate(models.TransientModel):

	_name = 'field.visit.template'
	_description = 'FieldsVisitTempate'

	visit_line_ids = fields.One2many('book.visit.line','visit_template_id')
	requisition_id = fields.Many2one('purchase.requisition')
	select_all = fields.Boolean('Select All')


	@api.multi
	def create_field_visit_report(self):
		val =[]
		requisition = self.env['purchase.requisition'].search([('id','=',self.requisition_id.id)])
		for rec in self.visit_line_ids:
			val.append((0,0,{
					'criteria_id':rec.criteria_id.id,
					'required_score':rec.required_score,
					
				}))
		visit = self.env['visit.template'].create({'name':self.requisition_id.name,'visit_ids':val})
		requisition.visit_id = visit.id

		return True
		