from odoo import models,fields,api


class vacancieBusyWizard(models.TransientModel):
	_name="vacancy.busy.wizard"

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

		return self.env.ref('kamil_hr_record_jobs.vacancy_and_busy_report').report_action(self, data=data)
	