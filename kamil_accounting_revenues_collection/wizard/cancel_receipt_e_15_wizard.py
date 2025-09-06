from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class Cancel_Receipt_E15Wizard(models.TransientModel):
    _name ='cancel.receipt.e15.wizard'

    date_cancel = fields.Date(default=lambda self: fields.Date.today(),readonly=True)
    collection_id = fields.Many2one("collection.collection",readonly=True)
    cancel_reason = fields.Text(string='Cancel Reason', required=True,track_visibility='always')


    @api.multi
    def get_cancel_receipt_e15(self):
        if self.collection_id:
            self.collection_id.write({'cancel_e15_state': 'send'})
            self.collection_id.write({'is_cancel_receipt_e15': True})
            self.collection_id.write({'cancel_reason': self.cancel_reason})






