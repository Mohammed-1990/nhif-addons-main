from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError
from . import amount_to_text as amount_to_text_ar
from odoo.exceptions import ValidationError


class MoneySupply(models.Model):
	_name = 'money.supply'
	_description = 'Bank/Save Supply'
	_order = 'id desc'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']

	ref = fields.Char(string="Number",track_visibility='always') 
	name = fields.Char(string='Description',track_visibility='always')
	date = fields.Date(track_visibility='always', default=lambda self: fields.Date.today())
	supply_type = fields.Selection([('bank_supply','Bank Supply'),('39_receipt','39 Receipt')], default='39_receipt',track_visibility='always')
	partner_id = fields.Many2one('res.partner', string='Receipt From',track_visibility='always')
	journal_id = fields.Many2one('account.journal', string='Bank/Save',track_visibility='always')
	bank_or_cash_account_id = fields.Many2one('account.account', string='Bank/Cash Account',track_visibility='always')
	account_id = fields.Many2one('account.account', string='Account',track_visibility='always')
	account_number = fields.Char(track_visibility='always')
	total_amount = fields.Float(string="Total Amount" ,track_visibility='always')
	amount = fields.Float(track_visibility='always')
	pid_amount = fields.Float(string="Pid Amount", track_visibility='always')
	reminning_amount = fields.Float(string="Reminning Amount",compute='compute_reminning_amount', store=True ,track_visibility='always')
	amount_in_words = fields.Char(compute='get_amount_in_words',track_visibility='always')
	clipboard_number = fields.Char(string='Clipboard Number/39 Receipt Number',track_visibility='always')
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('validated','Validated'),('canceled','Canceled')], default='draft', copy=False,track_visibility='always')
	move_id = fields.Many2one('account.move', copy=False)
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	file_data = fields.Binary(
        string="Upload File",
        attachment=True
    )


	@api.multi
	@api.depends('total_amount','pid_amount')
	def compute_reminning_amount(self):
		for record in self:
			record.reminning_amount  = record.total_amount - record.pid_amount


	@api.multi
	@api.depends('amount')
	def get_amount_in_words(self):
		for record in self:
			record.amount_in_words  = amount_to_text_ar.amount_to_text(record.amount, 'ar')


	@api.multi
	@api.onchange('journal_id')
	def onchange_journal_id(self):
		for record in self:
			if record.journal_id:
				if record.journal_id.default_debit_account_id:
					record.bank_or_cash_account_id = record.journal_id.default_debit_account_id.id
				if record.journal_id.type == 'bank':
					record.account_number = record.journal_id.bank_account_id.acc_number

	@api.multi
	@api.onchange('supply_type')
	def onchange_supply_type(self):
		if self.supply_type == '39_receipt':
			self.journal_id = False
			self.bank_or_cash_account_id = False
			return {
				'domain' : {
					'journal_id':[('type','=','cash')]
				}
			}
		if self.supply_type == 'bank_supply':
			self.journal_id = False
			self.bank_or_cash_account_id = False
			return {
				'domain' : {
					'journal_id':[('type','=','bank')]
				}
			}


	# @api.model 
	# def create(self, vals):
	# 	vals['ref'] = self.env['ir.sequence'].next_by_code('money.supply.sequence') or '/'
	# 	return super(MoneySupply, self).create(vals)

	@api.model
	def create(self, vals):
		vals['ref'] = self.env['ir.sequence'].next_by_code('money.supply.sequence') or '/'
		record = super(MoneySupply, self).create(vals)

		if record.pid_amount == record.total_amount:
			raise ValidationError("تم تغذية كامل المبلغ المتعلق ب 67")
		
		if not record.receipt_67_id.exists():
			raise ValidationError("غير مسموح تغزية البك  /الخزينة  مباشرا يجب ان تكون العملية مرتبطة  باورنيك 67")


		return record

	@api.multi
	def do_confirm(self):
		if self.amount <= 0:
			raise ValidationError(_('Amount Must be more than Zero'))
		if self.amount > self.reminning_amount:
			raise ValidationError(_('Amount is   more than Aeminning Amount'))


		self.state = 'confirmed'



	@api.multi
	def do_cancel(self):
		for account_move in self.env['account.move'].search([('money_supply_id','=',self.id)]):
			account_move.button_cancel()
			account_move.unlink()
		self.state = 'canceled'


	@api.multi
	def unlink(self):
		for record in self:
			if record.state not in ['draft','canceled']:
				raise ValidationError(_('You Can not delete a Record, witch is not Draft or Canceled'))
			return super(MoneySupply, self).unlink()


	@api.multi
	def do_validate(self):
		self.move_id = self.env['account.move'].create({
			'ref': self.name,
			'journal_id': self.journal_id.id,
			'money_supply_id' : self.id,
			'date' : self.date,
			'document_number' : self.clipboard_number or self.name,
			'line_ids': [
			(0,0,{
				'partner_id': self.partner_id.id,
				'name': self.name,
				'account_id': self.account_id.id,
				'credit': self.amount,
				'date_maturity' : self.date,
				}),
			(0,0,{
				'partner_id': self.partner_id.id,
				'name': self.name,
				'account_id': self.bank_or_cash_account_id.id,
				'debit': self.amount,
				'date_maturity' : self.date,
				})
			]})
		self.move_id.post()
		self.write({'pid_amount':self.pid_amount + self.amount})
		self.receipt_67_id.write({'pid_amount':(self.pid_amount)})
		self.state = 'validated'

	@api.multi
	def do_reset_to_draft(self):
		self.state = 'draft'




	@api.multi
	def show_moves(self):
		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'tree,form',
			'res_model' : 'account.move',
			'domain' : [('money_supply_id','=', self.id )],
		}


class AccountMove(models.Model):
	_inherit = 'account.move'

	money_supply_id = fields.Many2one('money.supply')	
	document_number = fields.Char(default='-')


