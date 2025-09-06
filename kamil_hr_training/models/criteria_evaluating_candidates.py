from odoo import models, fields, api,_
from odoo.exceptions import Warning
from datetime import date, datetime



class Criteria_evaluating(models.Model):
	_name='criteria.evaluating'
	_inherit = ['mail.thread','mail.activity.mixin']
	
	name=fields.Char(required=True,)
	percentage = fields.Float(required=True,)


