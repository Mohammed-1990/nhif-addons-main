from odoo import models,fields,api,_ 

class Partner(models.Model):
	_inherit = 'res.partner'

	insured_ids = fields.One2many('collection.subscriber', 'partner_id')
	is_subscriber = fields.Boolean()


class Subscriber(models.Model):
	_name = 'collection.subscriber'

	insured_name = fields.Char(string='Insured Name')
	phone = fields.Char(string='Phone Number')
	city = fields.Many2one('res.country.state')
	email = fields.Char()
	card_id = fields.Char()
	expire_date = fields.Date()
	partner_id = fields.Many2one('res.partner')	
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
