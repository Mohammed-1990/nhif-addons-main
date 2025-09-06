from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError

class BudgetOperation(models.Model):
	_name = 'account.budget.operation'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']
	_order = 'id desc'

	name = fields.Char(string='Description',track_visibility='always')
	date = fields.Date(default=lambda self: fields.Date.today(),track_visibility='always')
	operation_type = fields.Selection([('addition','Addition'),('transfer','Transfer')], default='transfer',track_visibility='always')
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('validated','Validated'),('canceled','Canceled')], default='draft',track_visibility='always')
	line_ids = fields.One2many('account.budget.operation.line', 'line_id')
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	
	@api.multi
	def do_confirm(self):
		if self.operation_type == 'transfer':
			for record in self.line_ids:
				if record.amount > record.approved_value:
					raise ValidationError(_('There is No Enough Budget in the account ' + record.account_id.name))
		self.state = 'confirmed'

	@api.multi
	def do_validate(self):
		if self.operation_type == 'addition':
			for line in self.line_ids:
				for budget_line in line.budget_item_details_id.accounts_value_ids:
					if budget_line.account_id == line.account_id:
						budget_line.addition_value = budget_line.addition_value + line.amount 

		if self.operation_type == 'transfer':
			for line in self.line_ids:
				for budget_line in line.budget_item_details_id.accounts_value_ids:
					if budget_line.account_id == line.account_id:
						budget_line.withdraw_value = (abs(budget_line.withdraw_value) + abs(line.amount) )
						# if budget_line.planned_value < 0:
						# 	budget_line.withdraw_value = (abs(budget_line.withdraw_value) - abs(line.amount) ) * -1
						# else:
						# 	budget_line.withdraw_value = (abs(budget_line.withdraw_value) - abs(line.amount) )

				for budget_line in line.to_budget_item_details_id.accounts_value_ids:
					if budget_line.account_id == line.to_account_id:
						budget_line.addition_value = (abs(budget_line.addition_value) + line.amount) 
						# if budget_line.planned_value < 0:
							# budget_line.addition_value = (abs(budget_line.addition_value) + line.amount) * -1
						# else:
							# budget_line.addition_value = (abs(budget_line.addition_value) + line.amount) 

		self.state = 'validated'



	@api.multi
	def do_cancel(self):
		self.state = 'canceled'




class BudgetOperationLine(models.Model):
	_name = 'account.budget.operation.line'

	budget_id = fields.Many2one('crossovered.budget', string='Budget')
	budget_item_details_id = fields.Many2one('account.budget.post', string='Budget Item Details')
	account_id = fields.Many2one('account.account', string='Account')
	approved_value = fields.Float(string='Remaining Amount in the Account', compute='compute_approved_value')
	amount = fields.Float()
	to_budget_item_details_id = fields.Many2one('account.budget.post', string='To Budget Item')
	to_account_id = fields.Many2one('account.account', string='To Account')
	line_id = fields.Many2one('account.budget.operation')

	operation_type = fields.Selection(related='line_id.operation_type')
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	

	@api.multi
	@api.onchange('budget_id')
	def onchange_budget(self):
		for record in self:
			if record.budget_id:
				details_list_ids = []
				for line in record.budget_id.expenses_line_ids:
					details_list_ids.append( line.general_budget_id.id )
				return{
					'domain' : {
						'budget_item_details_id' : [('id','in',details_list_ids)],
						'to_budget_item_details_id' : [('id','in',details_list_ids)],
					}
				}


	@api.multi
	@api.onchange('budget_item_details_id', 'to_budget_item_details_id' )
	def onchange_budget_item(self):
		for record in self:
			to_account_list = []
			account_list = []

			if record.budget_item_details_id:
				for line in record.budget_item_details_id.accounts_value_ids:
					account_list.append( line.account_id.id )
			
			if record.to_budget_item_details_id:
				
				for line in record.to_budget_item_details_id.accounts_value_ids:
					to_account_list.append( line.account_id.id )

			return{
				'domain':{
					'account_id':[('id','in', account_list)],
					'to_account_id':[('id','in', to_account_list),('id','!=',record.account_id.id)]
				}
			}

	@api.multi
	@api.depends('account_id')
	def compute_approved_value(self):
		for record in self:
			if record.account_id:
				for detail in record.budget_item_details_id.accounts_value_ids:
					if detail.account_id == record.account_id:
						record.approved_value = detail.remaining_value


