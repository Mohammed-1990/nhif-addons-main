# *.* coding:utf-8 *.*

from odoo import models, fields, api

class Partner(models.Model):

	_inherit = 'res.partner'
	
	requisition_id = fields.Many2one('purchase.requisition','Tender')
	book_id = fields.Many2one('tender.book' , 'Tender Book')
	qualified = fields.Boolean('Is Qualified')
	area_rehabilitation_ids = fields.Many2many('area.rehabilitation','partner_rel','partner_id','area_id')
	visit_id = fields.Many2one('tender.book.visit','Visit')


	
