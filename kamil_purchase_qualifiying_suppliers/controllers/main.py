# *.* coding:utf-8 *.*
from odoo import http
from odoo.http import request
from datetime import datetime


class TenderBook(http.Controller):

	@http.route('/tenderbook/<int:id>/', auth='public', website=True)
	def Index(self, id):
		book = request.env['tender.book'].search([('id','=',id)])
		return http.request.render('kamil_purchase_qualifiying_suppliers.index',{'book': book})

	@http.route('/success/', auth='public', website=True)
	def success(self, **kw):
		return http.request.render('kamil_purchase_qualifiying_suppliers.success')


	@http.route('/tenderbook/add/', auth='public')
	def add(self, **kw):
		book = request.env['tender.book'].search([('id','=',kw['book_id'])])
		vals = {
			'name':kw['name'],
			'phone':kw['phone'],
			'mobile':kw['mobile'],
			'email':kw['email'],
			'website':kw['website'],
			'street':kw['street'],
			'street2':kw['street2'],
			'city':kw['city'],
			'state_id':kw['state'],
			'country_id':kw['country'],
			}
		book.partner_id.write(vals)
		book.write({
		'other_features':kw['other_features'],
		# 'terms':kw['terms_txt'],
		'area_rehab_ids':[(6,0,[kw['area']])],
		'received_date':datetime.now()
		})	
		book.send_email_done()
