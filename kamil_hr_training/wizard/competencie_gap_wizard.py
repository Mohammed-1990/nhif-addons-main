from odoo import models, fields ,api ,_
from odoo.exceptions import Warning


class CompetencieGapWizard(models.TransientModel):
	_name="competencie.gap.wizard"
	date_from = fields.Date()
	date_to = fields.Date()
	competencie_id = fields.Many2one('competencie.model',)
	gap_from = fields.Float('Gap percentage from', required=True,)
	gap_to = fields.Float('To', required=True,)

	
	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		if self.gap_from == 0.00 and self.gap_to == 0.00:
			raise Warning(_('Please enter gap percentage range'))
		data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'competencie_id': self.competencie_id.id,
                'gap_from':self.gap_from,
                'gap_to':self.gap_to,
            },
            
        }

		return self.env.ref('kamil_hr_training.competencie_gap_report').report_action(self, data=data)
	
