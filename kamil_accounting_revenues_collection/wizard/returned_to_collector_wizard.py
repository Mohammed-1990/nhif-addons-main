from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class Return_Receipt_E15Wizard(models.TransientModel):
    _name ='returned.collector.e15.wizard'

    returned_reason = fields.Text(string='Returned Reason', required=True,track_visibility='always')
    receipt_67_id= fields.Many2one('collection.receipt_67', string='Receipt 67')

    @api.multi
    def returned_collector_receipt_e15(self):
        for record in self.receipt_67_id:
            for  line in record.collection_ids:
                 if line:
                     line.write({'state':'returned_to_collector',
                                 'returned_reason':'returned_reason',
                                 })
            record.write({'state':'returned_to_collector'})

        # if self.collection_id:
        #     self.collection_id.write({'returned_reason': self.returned_reason})






