from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime



class kamilContractsContractInherit(models.Model):
	_inherit = 'kamil.contracts.contract'

	study_mission = fields.Many2one('study.mission')

	@api.multi
	def open(self):
		super(kamilContractsContractInherit,self).open()
		if self.study_mission:
			self.study_mission.sudo().write({'state':'confirmed'})
