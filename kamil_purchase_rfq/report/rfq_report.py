# -*- coding:utf-8 -*-
from odoo import api, fields, models, tools


class RfqReport(models.Model):
	_name = 'rfq.report'
	_description = 'RFQ Report'
	_auto = False
	_order = 'ordering_date desc, price_total desc'


	ordering_date = fields.Date('Ordering Date', readonly="1")
	user_id = fields.Many2one('res.users', string='Representative', readonly="1")
	admin_id = fields.Many2one('hr.department', string="Administration", readonly="1")
	dept_id = fields.Many2one('hr.department', 'Department', readonly="1")
	state = fields.Selection([
						('draft', 'draft'),
						('sent', 'RFQ Sent'),
						('general_conditions_selection','General Conditions Selection'),
						('technical_selection','Technical Selection'),
						('to approve', 'To Approve'),
						('purchase', 'Purchase Order'),
						('done', 'Locked'),
						('cancel', 'Cancelled'),
						('purchase_department','Purchase Department'),
						('finance_manager','Finance Manager')
						])

	product_id = fields.Many2one('product.product', 'Product', readonly=True)
	partner_id = fields.Many2one('res.partner', 'Vendor', readonly=True)
	rfq_id = fields.Many2one('purchase.rfq', 'Order', readonly=True)
	order_id = fields.Many2one('purchase.order', 'Invoices', readonly=True)
	price_total = fields.Float('Total Price', readonly=True)
	type = fields.Selection([
							('request_for_quotaion','Request For Quotaion(RFQs)'),
							('direct_purchase','Direct Purchase')
							],'Type')
	categ_id = fields.Many2one('product.category', 'Product Category', readonly="1")
	product_qty = fields.Float(string='Quantity',readonly=True)
	company_id = fields.Many2one('res.company', 'Company', readonly=True)



	@api.model_cr
	def init(self):
		# self._table = sale_report
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
			%s
			FROM ( %s )
			%s
			)""" % (self._table, self._select(), self._from(), self._group_by()))

	def _select(self):
		select_str = """
				SELECT
					min(l.id) as id,
					r.id as rfq_id,
					r.company_id as company_id,
					po.id as order_id,
					t.categ_id as categ_id,
					l.product_id as product_id,
					l.product_qty as product_qty,
					partner.id as partner_id,
					r.ordering_date as ordering_date,
					po.state as state,
					r.user_id as user_id,
					r.admin_id as admin_id,
					r.dept_id as dept_id,
					r.type as type,
					sum(l.price_unit * l.product_qty) as price_total					
					
		""" 
		return select_str

	def _from(self):
		from_str = """
				purchase_order_line l
			 	join purchase_order po on (l.order_id=po.id)
			 	join purchase_rfq r on (po.rfq_id=r.id)
					left join product_product p on (l.product_id=p.id)
					left join product_template t on (p.product_tmpl_id=t.id)
					left join res_partner partner on (l.partner_id = partner.id)

		"""
		return from_str

	def _group_by(self):
		group_by_str = """
			GROUP BY
				r.id,
				r.company_id,
				po.id,
				t.categ_id,
				l.product_id,
				l.product_qty,
				partner.id,
				r.ordering_date,
				po.state,
				r.user_id,
				r.admin_id,
				r.dept_id,
				r.type			
		"""
		return group_by_str
