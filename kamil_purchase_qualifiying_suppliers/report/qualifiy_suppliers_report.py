from odoo import models,fields,api
import time
import datetime

class ReportPublicTender(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_purchase_qualifiying_suppliers.suppliers_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        # area_id = data['form']['area_id']
        # if area_id:
        #     domain.append(('area_id','=',area_id))

        suppliers = self.env['res.partner'].search([])
        area_rehabilitation = self.env['area.rehabilitation'].search([])

        docs = []
        for supp in suppliers:
            area = ''
            for rec in area_rehabilitation:
                area = area +'-' + rec.name
            if supp.qualified == True:
                docs.append({
                    'name': supp.name,
                    'area': area,
                })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            # 'area_id': area_id,
        }