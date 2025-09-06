from odoo import models,fields,api


class ReportVacancy_busy(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_record_jobs.vacancy_and_busy_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        record_jobs_id = self.env['record.jobs'].search([('id','=',data['form']['record_jobs'])])
        degree_list = []
        for job in record_jobs_id.line_ids:
            if job.employee_degree not in degree_list:
                degree_list.append(job.employee_degree)

        job_list = []
        for job in record_jobs_id.line_ids:
            if job.job not in job_list:
                job_list.append(job.job)

        docs = []
        for degree in degree_list:
            for job in job_list:
                busy_count = 0
                vacancy_count = 0
                for line in record_jobs_id.line_ids:
                    if line.employee_degree == degree and line.job == job:
                        if line.employee_id:
                            busy_count += 1
                        else:
                            vacancy_count += 1
                total = busy_count + vacancy_count
                if total != 0:
                    docs.append({'degree':degree.name,
                        'job':job.name,
                        'busy_count':busy_count,
                        'vacancy_count':vacancy_count,
                        'total':total,
                        })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'name':record_jobs_id.name,
        }