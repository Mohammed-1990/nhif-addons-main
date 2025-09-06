# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#
# Please note that these reports are not multi-currency !!!
#

from odoo import api, fields, models, tools


class QualifyingSuppliersReport(models.Model):
	_name = "purchase.qualifying.suppliers.report"
	_description = "Qualifying Suppliers Report"
	_auto = False

	requisition_id = fields.Many2one('purchase.requisition', '# Tender')
	date = fields.Datetime('Order Date', readonly=True)
	deadline_date = fields.Datetime('deadline Date', readonly=True)
	user_id = fields.Many2one('Represntative', readonly=True)
	admin_id = fields.Many2one('hr.department', string="Administration", readonly="1")
	dept_id = fields.Many2one('hr.department', 'Department', readonly="1")
	area_id = fields.Many2one('area.rehabilitation', 'Area of rehabilitation', readonly=True)
	book_id = fields.Many2one('tender.book', '# Books', readonly=True)
	rep_attendee_id = fields.Many2one('rep.attendee', 'Rep attendee', readonly=True)
	partner_id = fields.Many2one('res.partner', 'Supplier', readonly=True)
	pr_state = fields.Selection([
							('draft','Draft'),
							('finance_admin_purchase_dept)','Administration and Financial Manager /Purchase Department'),
							('gen_man_appr','General Manager Approval'),
							('announcement','Announcement'),
							('comm_decided','Committee Decided'),
							('general_conditions_selection','General Conditions Selection'),
							('suppliers_valuation','Suppliers Valuation'),
							('finance_admin_apprv','Administration and Financial Manager Approval'),
							('gm_sign','General Manager Signature'),
							('internal_refrance','Internal Refrance'),
							('in_progress','In Progress'),
							('ongoing', 'Ongoing'),
							('in_progress', 'Confirmed'),
							('open', 'Bid Selection'),
							('done','Done'),
							('cancel','Cancel'),
							],string='Tender State')
	book_state = fields.Selection([
					('draft','Draft'),
					('general_conditions_selection','General Conditions Selection'),
					('technical_selection','Technical Selection'),
					('to approve', 'To Approve'),
					('confirm','Confirm'),
					('qualifier','Qualifier'),
					('unqualifier','Unqualifier'),
					('done','Done'),
					('cancel','Cancel')
					], string='Book State')


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
					min(r.id) as id,
					l.vendor_rehabilitation_id as requisition_id,
					area.id as area_id,
					b.id as book_id,
					r.ordering_date as date,
					r.date_end as deadline_date,
					r.state as pr_state,
					b.state as book_state,
					ap.res_partner_id as partner_id,
					r.user_id as user_id
					
					
		""" 
		return select_str

	def _from(self):
		from_str = """
			 purchase_requisition r 
				join area_rehabilitation_line l on (l.vendor_rehabilitation_id=r.id)
					left join area_rehabilitation area on (l.area_rehabilitation_id=area.id)
					left join tender_book b on (r.id=b.requisition_id)
					left join area_rel ar on ar.tender_book_id = b.id and ar.area_rehabilitation_id = area.id
					left join area_rehabilitation_line_res_partner_rel ap on ap.res_partner_id = b.partner_id and ap.area_rehabilitation_line_id = l.id

		"""
		return from_str

	def _group_by(self):
		group_by_str = """
			GROUP BY
				l.vendor_rehabilitation_id,
				l.area_rehabilitation_id,
				area.id,
				b.id,
				r.ordering_date,
				r.date_end,
				r.state,
				b.state,
				ap.res_partner_id,
				r.user_id
				
		"""
		return group_by_str
