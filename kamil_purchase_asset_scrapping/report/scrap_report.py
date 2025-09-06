# *.* coding:utf-8 *.*
from odoo import models, fields, api, tools

class ScrapReport(models.Model):
	_name = 'scrap.report'
	_description = 'Scrap Report'
	_auto = False

	scrap_id = fields.Many2one('scrap.request', 'Scrap', readonly=True)
	ordering_date = fields.Date('Ordering Date')
	user_id = fields.Many2one('res.users', string='Representative', readonly=True)
	admin_id = fields.Many2one('hr.department', string="Administration", readonly="1")
	dept_id = fields.Many2one('hr.department', 'Department', readonly="1")
	asset_id = fields.Many2one('account.asset.asset', 'Assets')
	book_id = fields.Many2one('tender.book','Books')
	partner_id = fields.Many2one('res.partner', 'Customer', readonly="1")
	estimated_value = fields.Float('Estimated Value')
	sales_value = fields.Float('Selling Value')
	company_id = fields.Many2one('res.company','State')
	product_id = fields.Many2one('product.product','Product', readonly="1")
	state = fields.Selection([('draft','Draft'),
							('manager_director','Manager Director'),
							('gen_man_appr','General Manager Approval'),
							('director_finance_admin','Director and finance and administrative'),
							('announcement','Announcement'),
							('comm_decided','Committee Decided'),
							('auction','Auction'),
							('finance_admin_apprv','Administration and Financial Manager Approval'),
							('finance_manger_apprv','Financial Manager Approval'),
							('done','Done'),
							('cancel','Cancel'),
							],'Status')

	
	def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
		with_ = ("WITH %s" % with_clause) if with_clause else ""

		select_ = """
			min(l.id) as id,
			s.id as scrap_id,
			s.state as state,
			partner.id as partner_id,
			s.ordering_date as ordering_date,
			s.user_id as user_id,
			s.admin_id as admin_id,
			s.dept_id as dept_id,
			aa.id as asset_id,
			aa.product_id as product_id,
			aa.company_id as company_id,
			sum(l.estimated_value) as estimated_value,
			sum(l.sales_value) as sales_value
		"""

		for field in fields.values():
			select_ += field

		from_ = """
				scrap_request_line l
					join scrap_request s on (l.scarp_request_id=s.id)
						left join collection_collection c on (c.scrap_id= s.id)
						left join res_partner partner on l.partner_id = partner.id
						left join scrap_asset_ref sa on (sa.scrap_request_line_id=l.id)
						left join account_asset_asset aa on (sa.account_asset_asset_id=aa.id)

				%s
		""" % from_clause

		groupby_ = """
				s.id,
				s.state,			
				partner.id,
				s.ordering_date,
				s.user_id,
				s.admin_id,
				s.dept_id,
				aa.id,
				aa.company_id,
				aa.product_id
				%s
		""" % (groupby)

		return '%s (SELECT %s FROM %s WHERE l.id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_)

	@api.model_cr
	def init(self):
		# self._table = scrap_report
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
