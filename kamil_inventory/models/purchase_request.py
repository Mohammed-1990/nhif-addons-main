
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class purchaseRequest(models.Model):
    _inherit = 'purchase.request'


    need_request_id = fields.Many2one('need.requisition')


class purchaseOrder(models.Model):
    _inherit = 'purchase.order'


    stock_location_id = fields.Many2one('stock.location', string='Stock Location', domain=[('usage','ilike','internal')])

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_total': amount_untaxed ,
            })


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    including_tax = fields.Float(
        string="Including Tax",
        compute="_compute_including_tax",
        store=True
    )

    @api.depends('price_unit', 'product_qty', 'taxes_id')
    def _compute_including_tax(self):
        for line in self:
            if line.taxes_id:
                line.price_unit = line.price_unit + ( line.price_unit  * sum(line.taxes_id.mapped('amount')) /100)
            else:
                # مافي ضرائب → يبقى المبلغ بدون ضريبة
                line.price_unit = line.price_unit
