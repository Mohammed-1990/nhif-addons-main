from odoo import models, fields, api
from datetime import date,datetime
from dateutil.relativedelta import relativedelta	
from odoo.exceptions import Warning

class resCompany(models.Model):
	_inherit = "res.company"

	is_main_company = fields.Boolean('Main Company')