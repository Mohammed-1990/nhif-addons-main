from odoo import models,fields,api
import time
import datetime

class ReportStockInventory(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_inventory.stock_inventory_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        # domain = []
        location_id = data['form']['location_id']
        # if location_id:
        #     domain.append(('location_id', '=', location_id))

        stock_qty = self.env['stock.quant'].search(
            [])
        product_id = self.env['product.template'].search([])

        docs = []
        for qty in stock_qty:
            if qty.location_id.usage in ['customer', 'internal']:
                if str(qty.location_id) == location_id:
                    if qty.product_id.active == True:
                        docs.append({
                            'product': qty.product_id.name,
                            'location': qty.location_id.name,
                            'quantity': qty.quantity,
                            'uom': qty.product_uom_id.name,
                            'reserved': qty.reserved_quantity,
                            'categ': qty.categ_id.name,
                        })
                

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'location_id': location_id,
        }
