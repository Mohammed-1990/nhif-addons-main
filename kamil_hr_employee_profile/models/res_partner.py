from odoo import models, fields, api
from datetime import date,datetime
from dateutil.relativedelta import relativedelta	
from odoo.exceptions import Warning


class resPartner(models.Model):
	_inherit = "res.partner"

	is_employee = fields.Boolean()
	signup_token = fields.Char(copy=False, groups="base.group_user")
	signup_type = fields.Char(string='Signup Token Type', copy=False, groups="base.group_user")
	signup_expiration = fields.Datetime(copy=False, groups="base.group_user")

