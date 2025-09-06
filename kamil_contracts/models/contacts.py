from odoo import models, fields, api
# from datetime import date,datetime
# from dateutil.relativedelta import relativedelta	
# from odoo.exceptions import Warning


class inheritContacts(models.Model):
	_inherit = "res.partner"
	part = fields.Selection([
		('presidency','Presidency'),
		('branch','Branch'),
		('center','Center')],)