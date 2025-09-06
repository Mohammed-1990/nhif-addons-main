from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from datetime import date, datetime


class recipients_performance_wiz(models.TransientModel):
    _name = 'recipients.performance.wiz'

    collector = fields.Many2one(
        comodel_name='hr.employee',
        string='Collector',
        required=True)
    date_from = fields.Date(
        string='Date from',
        required=True, default = lambda self: date(date.today().year, date.today().month, 1))
    date_to = fields.Date(
        string='Date to',
        required=True, default = lambda self: date(date.today().year, date.today().month, 30))

    @api.multi
    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'from': {
                'collector_id' : self.collector.id,
                'collector_name': self.collector.name,
                'date_from' : self.date_from,
                'date_to' : self.date_to,
            },
        }

        return self.env.ref('kamil_accounting_reports.report_recipients_performance').report_action(self, data=data)
