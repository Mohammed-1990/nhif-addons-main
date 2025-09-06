from odoo import models,fields,api

class totalExecutedInternalAndExternalWizard(models.TransientModel):
	_name="total.executed.internal.and.external.wizard"
	# program_execution_id = fields.Many2one('program.execution')
	date_from = fields.Date()
	date_to = fields.Date()
	country =fields.Many2one("res.country")
	training_type = fields.Many2one('types.short.training')


	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
		"""
		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				'date_from'	: self.date_from,
				'date_to' : self.date_to,
				'country': self.country.id,	
				'training_type':self.training_type.id,
			},
		}


		return self.env.ref('kamil_hr_training.total_executed_internal_and_external_report').report_action(self, data=data)