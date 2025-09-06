from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError
from . import amount_to_text as amount_to_text_ar
from datetime import date, datetime


class MoneyMovement(models.Model):
	_name = 'money.movement'
	_description = 'Money Movement'
	_order = 'id desc'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']

	transfer_no = fields.Char()
	branch_id = fields.Many2one('res.company', string='Branch',default= lambda self:self.env.user.company_id.id,track_visibility='always')
	name = fields.Char(string='Description',track_visibility='always')
	date = fields.Date(default=lambda self: fields.Date.today(),track_visibility='always')
	from_journal_id = fields.Many2one('account.journal', string='From Bank/Cash',track_visibility='always', domain=[('type','in',['bank','cash'])])
	to_journal_id = fields.Many2one('account.journal', string='To Bank/Cash',track_visibility='always', domain=[('type','in',['bank','cash'])])
	amount = fields.Float(track_visibility='always')
	amount_in_words = fields.Char(compute='get_amount_in_words',track_visibility='always')
	move_id = fields.Many2one('account.move')
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('canceled','canceled')],default='draft',track_visibility='always')

	from_journal_balance = fields.Float('Current Balance', compute='get_journal_balance')
	to_journal_balance = fields.Float('Current Balance', compute='get_journal_balance')

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)


	@api.multi
	@api.depends('from_journal_id','to_journal_id', 'date')
	def get_journal_balance(self):


		date_to = fields.Date.today()
		date_from = date( date_to.year, 1, 1) 
		if self.date:
			date_to = self.date

		if self.from_journal_id:
			self._cr.execute("select sum(COALESCE( debit, 0 ))-sum(COALESCE( credit, 0 )) from account_move_line where account_id="  + str(self.from_journal_id.default_credit_account_id.id) + "  AND date <=  '" + str(date_to) +  "'  " )
			self.from_journal_balance = self.env.cr.fetchone()[0] or 0.0

		if self.to_journal_id:
			self._cr.execute("select sum(COALESCE( debit, 0 ))-sum(COALESCE( credit, 0 )) from account_move_line where account_id="  + str(self.to_journal_id.default_credit_account_id.id) + "    AND date <=  '" + str(date_to) +  "'  " )
			self.to_journal_balance = self.env.cr.fetchone()[0] or 0.0
					


	@api.multi
	@api.onchange('from_journal_id')
	def onchange_from_journal(self):
		if self.from_journal_id:
			return {
				'domain' : {
					'to_journal_id' : [('id','!=', self.from_journal_id.id),('type','in',['bank','cash'])],
				}
			}

	@api.model 
	def create(self, vals):
		create_id =  super(MoneyMovement, self).create(vals)
		if create_id.date:
			seq_code = 'bank.transfer.sequence.' + str(create_id.date.year) + '.' + str(create_id.date.month)
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
			create_id.transfer_no = seq 
		return create_id


	@api.multi 
	def write(self, vals):
		write_id = super(MoneyMovement, self).write(vals)
		if vals.get('date', False):
			seq_code = 'bank.transfer.sequence.' + str(self.date.year) + '.' + str(self.date.month)
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




	@api.multi
	def do_confirm(self):

		if self.amount > self.from_journal_balance:
			raise ValidationError(_('There is No Enough Balance'))

		self.move_id = self.env['account.move'].create({
			'ref': self.name,
			'journal_id': self.to_journal_id.id,
			'money_movement_id' : self.id,
			'date' : self.date,
			'document_number' : self.transfer_no or self.name,
			'line_ids': [
			(0,0,{
				'name': self.name,
				'account_id': self.from_journal_id.default_credit_account_id.id,
				'credit': self.amount,
				'date_maturity' : self.date,
				}),
			(0,0,{
				'name': self.name,
				'account_id': self.to_journal_id.default_credit_account_id.id,
				'debit': self.amount,
				'date_maturity' : self.date,
				})
			]})
		self.move_id.post()
		self.state = 'confirmed'


	@api.multi
	@api.depends('amount')
	def get_amount_in_words(self):
		for record in self:
			record.amount_in_words  = amount_to_text_ar.amount_to_text(record.amount, 'ar')


	@api.multi
	def do_cancel(self):
		for account_move in self.env['account.move'].search([('money_movement_id','=',self.id)]):
			account_move.button_cancel()
			account_move.unlink()
		self.state = 'canceled'



	@api.multi
	def show_moves(self):
		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'tree,form',
			'res_model' : 'account.move',
			'domain' : [('money_movement_id','=', self.id )],
		}


	@api.multi
	def do_reset_to_draft(self):
		self.state = 'draft'




class AccountMove(models.Model):
	_inherit = 'account.move'

	money_movement_id = fields.Many2one('money.movement')	
	document_number = fields.Char(default='---')

