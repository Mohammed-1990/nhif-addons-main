# *.* coding:utf-8 *.*
from odoo import models, fields, api, tools

class RevenuesBudgetReport(models.Model):
	_name = 'revenues.budget.report'
	_description = 'Scrap Report'
	_auto = False

	date_from = fields.Date('Ordering Date')
	date_to = fields.Date('Deadline Date')
	budget_id = fields.Many2one('crossovered.budget', string='Budget')
	budget_item_id = fields.Many2one('account.analytic.account', string="Budget Item")
	planned_amount = fields.Float('Planned Amount')
	practical_amount = fields.Float('Practical Amount')
	remaining_value = fields.Float('remaining Value')
	percentage = fields.Float('Percentage')

	def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
		with_ = ("WITH %s" % with_clause) if with_clause else ""

		select_ = """
			min(l.id) as id,
			s.id as budget_id,
			l.id as budget_item_id,
			l.planned_amount as planned_amount
		"""

		for field in fields.values():
			select_ += field

		from_ = """
				crossovered_budget_lines l
					join crossovered_budget s on (l.revenues_budget_id=s.id)
						
				%s
		""" % from_clause

		groupby_ = """
				s.id,
				l.id		
				%s
		""" % (groupby)

		return '%s (SELECT %s FROM %s WHERE l.id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_)

	@api.model_cr
	def init(self):
		# self._table = scrap_report
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
