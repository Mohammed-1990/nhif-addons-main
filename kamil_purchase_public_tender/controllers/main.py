# *.* coding:utf-8 *.*

from datetime import datetime, time

from odoo import http
from odoo.http import request
from datetime import datetime

				
class book(http.Controller):

	@http.route('/book/<int:id>/', auth='public',website=True)
	def index(self, id):
		book = request.env['purchase.order'].search([('id','=',id)])
		return http.request.render('kamil_purchase_public_tender.index',{'book':book})

	@http.route('/book/add/', auth='public')
	def add(self, **kw):
		book = request.env['purchase.order'].search([('id','=',kw['book_id'])])
		product_list = []
		sp1 =  kw['price'].split(';',1)
		sp2 = sp1[1].rsplit(';')
		sp3 = sp2[0].split(',')

		list_val = []



		for rec in sp2:
			val = rec.split(',')
			# length = len(val)
			if val[0]:
				print('\n\n\n')
				print(val)
				print(val[2])
				print('\n\n\n')
				for line in book.requisition_id.line_ids:
					if line.schedule_date:
						date_planned = datetime.combine(line.schedule_date, time.min)
					else:
						date_planned = datetime.now()
						
					if(int(val[0]) == line.product_id.id):
						product = request.env['product.product'].search([('id','=',int(val[0]))])
						list_val.append((0,0,
							{
							'name': product.display_name,
							'product_id':int(val[0]),
							'product_uom':product.uom_po_id.id,
							'product_qty':float(val[1]),
							'price_unit':float(val[2]),
							'date_planned':date_planned,
							'account_analytic_id':line.account_analytic_id.id,
							'analytic_tag_ids':line.analytic_tag_ids.ids,
							'move_dest_ids': line.move_dest_id and [(4, line.move_dest_id.id)] or []
							}))
		book.order_line.unlink()
		book.write({'order_line':list_val})

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
			'terms':kw['terms_txt'],
			})			
		# book.send_email_done()

		

	@http.route('/success/', auth='public', website=True)
	def success(self, **kw):
		return http.request.render('kamil_purchase_public_tender.success')