# *.* encoding:utf-8 *.*

from odoo import models, fields, api

class RepresentativeAttendance(models.TransientModel):

	_name = 'representative.attendance'
	_description = 'representative attendance'

	name = fields.Char('Name', required=True)
	phone = fields.Char('Phone')
	email = fields.Char('Email')
	book_id = fields.Many2one('tender.book', 'Book Number')
	order_id = fields.Many2one('purchase.order' , ' Book Number')
	tender_id = fields.Many2one('purchase.requisition')
	partner_id = fields.Many2one('res.partner', 'Company Name',)
	vendor_name = fields.Char(related='book_id.vendor_name')
	type = fields.Selection(related='tender_id.type')

	street = fields.Char('Street')
	street2 = fields.Char('Street2')
	zip = fields.Char('Zip', change_default=True)
	city = fields.Char('City')
	state_id = fields.Many2one("res.country.state", string='State')
	country_id = fields.Many2one('res.country', string='Country')
	phone = fields.Char('Phone', track_visibility='onchange', track_sequence=5)
	mobile = fields.Char('Mobile')
	title = fields.Many2one('res.partner.title')


	@api.onchange('book_id')
	def onchange_book_id(self):
		self.partner_id = self.book_id.partner_id

	@api.onchange('order_id')
	def onchange_order_id(self):
		self.partner_id = self.order_id.partner_id

	@api.multi
	def create_representative_attendance(self):
		rep_attendee = self.env['rep.attendee'].browse(self.env.context.get('active_ids'))
		partner = self.env['res.partner']
		val = []
		val.append((0,0 ,{
				'name':self.name,
				'phone':self.phone,
				'email':self.email,
				'street':self.street,
				'street2':self.street2,
				'zip':self.zip,
				'city':self.city,
				'state_id':self.state_id.id,
				'country_id':self.country_id.id,
				'type':'contact'
				}))

		id = 0
		if type == 'qualifying_suppliers':
			id = self.book_id.partner_id.id
		else:
			id = self.order_id.partner_id.id

		pr = self.env['res.partner'].search([('id','=',id)])

		pr.write({'child_ids':val})
		rep_attendee.create({
				'name':self.name,
				'phone':self.phone,
				'email':self.email,
				'tender_id':self.tender_id.id,
				'vendor_name':self.vendor_name,
				'book_id':self.book_id.id,
				'street':self.street,
				'street2':self.street2,
				'zip':self.zip,
				'city':self.city,
				'state_id':self.state_id.id,
				'country_id':self.country_id.id,
				'tender_id':self.tender_id.id,
				'book_id':self.book_id.id,
				'order_id':self.order_id.id
				
			})
