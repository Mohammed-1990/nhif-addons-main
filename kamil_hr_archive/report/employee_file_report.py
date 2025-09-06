from odoo import models,fields,api
from datetime import date,datetime
from dateutil.relativedelta import relativedelta


class ReportEmployeeFile(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_archive.employee_file_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        employee_ids = data['form']['employee_ids']

        domain = []
        if employee_ids:
            domain.append(('employee_id','in',employee_ids))

        docs = []
        for archive in self.env['archive.archive'].search(domain):
            docs.append({
                'employee_no': archive.employee_id.number,
                'employee': archive.employee_id.name,
                'branch' : archive.branch_id.name,
                'file_no': archive.file_no,
                'closet_no': archive.closet_no,
                'box_no': archive.box_no,
                
                })
       

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }