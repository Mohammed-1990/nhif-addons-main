from odoo import models,fields,api


class functionWizard(models.TransientModel):
	_name="function.wizard"

	record_jobs_id = fields.Many2one('record.jobs',string='Record Jobs',required=True,)

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'record_jobs_id': self.record_jobs_id.id,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_hr_record_jobs.functions_report').report_action(self, data=data)
	
	