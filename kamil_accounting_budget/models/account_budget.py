from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError
from datetime import date


class BudgetaryPosition(models.Model):
	_inherit = 'account.budget.post'

	analytic_account_id = fields.Many2one('account.analytic.account', string='Budget Item', domain=lambda self:self.get_budget_item_domain())
	accounts_value_ids = fields.One2many('budget.account.value','budgetary_position_id')

	date_from = fields.Date(default = lambda self: date(date.today().year, 1, 1)  )
	date_to = fields.Date( default = lambda self: date(date.today().year, 12, 31)  )

	@api.multi
	def get_budget_item_domain(self):
		budget_items_ids = []
		for account in self.env['account.account'].search([('is_group','=','sub_account')]):
			if account.parent_budget_item_id:
				budget_items_ids.append( account.parent_budget_item_id.id )
		if budget_items_ids:
			return [('id','in', budget_items_ids)]
		return []


	@api.multi
	@api.onchange('analytic_account_id')
	def onchange_budget_item(self):
		for record in self:
			if record.analytic_account_id:
				record.name = str(self.analytic_account_id.name)			
				record.accounts_value_ids = False
				record.account_ids = False

				# exsiting_account_ids = []
				# for line in record.accounts_value_ids:
				# 	if line.planned_value > 0:
				# 		exsiting_account_ids.append(line.account_id.id )
				
				for account in self.env['account.account'].search([('code','=like',record.analytic_account_id.code+ '%'),('is_group','=','sub_account')]):
					# if account.id not in exsiting_account_ids:
					record.accounts_value_ids = [(0,0,{'account_id': account.id})]
					record.account_ids = [(4, account.id)]


				# for account in record.analytic_account_id.account_ids:
				# 	if account.id not in exsiting_account_ids:
				# 		record.accounts_value_ids = [(0,0,{'account_id': account.id})]
				# 	record.account_ids = [(4, account.id)]


class BudgetAccountValue(models.Model):
	_name = 'budget.account.value'

	account_id = fields.Many2one('account.account', string='Account')
	planned_value = fields.Float(string='Planned Amount')
	addition_value = fields.Float(string='Addition Amount')
	withdraw_value  = fields.Float(string='Withdraw Amount')
	approved_value = fields.Float(string='Approved Amount', compute='compute_approved_value')
	reserved_value = fields.Float(string='Reserved Amount')
	practical_value =  fields.Float(string='Practical Amount', compute='_compute_practical_amount')
	remaining_value = fields.Float(string='Remaining Amount', compute='compute_remaining_value')

	budgetary_position_id = fields.Many2one('account.budget.post')

	date_from = fields.Date(realted='budgetary_position_id.date_from')
	date_to = fields.Date(realted='budgetary_position_id.date_to')
	

	analytic_account_id = fields.Many2one('account.analytic.account', realted='budgetary_position_id.analytic_account_id')

	company_id = fields.Many2one('res.company',default= lambda self:self.env.user.company_id.id)


	@api.multi
	@api.depends('planned_value','addition_value','reserved_value','practical_value')

	@api.multi
	def compute_approved_value(self):
		for record in self:
			record.approved_value = record.planned_value + record.addition_value - record.withdraw_value


	def compute_remaining_value(self):
		for record in self:
			# record.remaining_value = abs(record.approved_value) - abs(record.reserved_value) - abs(record.practical_value)
			record.remaining_value = abs(record.approved_value) - abs(record.practical_value)


			# if record.planned_value < 0:
			# 	record.remaining_value = ((abs(record.planned_value) - abs(record.withdraw_value) ) + abs(record.addition_value) - abs(record.reserved_value) - abs(record.practical_value) )* -1

			# else:
			# 	record.remaining_value = (record.planned_value + record.addition_value) - (record.withdraw_value) - (record.reserved_value - record.practical_value) 



	@api.multi
	def _compute_practical_amount(self):
		for line in self:
			date_to = line.budgetary_position_id.date_to
			date_from = line.budgetary_position_id.date_from

			if line.account_id and line.budgetary_position_id.analytic_account_id and date_from and date_to:
				
				self._cr.execute("select sum(COALESCE( debit, 0 ) ) - sum(COALESCE( credit, 0 ) )  from account_move_line where account_id="  + str(line.account_id.id) + " AND date >= '" + str(date_from) + "'    AND date <=  '" + str(date_to) +  "'  " )

				line.practical_value = abs(self.env.cr.fetchone()[0] or 0.0)
				
				# if line.practical_value < 0:
					# line.practical_value = line.practical_value * -1>
				# account_total = line.practical_value
			# print('$$######/###  account_total = ', account_total)
			# print('\n\n\n')




class AnalyticAccount(models.Model):
	_inherit = 'account.analytic.account'

	account_ids = fields.Many2many('account.account', string='Accounts')


class BudgetLine(models.Model):
	_inherit = 'crossovered.budget.lines'

	revenues_budget_id = fields.Many2one('crossovered.budget')
	expenses_budget_id = fields.Many2one('crossovered.budget')
	crossovered_budget_id = fields.Many2one('crossovered.budget', 'Budget', ondelete='cascade', index=True, required=False, default=lambda self:self.get_default_budget())

	@api.model 
	def create(self,vals):
		if not vals.get('crossovered_budget_id', False):
			if vals.get('revenues_budget_id', False):
				vals['crossovered_budget_id'] = vals['revenues_budget_id']			
			if vals.get('expenses_budget_id', False):
				vals['crossovered_budget_id'] = vals['expenses_budget_id']
		return super(BudgetLine, self).create(vals)

    

	@api.multi
	def get_default_budget(self):
		for record in self:
			if not record.crossovered_budget_id:
				if record.revenues_budget_id :
					record.crossovered_budget_id = record.revenues_budget_id
				if record.expenses_budget_id:
					record.crossovered_budget_id = record.expenses_budget_id


	addition_value = fields.Float(string='Addition Amount', compute='compute_values')
	withdraw_value = fields.Float(string='Withdraw Amount', compute='compute_values')
	approved_value = fields.Float(string='Approved Amount', compute='compute_values')
	reserved_value = fields.Float(string='Reserved Amount', compute='compute_values')
	remaining_value = fields.Float(string='Remaining Amount' , compute='compute_remaining_value')
	planned_amount = fields.Float(compute='compute_values')
	analytic_account_id = fields.Many2one('account.analytic.account', realted='general_budget_id.analytic_account_id')
	practical_amount = fields.Float(compute='compute_values')

	date_from = fields.Date(realted='general_budget_id.date_from')
	date_to = fields.Date(realted='general_budget_id.date_to')

			
	@api.multi
	def compute_values(self):
		for record in self:
			total_practical_amount = 0
			total_planned_amount = 0
			total_addition_amount = 0
			total_reserved_amount = 0
			total_withdraw_amount = 0
			total_approved_amount = 0


			for line in record.general_budget_id.accounts_value_ids:
				total_practical_amount = total_practical_amount + line.practical_value
				total_planned_amount = total_planned_amount + line.planned_value
				total_addition_amount = total_addition_amount + line.addition_value
				total_reserved_amount = total_reserved_amount + line.reserved_value
				total_withdraw_amount = total_withdraw_amount + line.withdraw_value
				total_approved_amount = total_approved_amount + line.approved_value

			record.practical_amount = total_practical_amount
			record.planned_amount = total_planned_amount
			record.addition_value = total_addition_amount
			# record.reserved_value = total_reserved_amount
			record.withdraw_value = total_withdraw_amount
			record.approved_value = total_approved_amount


	@api.multi
	@api.depends('planned_amount','addition_value','reserved_value','practical_amount')
	def compute_remaining_value(self):
		for record in self:
			# record.remaining_value = abs(record.approved_value) - abs(record.reserved_value) - abs(record.practical_amount)
			record.remaining_value = abs(record.approved_value) - abs(record.practical_amount)

			# if record.planned_amount < 0:
			# 	record.remaining_value = ((abs(record.planned_amount) - abs(record.withdraw_value) ) + abs(record.addition_value) - abs(record.reserved_value) - abs(record.practical_amount) )* -1
			# else:
			# 	record.remaining_value = (record.planned_amount - record.withdraw_value + record.addition_value) - (record.reserved_value - record.practical_amount) 


	@api.multi
	@api.onchange('general_budget_id')
	def onchange_budgetary_position(self):
		if self.general_budget_id:
			if self.general_budget_id.analytic_account_id:
				self.analytic_account_id = self.general_budget_id.analytic_account_id.id 
			else:
				self.analytic_account_id = False
			if self.general_budget_id.date_from:
				self.date_from = self.general_budget_id.date_from
			if self.general_budget_id.date_to:
				self.date_to = self.general_budget_id.date_to

		else:
			self.analytic_account_id = False



class Budget(models.Model):
	_inherit = 'crossovered.budget'
	_order = 'id desc'

	date_from = fields.Date(default = lambda self: date(date.today().year, 1, 1)  )
	date_to = fields.Date( default = lambda self: date(date.today().year, 12, 31)  )

	is_started = fields.Boolean()


	revenues_line_ids = fields.One2many('crossovered.budget.lines', 'revenues_budget_id', string='Revenues',copy=True)
	expenses_line_ids = fields.One2many('crossovered.budget.lines', 'expenses_budget_id', string='Expenses',copy=True)


	def do_start(self):
		
		self.is_started = True		

		self.revenues_line_ids = False
		self.expenses_line_ids = False

		budget_items_ids = []
		# for account in self.env['account.account'].search([('is_group','=','sub_account')]):
		# 	if account.parent_budget_item_id:
		# 		budget_items_ids.append( account.parent_budget_item_id.id )

		for account in self.env['account.account'].search([('is_group','=','group')]):
			if len(account.code) == 2:
				budget_items_ids.append( account.code )

		account_list = []

		for budget_line in self.env['account.analytic.account'].search([('code','in',budget_items_ids)]):
			if budget_line.code not in account_list:
				account_list.append(budget_line.code)
				if budget_line.code[:1] == '1':
			
					
					list_of_lines = []
					list_of_account_lines = []
					for the_account in self.env['account.account'].search([('code','=like',budget_line.code+ '%'),('is_group','=','sub_account')]):
						
						list_of_lines.append( (0,0,{
							'account_id': the_account.id,
							'planned_value' : the_account.budget_amount,
							}) )
						list_of_account_lines.append( (4, the_account.id) )

					general_budget_id = self.env['account.budget.post'].create({
						'analytic_account_id' : budget_line.id,
						'date_from' : self.date_from,
						'date_to' : self.date_to,
						'account_ids':list_of_account_lines,
						'accounts_value_ids' : list_of_lines,
						'name' : budget_line.name,
						})

					self.revenues_line_ids = [(0,0,{
						'general_budget_id' : general_budget_id.id,
						'analytic_account_id' : budget_line.id,
						'date_from' : self.date_from,
						'date_to' : self.date_to,
					})]

				if budget_line.code[:1] in ['2'] or budget_line.code[:2] in ['30']:

					list_of_lines = []
					list_of_account_lines = []
					for the_account in self.env['account.account'].search([('code','=like',budget_line.code+ '%'),('is_group','=','sub_account')]):
						
						list_of_lines.append( (0,0,{
							'account_id': the_account.id,
							'planned_value' : the_account.budget_amount,
							}) )
						list_of_account_lines.append( (4, the_account.id) )

					general_budget_id = self.env['account.budget.post'].create({
						'analytic_account_id' : budget_line.id,
						'date_from' : self.date_from,
						'date_to' : self.date_to,
						'account_ids':list_of_account_lines,
						'accounts_value_ids' : list_of_lines,
						'name' : budget_line.name,
						})

					self.expenses_line_ids = [(0,0,{
						'general_budget_id' : general_budget_id.id,
						'analytic_account_id' : budget_line.id,
						'date_from' : self.date_from,
						'date_to' : self.date_to,
					})]









	@api.multi
	def budget_operations(self, do_just_check=False, do_reserve=False, do_actual=False, budget_item=False, account=False,amount=0.0, date=False):
		account_found = False
		budget_found = False
		
		for budget in self.env['crossovered.budget'].search([('state','=','validate'),('date_from','<=',date),('date_to','>=',date)]):

			for revenues_line in budget.revenues_line_ids:
				for buget_detail in revenues_line.general_budget_id.accounts_value_ids:



			# for budget_line in budget.revenues_line_ids:
				
			# 	if budget_line.date_from <= date and budget_line.date_to >= date:
					
						budget_found = True
					# for buget_detail in budget_line.general_budget_id.accounts_value_ids:
						if buget_detail.account_id == account:
							account_found = True
							if do_actual:

								if buget_detail.planned_value < 0:
										# buget_detail.reserved_value = (abs(buget_detail.reserved_value) - amount) * -1
										pass
								else:
									pass
									# buget_detail.reserved_value = (abs(buget_detail.reserved_value) - amount) 

							if abs(buget_detail.remaining_value) < amount:
								if do_just_check:
									raise ValidationError(_('there is no enough budget for the account ' + account.name ))
							
								if do_reserve:
									raise ValidationError(_('there is no enough budget for the account ' + account.name ))
							else:
								if do_reserve:
									if buget_detail.planned_value < 0:
										# buget_detail.reserved_value = (abs(buget_detail.reserved_value) + amount) * -1
										pass
									else:
										pass
										# buget_detail.reserved_value = (abs(buget_detail.reserved_value) + amount) 


			for expenses_line in budget.expenses_line_ids:
				for buget_detail in expenses_line.general_budget_id.accounts_value_ids:

			# for budget_line in budget.expenses_line_ids:
			# 	if budget_line.analytic_account_id == budget_item and budget_line.date_from <= date and budget_line.date_to >= date:

						budget_found = True
					# for buget_detail in budget_line.general_budget_id.accounts_value_ids:

						if buget_detail.account_id == account:
							account_found = True
							if do_actual:
								if buget_detail.planned_value < 0:
										# buget_detail.reserved_value = (abs(buget_detail.reserved_value) - amount) * -1
										pass
								else:
									# buget_detail.reserved_value = (abs(buget_detail.reserved_value) - amount) 
									pass

							if abs(buget_detail.remaining_value) < amount:
								if do_just_check:
									raise ValidationError(_('there is no enough budget for the account ' + account.name ))
							
								if do_reserve:
									raise ValidationError(_('there is no enough budget for the account ' + account.name ))
							else:
								if do_reserve:
									if buget_detail.planned_value < 0:
										pass
										# buget_detail.reserved_value = (abs(buget_detail.reserved_value) + amount) * -1
									else:
										pass
										# buget_detail.reserved_value = (abs(buget_detail.reserved_value) + amount) 



		if not budget_found:
			raise ValidationError(_('There is No Budget Found'))
		if not account_found:
			raise ValidationError(_('There no budget for the Account ' + account.name ))



