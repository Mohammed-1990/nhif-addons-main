from odoo import models,fields,api


class ReportVacancies(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_record_jobs.vacancies_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        record_jobs_id = self.env['record.jobs'].search([('id','=',data['form']['record_jobs'])])

        docs = []
        job_title_list = []
        number=1
        for job in record_jobs_id.line_ids:
            if not job.employee_id :
                job_title_list.append(job.job)
                docs.append({'job_number':job.job_number,'number':number,'job':job.job.name,'employee_degree':job.employee_degree.name})
                number+=1

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'name':record_jobs_id.name,
        }