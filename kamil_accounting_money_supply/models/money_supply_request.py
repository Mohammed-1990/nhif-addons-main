from odoo import models,fields,api,_ 
from . import amount_to_text as amount_to_text_ar


class MoneySupplyRequest(models.Model):
	_name = 'money.supply.request'
	_description = 'Money Supply Request'
	_order = 'id desc'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']

	name = fields.Char('Description',track_visibility='always')
	cash_journal_id = fields.Many2one('account.journal', domain=[('type','=','cash')], string='To Cash Journal',track_visibility='always')
	bank_journal_id = fields.Many2one('account.journal', domain=[('type','=','bank')], string='From Bank Journal',track_visibility='always')
	amount = fields.Float(track_visibility='always')
	amount_in_words = fields.Char(compute='get_amount_in_words',track_visibility='always')
	date = fields.Date(default=lambda self: fields.Date.today(),track_visibility='always')
	state = fields.Selection([('draft','Draft'),('admin_approved','Admin Approved'),('finance_approved','Finance Manager Approved'),('ratifications_department','Transfer to Ratifications Department'),('canceled','Canceled')], default='draft',track_visibility='always')
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)

	@api.multi
	def show_ratification(self):

		for ratification_id in self.env['ratification.ratification'].search([('money_supply_request_id','=',self.id)]):
			
			return {
				'type' : 'ir.actions.act_window',
				'view_mode' : 'form',
				'res_model' : 'ratification.ratification',
				'res_id' : ratification_id.id,
				'domain' : [('money_supply_request_id','=', self.id )],
				'context' : {'default_money_supply_request_id':self.id}, 
			}			

		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'ratification.ratification',
			'domain' : [('money_supply_request_id','=', self.id )],
			'context' : {'default_money_supply_request_id':self.id}, 
		}



	@api.multi
	@api.depends('amount')
	def get_amount_in_words(self):
		for record in self:
			record.amount_in_words  = amount_to_text_ar.amount_to_text(record.amount, 'ar')


	@api.multi
	def do_finance_approve(self):
		for record in self:
			record.state = 'finance_approved'
	
	@api.multi
	def do_admin_approve(self):
		for record in self:
			record.state = 'admin_approved'
	
	@api.multi
	def do_transfer_to_ratifications(self):
		for record in self:
			record.state = 'ratifications_department'

	@api.multi
	def do_cancel(self):
		for record in self:
			record.state = 'canceled'

	@api.multi
	def do_reset_to_draft(self):
		for record in self:
			record.state = 'draft'


# class Ratification(models.Model):
# 	_inherit = 'ratification.ratification'

# 	money_supply_request_id = fields.Many2one('money.supply.request')