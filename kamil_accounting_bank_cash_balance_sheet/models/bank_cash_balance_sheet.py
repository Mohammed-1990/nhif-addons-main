from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
from . import amount_to_text as amount_to_text_ar

from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class BankCashBalabceSheet(models.Model):
	_name = 'bank.cash.balance.sheet'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']
	_description = 'Bank/Cash Balance Sheet'
	_order = 'id desc'

	name = fields.Many2one('account.journal', string='Bank/Cash', domain=[('type','in',['bank','cash'])])

	type = fields.Selection(related='name.type')
	operation_date = fields.Date(default=lambda self: fields.Date.today())

	month = fields.Selection([(1,'January'),(2, 'February'),(3, 'March'),(4, 'April'),(5, 'May'),(6, 'June'),(7, 'July'),(8, 'August'),(9, 'September'),(10, 'October'),(11, 'November'),(12, 'December')], default=1,track_visibility='always')
	year = fields.Char()
	all_transactions = fields.Boolean(default=True)
	not_paid_off = fields.Boolean()
	paid_off = fields.Boolean()
	canceled= fields.Boolean()
	state = fields.Selection([('draft','Draft'),('confirm','Confirm')],default='draft')
	line_ids = fields.One2many('bank.cash.balance.sheet.line', 'line_id')


	move_ids = fields.Many2many(comodel_name='bank.cash.balance.sheet.line', relation='bank_balance_moves')

	previous_move_ids = fields.Many2many(comodel_name='bank.cash.balance.sheet.line', relation='bank_balance_previoud_moves')


	move_line_ids = fields.Many2many('account.move.line')
	previous_move_line_ids = fields.One2many('account.move.line', 'sheet_id')

	balance_according_to_bank_statement = fields.Float()
	revenues_under_collection = fields.Float(compute='compute_values')
	total = fields.Float( compute='compute_values')

	cheques_not_provided_for_exchange = fields.Float(compute='compute_values')
	bank_balance = fields.Float(compute='compute_values')

	previous_balance_book = fields.Float()

	total_revenues = fields.Float(compute='compute_values')
	total_expenses = fields.Float(compute='compute_values')

	other_revenues = fields.Float()
	other_expenses = fields.Float()

	current_balance_book = fields.Float(compute='compute_values')

	strored_current_balance_book = fields.Float()

	addition_ids = fields.One2many('bank.sheet.addition', 'sheet_id', readonly=True)

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)





	# def write(self, vals):
	# 	write_id = super(BankCashBalabceSheet, self).write(vals)
	# 	if vals.get('move_ids', False) or vals.get('previous_move_ids', False):
	# 		for sheet in self.env['bank.cash.balance.sheet'].search([('id','in',self._ids)]):
	# 			for line in sheet.move_ids:
	# 				if line.move_line_id:
	# 					line.move_line_id.paid_off = line.paid_off
	# 				else:
	# 					raise ValidationError(_('Please Add move line for (%s) ' %(line.name)))
	# 			for line in sheet.previous_move_ids:
	# 				for paid_line in line.move_line_id:
	# 					paid_line.paid_off = line.paid_off
	# 	return write_id

	@api.model
	def create(self, vals):
		for record in self.env['bank.cash.balance.sheet'].search([('month','=',vals.get('month',False)),('year','=',vals.get('year',False)),('name','=',vals.get('name', False))]):
			raise ValidationError(_('لا يمكنك إنشاء اكثر من موازنة لنفس الفترة'))
		return super(BankCashBalabceSheet, self).create(vals)

	@api.onchange('month', 'year')
	def onchange_month_year(self):
		for record in self:
			if record.year and record.month:
				current_date = date( int(record.year) , int(record.month) , 1)
				previous_month = current_date + relativedelta(months=- 1)

				for bank_balance_record in self.env['bank.cash.balance.sheet'].search([('name','=',self.name.id),('year','=',str(previous_month.year)),('month','=',int(previous_month.month) )]):
						record.previous_balance_book = bank_balance_record.current_balance_book



	@api.depends('move_ids','previous_move_ids','balance_according_to_bank_statement', 'revenues_under_collection','total','cheques_not_provided_for_exchange','bank_balance','previous_balance_book','total_revenues','total_expenses','current_balance_book','other_revenues','other_expenses', 'addition_ids')
	def compute_values(self):
		for record in self:
			# if record.state == 'draft':
				for line in record.previous_move_ids:
					if line.debit > 0 and not line.paid_off:
						record.revenues_under_collection = record.revenues_under_collection + line.debit

					if line.credit > 0 and not line.paid_off:
						record.cheques_not_provided_for_exchange = record.cheques_not_provided_for_exchange + line.credit

				for line in record.move_ids:

					if line.debit > 0 and not line.paid_off:
						record.revenues_under_collection = record.revenues_under_collection + line.debit

					if line.credit > 0 and not line.paid_off:
						record.cheques_not_provided_for_exchange = record.cheques_not_provided_for_exchange + line.credit

					if line.debit > 0:
						if line.date.year == int(record.year) and line.date.month == record.month:
							record.total_revenues = record.total_revenues + line.debit

					if line.credit > 0:
						if line.date.year == int(record.year) and line.date.month == record.month:
							record.total_expenses = record.total_expenses + line.credit

				#other revenues and expenses
				record.revenues_under_collection = record.revenues_under_collection - record.other_expenses
				record.cheques_not_provided_for_exchange = record.cheques_not_provided_for_exchange + record.other_revenues

				record.total = record.balance_according_to_bank_statement + record.revenues_under_collection

				record.bank_balance = record.total - record.cheques_not_provided_for_exchange



				#other revenues and expenses
				record.total_revenues = record.total_revenues - record.other_expenses
				record.total_expenses = record.total_expenses + record.other_revenues


				record.current_balance_book = record.previous_balance_book + record.total_revenues - record.total_expenses
				strored_current_balance_book = record.previous_balance_book + record.total_revenues - record.total_expenses


				for line in record.addition_ids:
					if line.the_type == 'addition':
						record.bank_balance = record.bank_balance + line.amount

					if line.the_type == 'subtraction':
						record.bank_balance = record.bank_balance - line.amount




	def do_save_changes(self):
		for record in self:
			for line in record.move_ids:
				if line.move_line_id:
					line.move_line_id.paid_off = line.paid_off
				else:
					raise ValidationError(_('Please Add move line for (%s) ' %(line.name)))


			for line in record.previous_move_ids:
				if line.move_line_id:
					line.move_line_id.paid_off = line.paid_off
				else:
					raise ValidationError(_('Please Add move line for (%s) ' %(line.name)))


	def do_confirm(self):
		for line in self.move_ids:
			if line.move_line_id:
				line.move_line_id.paid_off = line.paid_off
			else:
				raise ValidationError(_('Please Add move line for (%s) ' %(line.name)))

		for line in self.previous_move_ids:
			if line.move_line_id:
				line.move_line_id.paid_off = line.paid_off
			else:
				raise ValidationError(_('Please Add move line for (%s) ' %(line.name)))
		self.state = 'confirm'


	def do_calculate(self):
		self.move_ids = False
		self.previous_move_ids = False

		all_move_ids_list = []
		all_previous_move_ids_list = []

		for move_line in self.env['account.move.line'].search([('account_id','=',self.name.default_debit_account_id.id),('hide_in_sheet','=', False),],order='document_number asc'):
			if move_line.date.year == int(self.year):
				if move_line.date.month == self.month:
					all_move_ids_list.append( (0,0,{
						'date' : move_line.date,
						'partner_id' : move_line.partner_id,
						'document_number' : move_line.document_number,
						'name' : move_line.name,
						'debit' : move_line.debit,
						'credit' : move_line.credit,
						'paid_off' : move_line.paid_off,
						'canceled' : move_line.canceled,
						'move_line_id' : move_line.id,
						}) )

				if move_line.date.month < self.month and move_line.paid_off == False:
					all_previous_move_ids_list.append( (0,0,{
						'date' : move_line.date,
						'partner_id' : move_line.partner_id,
						'document_number' : move_line.document_number,
						'name' : move_line.name,
						'debit' : move_line.debit,
						'credit' : move_line.credit,
						'paid_off' : move_line.paid_off,
						'canceled' : move_line.canceled,
						'move_line_id' : move_line.id,
						}) )

			if move_line.date.year < int(self.year) and move_line.paid_off == False:
				all_previous_move_ids_list.append( (0,0,{
					'date' : move_line.date,
					'partner_id' : move_line.partner_id,
					'document_number' : move_line.document_number,
					'name' : move_line.name,
					'debit' : move_line.debit,
					'credit' : move_line.credit,
					'paid_off' : move_line.paid_off,
					'canceled' : move_line.canceled,
					'move_line_id' : move_line.id,
					}) )
		self.move_ids = all_move_ids_list
		self.previous_move_ids = all_previous_move_ids_list



	def do_hide_paid_off(self):
		self.previous_move_ids = False
		for move_line in self.env['account.move.line'].search([('account_id','=',self.name.default_debit_account_id.id),('hide_in_sheet','=', False)],order='document_number asc'):
			if move_line.date.year == int(self.year):
				if move_line.date.month < self.month and move_line.paid_off == False:
					self.previous_move_ids = [(0,0,{
						'date' : move_line.date,
						'partner_id' : move_line.partner_id,
						'document_number' : move_line.document_number,
						'name' : move_line.name,
						'debit' : move_line.debit,
						'credit' : move_line.credit,
						'paid_off' : move_line.paid_off,
						'canceled' : move_line.canceled,
						'move_line_id' : move_line.id,
						})]
			if move_line.date.year < int(self.year) and move_line.paid_off == False:
				self.previous_move_ids = [(0,0,{
					'date' : move_line.date,
					'partner_id' : move_line.partner_id,
					'document_number' : move_line.document_number,
					'name' : move_line.name,
					'debit' : move_line.debit,
					'credit' : move_line.credit,
					'paid_off' : move_line.paid_off,
					'canceled' : move_line.canceled,
					'move_line_id' : move_line.id,
					})]





	def do_show_all_moves(self):
		self.previous_move_ids = False
		for move_line in self.env['account.move.line'].search([('account_id','=',self.name.default_debit_account_id.id),('hide_in_sheet','=', False)],order='document_number asc'):
			if move_line.date.year == int(self.year):
				if move_line.date.month < self.month:
					self.previous_move_ids = [(0,0,{
						'date' : move_line.date,
						'partner_id' : move_line.partner_id,
						'document_number' : move_line.document_number,
						'name' : move_line.name,
						'debit' : move_line.debit,
						'credit' : move_line.credit,
						'paid_off' : move_line.paid_off,
						'canceled' : move_line.canceled,
						'move_line_id' : move_line.id,
						})]
			if move_line.date.year < int(self.year):
				self.previous_move_ids = [(0,0,{
					'date' : move_line.date,
					'partner_id' : move_line.partner_id,
					'document_number' : move_line.document_number,
					'name' : move_line.name,
					'debit' : move_line.debit,
					'credit' : move_line.credit,
					'paid_off' : move_line.paid_off,
					'canceled' : move_line.canceled,
					'move_line_id' : move_line.id,
					})]



	def do_validate(self):
		self.state = 'validate'


	def do_set_to_draft(self):
		for line in self.move_ids:
			if not line.move_line_id:
				raise ValidationError(_('Please Add move line for (%s) ' %(line.name)))

		for line in self.previous_move_ids:
			if not line.move_line_id:
				raise ValidationError(_('Please Add move line for (%s) ' %(line.name)))
		self.state = 'draft'

class BankCashBankbalabceSheetLine(models.Model):
	_name = 'bank.cash.balance.sheet.line'

	date = fields.Date()
	name = fields.Char()
	partner_id = fields.Many2one('res.partner')
	document_number = fields.Char()
	debit = fields.Float()
	credit = fields.Float()
	paid_off = fields.Boolean()
	canceled = fields.Boolean()
	payment_id = fields.Many2one('ratification.payment')
	collection_id = fields.Many2one('collection.collection')
	line_id = fields.Many2one('bank.cash.balance.sheet')
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	is_more_than_6_month = fields.Float(compute='get_is_more_than_6_month')
	move_line_id = fields.Many2one('account.move.line')
	hide_in_sheet = fields.Boolean()


	# @api.onchange('paid_off')
	# def onchange_paid_off(self):
	# 	for record in self:
	# 		if record.move_line_id:
	# 			# self._cr.execute("UPDATE account_move_line SET  paid_off = " + str( record.paid_off ) + " WHERE id = " + str(record.move_line_id.id) )
	# 			record.move_line_id.paid_off = record.paid_off


	def do_cancel_entery(self):

		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'account.move.cancel',
			'target':'new',
			'context' : {
				'bank_sheet_id' : self.id,
				'default_move_id':self.move_line_id.move_id.id,
				'default_date': self.date,
				'account_id' : self.move_line_id.account_id.id,
				'amount' : (self.move_line_id.debit + self.move_line_id.credit),
				'journal_id' : self.move_line_id.move_id.journal_id.id,
				'journal_account_id' : self.move_line_id.move_id.journal_id.default_debit_account_id.id,
				'partner_id' : self.move_line_id.partner_id.id,
				},
		}


	def get_is_more_than_6_month(self):
		for record in self:
			six_month_ago = fields.Date.today() + relativedelta(months=- 6)
			if six_month_ago > record.date:
				record.is_more_than_6_month = 1
			else:
				record.is_more_than_6_month = 0



class AccountMove(models.Model):
	_inherit = 'account.move'

	balance_id = fields.Many2one('bank.cash.balance.sheet')



class Payment(models.Model):
	_inherit = 'ratification.payment'

	paid_off = fields.Boolean()
	canceled = fields.Boolean()

class Collection(models.Model):
	_inherit = 'collection.collection'

	paid_off = fields.Boolean()
	canceled = fields.Boolean()


class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	# @api.depends('partner_id','company_id')
	# def get_diffrence(self):
	# 	for rec in self:
	# 		rec.diffrence = False
	# 		if rec.partner_id and rec.partner_id.is_employee == False and rec.partner_id.company_id != rec.company_id:
	# 			rec.diffrence = True
	# 			rec.write({'sec_diffrence': True})
	# 		else:
	# 			rec.write({'sec_diffrence': False})


	diffrence = fields.Boolean(default=False)
	sec_diffrence = fields.Boolean()

	document_number = fields.Char(related='move_id.document_number')
	paid_off = fields.Boolean()
	canceled = fields.Boolean()

	is_canceled_move = fields.Boolean()
	cancel_operation_type = fields.Selection([('reverse_move','Reverse Move'),('add_liability','Lift as Liability/Add to the Net Worth')], default='reverse_move')


	hide_in_sheet = fields.Boolean()

	sheet_id = fields.Many2one('bank.cash.balance.sheet')

	is_more_than_6_month = fields.Float(compute='get_is_more_than_6_month')



	def do_cancel_entery(self):

		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'account.move.cancel',
			'target':'new',
			'context' : {
				'bank_sheet_id' : self.id,
				'default_move_id':self.move_id.id,
				'default_date': self.date,
				'account_id' : self.account_id.id,
				'amount' : (self.debit + self.credit),
				'journal_id' : self.move_id.journal_id.id,
				'journal_account_id' : self.move_id.journal_id.default_debit_account_id.id,
				'partner_id' : self.partner_id.id,
				},
		}



	def get_is_more_than_6_month(self):
		for record in self:
			six_month_ago = fields.Date.today() + relativedelta(months=- 6)
			if six_month_ago > record.date:
				record.is_more_than_6_month = 1
			else:
				record.is_more_than_6_month = 0


class CancelMove(models.TransientModel):
	_name = 'account.move.cancel'

	operation_type = fields.Selection([('reverse_move','Reverse Move'),('add_liability','Lift as Liability/Add to the Net Worth')],default='reverse_move')
	account_id = fields.Many2one('account.account', string='Account')
	date = fields.Date()
	description = fields.Char()


	def do_execute_cancel_move(self):

		journal_id = False
		if self._context.get('journal_id', False):
			journal_id = self.env['account.journal'].search([('id', '=', self._context['journal_id'])])[0]

		if not self._context.get('journal_account_id', False):
			raise ValidationError(_('الرجاء تحديد حساب لـ' + journal_id.name ))

		if self._context.get('default_move_id',False):
			for account_move in self.env['account.move'].search([('id','=', self._context['default_move_id'] )]):
				for line in account_move.line_ids:
					line.is_canceled_move = True
					line.cancel_operation_type = self.operation_type

		if self.operation_type == 'reverse_move':
			if self._context.get('default_move_id',False):
				for account_move in self.env['account.move'].search([('id','=', self._context['default_move_id'] )]):

					copy_move = account_move.copy()

					copy_move.date = self.date
					copy_move.name = _('عكس القيد - مستند رقم ' + str(account_move.document_number) + ' --> ') + str(copy_move.name)
					copy_move.ref = _('عكس القيد --> ') + str(copy_move.ref)

					copy_move.line_ids = False

					lines = []

					line_debit = line_credit = 0

					for line in account_move.line_ids:
						if line.account_id.id != journal_id.default_debit_account_id.id :
							lines.append( (0,0,{
								'account_id' : line.account_id.id,
								'partner_id' : line.partner_id.id,
								'name' :  str('عكس القيد -- مستند رقم ') + str(account_move.document_number) + str(' -- ')  + str(line.name),
								'analytic_account_id' : line.analytic_account_id.id,
								'debit' : line.credit,
								'credit' : line.debit,
								'date_maturity' : self.date,
								'date' : self.date,
								}) )
						else:
							line_debit = line_debit + line.debit
							line_credit = line_credit + line.credit
					lines.append( (0,0,{
						'account_id' : journal_id.default_debit_account_id.id,
						'name' :  str('عكس القيد -- مستند رقم ') + str(account_move.document_number) + str(' -- ')  + str(account_move.name),
						'credit' : line_debit,
						'debit' : line_credit,
						'date_maturity' : self.date,
						'date' : self.date,
						}) )

					copy_move.line_ids = lines
					copy_move.post()


		if self.operation_type == 'add_liability':

			journal_id = self._context['journal_id']
			journal_account_id = self._context['journal_account_id']

			move = self.env['account.move'].create({
				'date':self.date,
				'journal_id' : journal_id,
				'name' : self.description,
				'line_ids' : [(0,0,{
					'account_id' : self.account_id.id ,
					'name' : self.description ,
					'debit' : 0,
					'credit' : self._context['amount'] ,
					'partner_id' : self._context['partner_id'],
					}),
				(0,0,{
					'account_id' : journal_account_id ,
					'name' : self.description ,
					'debit' : self._context['amount'],
					'credit' : 0,
					'partner_id' : self._context['partner_id'],
					}),
				]})
			move.post()



class BankSheetAddition(models.Model):
	_name = 'bank.sheet.addition'

	name = fields.Char(string='Description', readonly=True)
	the_type = fields.Selection([('addition','addition'),('subtraction','subtraction')], default='addition', readonly=True)
	amount = fields.Float(readonly=True)
	sheet_id = fields.Many2one('bank.cash.balance.sheet')
