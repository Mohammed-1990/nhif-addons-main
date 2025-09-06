from odoo import models,fields,api


class ReportFunction(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_record_jobs.functions_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        record_jobs_id = self.env['record.jobs'].search([('id','=',data['form']['record_jobs_id'])])

        docs = []
        job_title_list = []
        for job in record_jobs_id.line_ids:
            if job.job not in job_title_list:
                job_title_list.append(job.job)
        for job in job_title_list:
            count = 0
            for line in record_jobs_id.line_ids:
                if job == line.job:
                    count +=1
            docs.append({'function':job.name,
                'count':count,})

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'name':record_jobs_id.name,
        }