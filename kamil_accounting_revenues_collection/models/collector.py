from odoo import models,fields,api,_ 

class Collector(models.Model):
	_inherit = 'hr.employee'

	is_collector = fields.Boolean(string='Is Collector ?',)
	collector_account_id = fields.Many2one('account.account', domain=[('is_collection_account', '=', True)], string='Collector Account')
