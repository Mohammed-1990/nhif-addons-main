# *.* coding:utf-8 *.*
from odoo import models, fields, api, tools

class ScrapReport(models.Model):
	_name = 'item.card.test'
	_description = 'Item Card Report'
	_auto = False


	date = fields.Datetime('Date')
	product_id = fields.Many2one('product.product', 'Product')
	product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
	product_qty = fields.Float('Quantity')
	product_uom_qty = fields.Float('uom Quantity ')
	product_remaining_qty = fields.Float('Remaining Quantity')
	move_id = fields.Many2one('stock.move', 'Stock Move')
	qty_done = fields.Float(' Quantity Done')
	available_quantity = fields.Float('Available Quantity')
	picking_type_id = fields.Many2one('stock.picking.type','Operation Type')
	location_id = fields.Many2one('stock.location', 'Location')
	state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done')], string='Status')

# sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))

	def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
		with_ = ("WITH %s" % with_clause) if with_clause else ""

		select_ = """
			min(l.id) as id,
			l.product_id as product_id,
			l.move_id as move_id,
			l.product_qty as product_qty,
			sum(l.qty_done) as qty_done,
			l.date as date,
			l.product_uom_id as product_uom_id,
			q.quantity as available_quantity,
			s.picking_type_id as picking_type_id,
			l.state as state,
			s.location_id as location_id,
			s.product_uom_qty as product_uom_qty

		"""

		for field in fields.values():
			select_ += field

		from_ = """
				stock_move_line l
					join stock_move s on (l.move_id=s.id)
					join stock_quant q on(l.product_id=q.product_id and s.location_id=q.location_id)
				%s
		""" % from_clause

		groupby_ = """
				l.product_id,
				l.move_id,
				l.product_qty,
				l.qty_done,
				l.date,
				l.product_uom_id,
				s.picking_type_id,
				s.location_id,
				l.state,
				q.quantity,
				s.product_uom_qty
				%s
		""" % (groupby)

		return '%s (SELECT %s FROM %s WHERE l.id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_)

	@api.model_cr
	def init(self):
		# self._table = scrap_report
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
