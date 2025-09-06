from odoo import models,fields,api


class ReportFunction(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_structure.administrative_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        domain = []
        if data['form']['department_id']:
            domain.append(('id','child_of',data['form']['department_id']))


        docs = []
        for department in self.env['hr.department'].search(domain):
            docs.append({
                'department':department.name,
                'management':department.parent_id.name,
                'manager':department.manager_id.name,})            

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }