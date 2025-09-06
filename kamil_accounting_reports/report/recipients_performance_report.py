from odoo import fields, models, api


class ModelName(models.AbstractModel):
    _name = 'report.kamil_accounting_reports.recipients_performance_template'

    def get_template_data(self, collector_id, date_from, date_to):
        sum = []
        self.env.cr.execute("SELECT c.ref, r.name, c.date, c.amount, rc.name  FROM collection_collection as c JOIN res_partner as r ON r.id = c.partner_id JOIN res_currency as rc ON rc.id = c.currency_id where c.collector_id = " + collector_id + " AND c.date >=  '" + str(date_from) + "' AND c.date <=  '" + str(date_to) + "'")
        for i in self.env.cr.fetchall():
            sum.append(i)
        print(sum)
        return sum

    @api.model
    def _get_report_values(self, docids, data=None):
        collector = data['from']['collector_name']
        date_from = data['from']['date_from']
        date_to = data['from']['date_to']
        company_id_logo = self.env.user.company_id.logo

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'data': data,
            'company_id_logo': company_id_logo,
            'get_template_data': self.get_template_data,
        }