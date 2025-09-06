from odoo import models,fields,api,_ 
from . import amount_to_text as amount_to_text_ar
from odoo.exceptions import ValidationError

class RatificationList(models.Model):
	_name = 'ratification.list'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']
	_order = 'id desc'

	ref = fields.Char()
	name = fields.Char(string='Description',track_visibility='always')
	date = fields.Date(default=lambda self: fields.Date.today())
	
	deduction_amount = fields.Float(compute='get_total_deductions')

	total_amount =  fields.Float(compute='get_total_amount')

	total_net_amount = fields.Float(compute='get_total_net_in_words')

	total_net_amount_in_words = fields.Char(compute='get_total_net_in_words')
	

	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('canceled','Canceled'),('send_to_ia','Send to Internal Auditor')], default='draft',copy=False,track_visibility='always')
	line_ids = fields.One2many('ratification.list.line', 'line_id')

	ratification_ids = fields.One2many('ratification.ratification', 'ratification_list_id')

	tax_amount_ids = fields.Many2many('list.deduction.line')

	ratification_line_ids = fields.One2many('ratification.line', 'ratification_list_id', copy=True)
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	other_deduction_ids = fields.One2many('list.other.deduction','ratification_list_id')
	x_create_user_id = fields.Many2one('res.users', string='Created by', default= lambda self:self.env.user.id)
	ratification_state = fields.Selection([('draft','Draft'),('executed','Under Execution'),('audited','Approved'),('payment_created','Payment Created'),('payment_confirmed','Payment Confirmed'),('paid','Paid'),('canceled','Canceled')], compute='get_state_ratification', store=True)
	from_complex = fields.Boolean()

	@api.multi
	def get_state_ratification(self):
		for record in self:
			for ratification in record.ratification_ids:
				
				record.ratification_state = ratification.state

	@api.multi
	@api.onchange('ratification_line_ids')  # Trigger when lines are added/removed/changed
	def _onchange_ratification_list_line_ids(self):
		for line in self.ratification_line_ids:
			# Only update if the line's date is not already set or is default (today)
			# This avoids overwriting manually entered dates or dates from other sources
			if not line.date or line.date == fields.Date.today():
				if self.date:
					line.date = self.date
				else:
					line.date = date.today()  # Fallback if parent date is not set yet


	@api.multi
	@api.depends('ratification_line_ids','total_net_amount', 'other_deduction_ids')
	def get_total_amount(self):
		for record in self:
			total_amount = 0
			for line in record.ratification_line_ids:
				total_amount = total_amount + line.amount
			record.total_amount = total_amount




	@api.multi
	@api.depends('ratification_line_ids','total_net_amount', 'other_deduction_ids')
	def get_total_deductions(self):
		for record in self:
			deduction_amount = 0
			for line in record.ratification_line_ids:
				for tax_line in line.deduction_ids:
					deduction_amount = deduction_amount + tax_line.amount


			# record.deduction_amount = deduction_amount
			

			other_deduction_amount = 0
			for line in record.other_deduction_ids:
				if line.partner_id and line.tax_id:
					other_deduction_amount = other_deduction_amount + line.amount

			record.deduction_amount = deduction_amount + other_deduction_amount

	@api.model 
	def create(self, vals):
		vals['ref'] = self.env['ir.sequence'].next_by_code('ratification.list.sequence') or '/'
		rat_list = super(RatificationList, self).create(vals)

		self._cr.execute("delete from ratification_line where account_id is  null")
		self._cr.execute("delete from list_other_deduction where tax_id is null")
		return rat_list


	@api.multi
	@api.depends('line_ids','ratification_line_ids','other_deduction_ids')
	def get_total_net_in_words(self):
		for record in self:
			total = 0
			for line in record.ratification_line_ids:
				total = total + line.amount

			record.total_net_amount = total - record.deduction_amount

			record.total_net_amount_in_words = amount_to_text_ar.amount_to_text( (total - record.deduction_amount) , 'ar')

	@api.multi
	def set_to_draft(self):
		if self.ratification_ids and self.ratification_ids.state != 'draft':
			raise ValidationError(_('You Can not Set to Draft the List after the ratification was Issued'))
		self.state = 'draft'

	@api.multi
	def do_cancel(self):		
		if self.ratification_ids:
			raise ValidationError(_('You Can not Cancel the List after the ratification was Issued'))
		self.state = 'canceled'

	@api.multi
	def unlink(self):
		for rat_list in self:
			if rat_list.state not in ['draft','canceled','send_to_ia']:
				raise ValidationError(_('You Can not delete a record, witch is not Draft or Canceled'))
			return super(RatificationList, self).unlink()
		
	



	@api.multi
	def do_confirm(self):
		for line in self.ratification_line_ids:
				line.write({'account_id':self.complex_id.payable_account_id.id,
				'analytic_account_id':False,
				'the_type':'accounts_payable'

				})

		
		self.create_uid = self.env.user.id 	
		self.x_create_user_id = self.env.user.id 	
		self.state = 'confirmed'


	@api.multi
	def show_ratifications(self):

		for ratification in self.env['ratification.ratification'].search([('ratification_list_id','=',self.id)]):
			return {
				'type' : 'ir.actions.act_window',
				'view_mode' : 'form',
				'res_model' : 'ratification.ratification',
				'res_id' : ratification.id,
				'context':{'default_ratification_list_id' : self.id, 'default_name' : self.name},
				'domain' : [('ratification_list_id','=', self.id  )],
			}


		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'ratification.ratification',
			'context':{'default_ratification_list_id' : self.id, 'default_name' : self.name},
			'domain' : [('ratification_list_id','=', self.id  )],
		}




	@api.multi
	def do_print(self):

		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'wizard.ratification.list',
			'target': 'new',
			'context':{'list_id': self.id}
		}

	

	@api.model 
	def create(self, vals):
		create_id = super(RatificationList, self).create(vals)
		if create_id.date:
			seq_code = 'ratification.list.sequence.' + str(create_id.date.year) + '.' + str(create_id.date.month)
			seq = self.env['ir.sequence'].next_by_code( seq_code )
			if not seq:
				self.env['ir.sequence'].create({
					'name' : seq_code,
					'code' : seq_code,
					'prefix' :  str(create_id.date.year) + '-' +  str(create_id.date.month) + '-' ,
					'number_next' : 1,
					'number_increment' : 1,
					'use_date_range' : True,
					'padding' : 4,
					})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
			create_id.ref = seq 
		return create_id


	@api.multi 
	def write(self, vals):
		write_id = super(RatificationList, self).write(vals)
		if vals.get('date', False):
			seq_code = 'ratification.list.sequence.' + str(self.date.year) + '.' + str(self.date.month)
			seq = self.env['ir.sequence'].next_by_code( seq_code )
			if not seq:
				self.env['ir.sequence'].create({
					'name' : seq_code,
					'code' : seq_code,
					'prefix' :  str(self.date.year) + '-' +  str(self.date.month) + '-' ,
					'number_next' : 1,
					'number_increment' : 1,
					'use_date_range' : True,
					'padding' : 4,
					})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
			self.ref = seq 
		return write_id

class RatificationListLine(models.Model):
	_name = 'ratification.list.line'

	partner_id = fields.Many2one('res.partner', string='The Partner')
	name = fields.Char()
	analytic_account_id = fields.Many2one('account.analytic.account',string='Budget Item')
	account_id = fields.Many2one('account.account', string='Account')
	cost_center_id = fields.Many2one('kamil.account.cost.center', string='Cost Center')
	analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Analytic Tags')
	amount = fields.Float()

	ratification_type = fields.Selection([
		('expenses','expenses'),
		('purchases','Purchases'),
		('accounts_receivable','Accounts Receivable'),
		('petty_cash','Petty Cash'),
		('service_provider_loan','Service Provider Loans'),
		('prepaid_expenses', 'Prepaid Expenses'),
		('accounts_payable','Accounts Payable'),
		('service_provider_claim','Service Provider Claim')],default='expenses',track_visibility='always')

	deduction_line_ids = fields.Many2many('list.deduction.line')

	deduction_ids = fields.Many2many('account.tax', string='Deductions')

	deduction_amount = fields.Float(compute='compute_deduction_amount')
	net_amount = fields.Float(compute='get_net_amount')
	account_number = fields.Char(string='Account Number')
	line_id = fields.Many2one('ratification.list')
	account_code = fields.Char()
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	

	@api.multi
	@api.onchange('account_id')
	def onchange_account(self):
		for record in self:
			if record.account_id:
				if record.ratification_type in ['expenses','service_provider_claim']:
					record.analytic_account_id = record.account_id.parent_budget_item_id


	@api.multi
	@api.onchange('ratification_type')
	def onchange_ratification_type(self):
		for record in self:
			if record.ratification_type in ['accounts_receivable','petty_cash','service_provider_loan','prepaid_expenses','purchases']:
				record.analytic_account_id = False

			if record.ratification_type == 'purchases':
				stock_account_ids = []
				for stock in self.env['stock.location'].search([]):
					if stock.account_id :
						stock_account_ids.append( stock.account_id.id )
				return {
					'domain' : {
						'account_id':[('id','in',stock_account_ids)]
					}
				}
			else:

				account_ids = []
				for account in self.env['account.account'].search([('is_group','=','sub_account')]):
					if account.code[:1] in ['2','3','4']:
						account_ids.append( account.id )

				return {
					'domain' : {
						'account_id':[('id','in',account_ids)]
					}
				}
		

	@api.multi
	@api.onchange('partner_id')
	def onchange_partner(self):
		for record in self:
			if record.partner_id:
				record.account_number = record.partner_id.account_number

	@api.multi
	@api.depends('deduction_ids','amount')
	def compute_deduction_amount(self):
		for record in self:
			tax_amount = 0
			for tax in record.deduction_ids:
				if tax.amount_type == 'fixed':
					tax_amount = tax_amount + tax.amount
				if tax.amount_type == 'percent':
					tax_amount = tax_amount + (tax.amount * record.amount / 100)
			record.deduction_amount = tax_amount



	@api.multi
	@api.depends('amount','deduction_amount')
	def get_net_amount(self):
		for record in self:
			record.net_amount = record.amount - record.deduction_amount





class RatificationListLineDeduction(models.Model):
	_name = 'ratification.list.line.deduction'
	_rec_name = 'line_ids'

	line_ids = fields.One2many('list.deduction.line','line_id', copy=True)
	line_id = fields.Many2one('ratification.list.line')





class ListOtherDeduction(models.Model):
	_name = 'list.other.deduction'
	
	name = fields.Char(string='Description')
	partner_id = fields.Many2one('res.partner',string='The Partner')
	tax_id = fields.Many2one('account.tax', string='Deduction')
	amount = fields.Float()
	ratification_list_id = fields.Many2one('ratification.list')




class RatificationListLineDeduction(models.Model):
	_name = 'list.deduction.line'
	_rec_name = 'tax_id'
	tax_id = fields.Many2one('account.tax', string='Deduction')
	amount = fields.Float()
	
	line_id = fields.Many2one('ratification.list.line.deduction')


class Ratification(models.Model):
	_inherit = 'ratification.ratification'

	ratification_list_id = fields.Many2one('ratification.list')


class ResPartner(models.Model):
	_inherit = 'res.partner'

	is_bank = fields.Selection([('bank','Bank'),('cashier','Cashier')], string='Is Bank/Cashier')