from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError

class RatificationComplex(models.TransientModel):
	_name = 'ratification.complex'
	

	name = fields.Char(string='Description')
	date = fields.Date(default=lambda self: fields.Date.today())

	ratification_ids = fields.Many2many('ratification.ratification')

	@api.multi
	def do_merg(self):
		new_list = self.env['ratification.list'].create({
			'name' : self.name,
			'date' : self.date,
			'from_complex':True,
			})

		rat_ids = []

		for rat in self.ratification_ids:
			for line in rat.line_ids:
				if not rat.ratification_list_id:
					line.partner_id = rat.partner_id
				copy_line = line.copy()
				if rat.loan_id:
					self._cr.execute("update ratification_line set loan_id = " + str(rat.loan_id.id) + " where id = " + str(copy_line.id) + " ")
				self._cr.execute("update ratification_line set ratification_list_id = " + str(new_list.id) + " where id = " + str(copy_line.id) + " ")
				self._cr.execute("update ratification_line set ratification_id = Null where id = " + str(copy_line.id) + " ")
			rat.state = 'merging_completed'







