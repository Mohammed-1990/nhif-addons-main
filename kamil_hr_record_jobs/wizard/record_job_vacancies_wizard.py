from odoo import models,fields,api


class vacanciesWizard(models.TransientModel):
	_name="vacancies.wizard"

	record_jobs = fields.Many2one('record.jobs',string='Record Jobs',required=True,)


	@api.multi
	def get_report(self):
		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
			'record_jobs': self.record_jobs.id,
			},
			}

		return self.env.ref('kamil_hr_record_jobs.vacancies_report').report_action(self, data=data)
	