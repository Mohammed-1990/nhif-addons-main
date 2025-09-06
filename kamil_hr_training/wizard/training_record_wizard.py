from odoo import models, fields ,api,_
from odoo.exceptions import Warning


class trainingRecordWizard(models.TransientModel):
	_name="training.record.wizard"
	program_execution_id = fields.Many2one('program.execution',)
	date_from = fields.Date()
	date_to = fields.Date()
	training_center = fields.Many2one('training.center')
	country =fields.Many2one("res.country")

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
		"""
		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				'program_execution_id': self.program_execution_id.id,	
				'date_from'	: self.date_from,
				'date_to' : self.date_to,
				'training_center': self.training_center.id,
				'country': self.country.id,	
			},
		}

		return self.env.ref('kamil_hr_training.training_record_report').report_action(self, data=data)
