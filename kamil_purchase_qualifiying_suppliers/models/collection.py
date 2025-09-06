# *.* coding:utf-8 *.*
from odoo import models, fields, api

class Collection(models.Model):
	_inherit = 'collection.collection'

	operation_type = fields.Selection(selection_add=[
							('qualifying_suppliers','Qualifying Suppliers'),
							('public_tender','Public Tender'),
							('limited_tender','Limited Tender'),
							])
	tender_id = fields.Many2one('purchase.requisition', 'Tender')
	
	
	@api.multi
	def do_audit(self):
		res = super(Collection, self).do_audit()
		if self.tender_id:
			if self.operation_type in ('qualifying_suppliers','public_tender','limited_tender'):
				self.tender_id.prepare_book(self.partner_id, self.tender_id, self.id)
		return res
		