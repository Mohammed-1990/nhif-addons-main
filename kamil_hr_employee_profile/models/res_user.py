from odoo import models, fields, api
from datetime import date,datetime
from dateutil.relativedelta import relativedelta	
from odoo.exceptions import Warning


class User(models.Model):
	_inherit = 'res.users'

	email = fields.Char(default='email@example.com')

	@api.multi
	@api.constrains('company_id', 'company_ids')
	def _check_company(self):
		if any(user.company_ids and user.company_id not in user.company_ids for user in self):
			x = 1
            # raise ValidationError(_('The chosen company is not in the allowed companies for this user'))


