from odoo import models, api
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _update_average_cost(self, product, new_qty, new_price, company):
        """حساب وتحديث متوسط التكلفة للمنتج داخل الشركة المحددة"""
        # الكمية والتكلفة داخل الشركة فقط
        product_company = product.with_context(force_company=company.id)
        current_qty = product_company.qty_available or 0.0
        current_cost = product_company.standard_price or 0.0
        raise ValidationError(current_cost)
        #
        # if current_qty <= 0:
        #     average_cost = new_price
        # else:
        #     total_cost = (current_qty * current_cost) + (new_qty * new_price)
        #     total_qty = current_qty + new_qty
        #     average_cost = total_cost / total_qty
        #
        # # تحديث التكلفة للشركة الحالية فقط
        product_company.write({'standard_price': current_cost})

    def _action_done(self):
        """عند إنهاء حركة المخزون (استلام شراء) يتم تحديث التكلفة لكل شركة"""
        res = super(StockMove, self)._action_done()

        for move in self:
            if move.picking_id.picking_type_id.code == 'incoming':
                product = move.product_id
                qty = move.product_uom_qty
                price_unit = 0.0
                company = move.company_id

                if move.purchase_line_id:
                    price_unit = move.purchase_line_id.price_unit

                if price_unit > 0 and qty > 0 and company:
                    self._update_average_cost(product, qty, price_unit, company)

        return res
