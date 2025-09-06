from odoo import models,fields,api,_ 

class AccountJournal(models.Model):
	
    _inherit = 'account.journal'
	
    bank_type = fields.Selection([
					('deposit_bank','Deposit Bank'),
					('expenses_bank','Expenses Bank')
					],'Bank Type' ,required=True ,track_visibility='always')
	

