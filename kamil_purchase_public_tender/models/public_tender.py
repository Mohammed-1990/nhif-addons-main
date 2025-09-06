# *.* coding:utf-8 *.*

from odoo import models, fields, api
from datetime import datetime, date

class PublicTender(models.Model):

	_inherit = 'purchase.requisition'

	READONLY_STATES = {
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}


	type = fields.Selection([('qualifying_suppliers','Qualifying Suppliers'),
							('public_tender','Public Tender'),
							('limited_tender','Limited Tender'),
							('direct_purchase','Direct Purchase')],
							'Type'
							)
	admin_id = fields.Many2one('hr.department', string="Administration", states=READONLY_STATES)
	dept_id = fields.Many2one('hr.department', 'Department', states=READONLY_STATES)
	request_ids = fields.Many2many('purchase.request',string='Requests')



	@api.model
	def create(self, vals):
		if self._context.get('default_type') == 'public_tender':
			seq_code = 'purchase.requisitioin.public.tenders' + '-' + str(datetime.now().year) + '-' + '.'
			seq = self.env['ir.sequence'].next_by_code( seq_code )
			if not seq:
				self.env['ir.sequence'].create({
					'name' : seq_code,
					'code' : seq_code,
					'prefix' :  'PT-' +str(datetime.now().year) + '-',
					'number_next' : 1,
					'number_increment' : 1,
					'use_date_range' : True,
					'padding' : 4,
					})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
			vals['sequence'] = seq
		return super(PublicTender, self).create(vals)




	# @api.multi	
	# def action_set_announcment(self):
	# 	res = super(PublicTender, self).action_set_announcment()
	# 	if self.type == 'public_tender':

		
	# 	# self.origin = self.env['ir.sequence'].next_by_code('purchase.requisitioin.public.tenders', context=context) 
	# 		# self.name = self.origin + ' / ' + self.name 
	# 		if self.ordering_date:
	# 			seq_code = 'purchase.requisitioin.public.tenders' + str(self.ordering_date.year) + ' / '+ '.' + str(self.name) +'.' + str(self.ordering_date.month)+ ' / ' +'.'
	# 			seq = self.env['ir.sequence'].next_by_code( seq_code )
	# 			if not seq:
	# 				self.env['ir.sequence'].create({
	# 					'name' : seq_code,
	# 					'code' : seq_code,
	# 					'prefix' : 'PT / ' + str(self.name) + ' / '+  str(self.ordering_date.year) + '-' +  str(self.ordering_date.month) + '-' ,
	# 					'number_next' : 1,
	# 					'number_increment' : 1,
	# 					'use_date_range' : True,
	# 					'padding' : 4,
	# 					})
	# 				seq = self.env['ir.sequence'].next_by_code( seq_code )
	# 			self.name = seq
	# 	return res

	# @api.model
	# def create(self, vals):
	# 	create_id = super(PublicTender, self).create(vals)
	# 	if create_id.ordering_date:
	# 		seq_code = 'purchase.requisitioin.public.tenders' + str(create_id.date.year) + ' / '+ '.' + str(create_id.name) +'.' + str(create_id.date.month)+ ' / ' +'.'
	# 		seq = self.env['ir.sequence'].next_by_code( seq_code )
	# 		if not seq:
	# 			self.env['ir.sequence'].create({
	# 				'name' : seq_code,
	# 				'code' : seq_code,
	# 				'prefix' : 'PT / ' + str(create_id.name) + ' / '+  str(create_id.date.year) + '-' +  str(create_id.date.month) + '-' ,
	# 				'number_next' : 1,
	# 				'number_increment' : 1,
	# 				'use_date_range' : True,
	# 				'padding' : 4,
	# 				})
	# 			seq = self.env['ir.sequence'].next_by_code( seq_code )
	# 		create_id.ref = seq 

	# 	return create_id

		# res = super(PurchaseRequest, self).create(vals)
		# return res

	@api.multi
	def action_internal_refrance(self):
		for record in self:
			for line in record.request_ids:
				line.state = 'done'
		self.write({'state':'done'})