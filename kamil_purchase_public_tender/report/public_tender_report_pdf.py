from odoo import models,fields,api
import time
import datetime

class ReportPublicTender(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_purchase_public_tender.public_tender_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        public_tender = self.env['purchase.requisition'].search([('type','=','public_tender'),('ordering_date','>=',date_from),('ordering_date','<=',date_to)])
        public_tender_invoice = self.env['purchase.order'].search([])
        attendee = self.env['rep.attendee'].search([])
        docs = []
        for purchase in public_tender:
            for invoice in public_tender_invoice:
                prod = ''
                prod_qty = ''
                attendee_name = ''
                for inv in invoice.order_line:
                    prod = prod + '\n' + inv.product_id.name
                    prod_qty = prod_qty + '\n' + str(inv.product_qty)
                for atte in attendee:
                    if atte.order_id.name == invoice.name:
                        attendee_name = atte.name
                if invoice.origin == purchase.name:
                    if invoice.state == 'purchase':
                        docs.append({
                            'sequence': purchase.sequence,
                            'date': purchase.ordering_date,
                            'name': purchase.name,
                            'user': purchase.user_id.name,
                            'invoice_no': invoice.name,
                            'attendee_name': attendee_name,
                            'product': prod,
                            'product_qty': prod_qty,
                            'taxes': invoice.amount_tax,
                            'total': invoice.amount_total,
                            'partner': invoice.partner_id.name,
                        })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
        }

