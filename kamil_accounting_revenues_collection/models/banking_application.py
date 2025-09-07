from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError

class BankingApplication(models.Model):
    _name = 'banking.application'
    _description = 'Banking application'
    _order = 'id desc'
    _inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']
    
    
    name = fields.Char(string='Name' ,track_visibility='always', copy=False)
    account_number = fields.Char(string='Account  Number',track_visibility='always', copy=False)
    company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)






