from odoo import models,fields,api
import time
import datetime

class ReportPurchaseRfq(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_purchase_rfq.purchase_rfq_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        purchase_rfq = self.env['purchase.rfq'].search([('type','=','request_for_quotaion'),('ordering_date','>=',date_from),('ordering_date','<=',date_to)])
        purchase_rfq_invoice = self.env['purchase.order'].search([])
        docs = []
        for purchase in purchase_rfq:
            for invoice in purchase_rfq_invoice:
                prod = ''
                prod_qty = ''
                for inv in invoice.order_line:
                    prod = prod + '\n' + inv.product_id.name
                    prod_qty = prod_qty + '\n' + str(inv.product_qty)
                if invoice.origin == purchase.sequence:
                    if invoice.state == 'purchase':
                        docs.append({
                            'date': purchase.ordering_date,
                            'name': purchase.name,
                            'user': purchase.user_id.name,
                            'invoice_no': invoice.name,
                            'invoice_date': invoice.date_order,
                            'supplier': invoice.partner_id.name,
                            'product': prod,
                            'product_qty': prod_qty,
                            'taxes': invoice.amount_tax,
                            'total':invoice.amount_total,
                        })
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
        }


