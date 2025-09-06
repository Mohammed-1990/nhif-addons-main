from odoo import models, fields ,api,_
from odoo.exceptions import Warning

class detailedPostgraduateStudiesWizard(models.TransientModel):
	_name="detailed.postgraduate.studies.wizard"

	# mission_id = fields.Many2one('study.mission')
	employee_id = fields.Many2one('hr.employee')
	date_from = fields.Date()
	date_to = fields.Date()
	specialization = fields.Many2one('university.specialization')
	university_id = fields.Many2one('university.model')
	country =fields.Many2one("res.country")
		
	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
		"""
		data = {
			'ids': self.ids,
			'model': self._name,
			'form': {
				# 'mission_id':self.mission_id.id,
				'employee_id': self.employee_id.id,
				'date_from':self.date_from,
				'date_to':self.date_to,
				'specialization':self.specialization.id,
				'university_id':self.university_id.id,
				'country':self.country.id,
					},

				}


		return self.env.ref('kamil_hr_training.detailed_postgraduate_studies_report').report_action(self, data=data)