from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError
from . import amount_to_text as amount_to_text_ar


class CostCenter(models.Model):
	_name = 'kamil.account.cost.center'

	name = fields.Char()
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)



class AnalyticLine(models.Model):
	_inherit = 'account.analytic.line'

	cost_center_id = fields.Many2one('kamil.account.cost.center')


	@api.model 
	def create(self, vals):
		
		if vals.get('amount', False):
			if float(vals['amount'])  < 0:
				vals['amount'] = abs(float(vals['amount']) )

		created_id = super(AnalyticLine, self).create(vals)

		if created_id.move_id :
			created_id.cost_center_id = created_id.move_id.cost_center_id

		return created_id



class AccountMove(models.Model):
	_inherit = 'account.move'

	amount_in_words = fields.Char(compute='get_amount_in_words')
	document_number = fields.Char(default='-')
	is_manual_move = fields.Boolean()
	is_manual_move = fields.Boolean()
	ratification_payment_id = fields.Many2one('ratification.payment')




	@api.multi
	def get_amount_in_words(self):
		for record in self:
			record.amount_in_words = amount_to_text_ar.amount_to_text(record.amount, 'ar')


class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	cost_center_id = fields.Many2one('kamil.account.cost.center')
	document_number = fields.Char(related='move_id.document_number')
	remaining_value = fields.Float(compute='get_budget_amounts')
	approved_value = fields.Float(compute='get_budget_amounts')

	@api.onchange('account_id')
	def onchange_account(self):
		for record in self:
			if record.account_id:
				record.analytic_account_id = record.account_id.parent_budget_item_id

	@api.depends('account_id','analytic_account_id')
	def get_budget_amounts(self):
		for record in self:
			if record.account_id:
				for budget in self.env['crossovered.budget'].search([('state','=','validate'),('date_from','<=',record.date),('date_to','>=',record.date)]):
					for budget_line in budget.expenses_line_ids:
						for buget_detail in budget_line.general_budget_id.accounts_value_ids:
							if buget_detail.account_id == record.account_id:
								if buget_detail.approved_value > 0:
									record.approved_value = buget_detail.approved_value
								if buget_detail.remaining_value:
									record.remaining_value = buget_detail.remaining_value
			else:
				record.analytic_account_id = False


	@api.onchange('debit')
	def onchange_amount(self):
		for record in self:
			budget_found = 0
			if record.account_id:
				for budget in self.env['crossovered.budget'].search([('state','=','validate'),('date_from','<=',record.date),('date_to','>=',record.date)]):
					for budget_line in budget.expenses_line_ids:
						for buget_detail in budget_line.general_budget_id.accounts_value_ids:
							if buget_detail.account_id == record.account_id:
								if buget_detail.planned_value != 0:
									budget_found = 1
								if buget_detail.approved_value > 0:
									record.approved_value = buget_detail.approved_value
								if buget_detail.remaining_value:
									record.remaining_value = buget_detail.remaining_value
			if record.analytic_account_id:
				if budget_found == 1 and record.debit > record.remaining_value  and record.account_id.code[:1] in ['2']:
					record.debit = 0
					self.env.user.sudo().notify_warning(_('There is no Enough Budget'))

					warning_mess = {
						'title': _('There is no Enough Budget'),
						'message' : _( 'يوجد فقط مبلغ ' + str( '{:,.2f}'.format( record.remaining_value )  ) + ' بالبند '),
					}
					return {'warning' : warning_mess}

class CurrencyRate(models.Model):
	_inherit = "res.currency.rate"

	rate = fields.Float(digits=(30, 15), default=1.0, help='The rate of the currency to the currency of rate 1')


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	budget_item_id = fields.Many2one('account.analytic.account', string='Budget Item')



class StockLocation(models.Model):
	_inherit = 'stock.location'

	account_id = fields.Many2one('account.account', string='Stock Account')


class ProductCategory(models.Model):
	_inherit = 'product.category'

	budget_item_id = fields.Many2one('account.analytic.account', string='Budget Item')


class AnalyticAccount(models.Model):
	_inherit = 'account.analytic.account'

	is_group = fields.Selection([('group','Group'),('sub_account','Sub Account')],default='group' )

class Account(models.Model):
	_inherit = 'account.account'

	budget_item_id = fields.Many2one('account.analytic.account', string='Budget Item')
	parent_budget_item_id = fields.Many2one('account.analytic.account', string='Parent Budget Item', compute='get_parent_budget_item', store=True)
	is_group = fields.Selection([('group','Group'),('sub_account','Sub Account')],default='group' )
	budget_amount = fields.Float()
	clarification_number = fields.Char()

	is_inventory_account = fields.Boolean(string='Is Inventory Account')


	@api.multi
	@api.depends('code','name','is_group','budget_item_id')
	def get_parent_budget_item(self):
		for record in self:
			if record.code:
				parent_budget_item_code = record.code[:-1]
				if parent_budget_item_code:
					found = False
					for budget_item in self.env['account.analytic.account'].search([('code','=',parent_budget_item_code)]):
						record.parent_budget_item_id = budget_item.id 
						found = True
					if not found:
						code = parent_budget_item_code
						i = 0
						for i in range(len(parent_budget_item_code)):
							sub_code = code[:( (i+1) * -1 )]
							if sub_code and not found:
								for budget_item in self.env['account.analytic.account'].search([('code','=',sub_code)]):
									record.parent_budget_item_id = budget_item.id 
									found = True
									break


	@api.model
	def create(self,vals):
		created_id = super(Account, self).create(vals)
		created_id.budget_item_id = self.env['account.analytic.account'].create({
				'name' : created_id.name,
				'code' : created_id.code,
				'is_group' :  created_id.is_group,
				'company_id' : created_id.company_id.id,
			})
		return created_id

	@api.multi
	def write(self,vals):

		write_id = super(Account, self).write(vals)
		for record in self.env['account.account'].search([('id','in', self._ids )]):
			if record.budget_item_id:
				for key in vals.keys():
					if key == 'name':
						record.budget_item_id.name = vals['name']
					if key == 'code' : 
						record.budget_item_id.code = vals['code']
					if key == 'is_group' : 
						record.budget_item_id.is_group = vals['is_group']
					if key == 'company_id' :
						record.budget_item_id.company_id = vals['company_id']

			else:
				name = record.name
				code = record.name 
				is_group = record.is_group
				company_id = record.company_id.id

				for key in vals.keys():
					if key == 'name':
						name = vals['name']
					if key == 'code' : 
						code = vals['code']
					if key == 'is_group' :
						is_group = vals['is_group']
					if key == 'company_id':
						company_id = vals['company_id']

				record.budget_item_id = self.env['account.analytic.account'].create({
						'name'  : name,
						'code' : code,
						'is_group' : is_group,
						'company_id' : company_id,
					})

		return write_id
	

	@api.multi 
	@api.onchange('parent_id')
	def onchange_parent(self):
		for record in self:
			if record.parent_id:
				max_number = []
				for account in self.env['account.account'].search([('code','=like',record.parent_id.code+ '_'),('code','!=',record.parent_id.code)]):
					code = [int(i) for i in account.code.split() if i.isdigit()]
					max_number.append( code[0] % 10 )
				next_number = 0

				if max_number:
					next_number  =  max( max_number ) + 1
				record.code = record.parent_id.code + str( next_number ) 
	




# class PartnerMerge(models.TransientModel):
# 	_inherit = 'base.partner.merge.automatic.wizard'

# 	bank_name = fields.Char(related='dst_partner_id.bank_name')
# 	account_number = fields.Char(related='dst_partner_id.account_number')
# 	bank_branch_name = fields.Char(related='dst_partner_id.bank_branch_name')


class Partner(models.Model):
	_inherit = 'res.partner'

	bank_name = fields.Char()
	account_number = fields.Char()
	bank_branch_name = fields.Char()

	code = fields.Char()

	# property_account_receivable_id 
	# property_account_payable_id = fields.Many2one('account.account', default= lambda self:self.get_medical_centers_account())

	department_id = fields.Many2one('hr.department', compute='get_emplyoee_department')

	
	# @api.multi
	# def name_get(self):
	# 	result = []
	# 	for partner in self:
	# 		if partner.code:
	# 			name = '[' + partner.code + '] ' + partner.name
	# 			result.append((partner.id, name))
	# 		else:
	# 			result.append((partner.id, partner.name))

	# 	return result

	@api.multi
	def get_emplyoee_department(self):
		for record in self:
			for employee in self.env['hr.employee'].search([('parent_id','=',record.id)]):
				record.department_id = employee.department_id

	@api.model
	def create(self, vals):
		res = super(Partner, self).create(vals)
		if vals.get('name', False):
			for record in self.env['res.partner'].search([('name','=',vals['name']),('company_id','=',res.company_id.id),('id','!=',res.id)]):
				raise ValidationError("There is an other partner with the same name!! ")
		return res


	@api.multi
	def write(self, vals):
		if vals.get('name', False):
			for record in self.env['res.partner'].search([('name','=',vals['name']), ('id','not in', self._ids),('company_id','=',self.company_id.id)]):
				raise ValidationError("There is an other partner with the same name!! ")
		return super(Partner, self).write(vals)
		

class Journal(models.Model):
	_inherit = 'account.journal'

	full_name = fields.Char(string='Full Name')
	account_number = fields.Char(string='Account Number')
	available_balance_str = fields.Char(compute='get_available_balance_str')

	@api.multi
	def get_available_balance_str(self):
		for record in self:
			if record.default_credit_account_id:
				self._cr.execute("select sum(COALESCE( debit, 0 ))-sum(COALESCE( credit, 0 )) from account_move_line where account_id="  + str(record.default_credit_account_id.id) + " " )
				balance = self.env.cr.fetchone()[0] or 0.0
			else:
				balance = 0

			str_balance = str('{:,.2f}'.format( balance ) )
			if balance < 0:
				str_balance = '(' + str('{:,.2f}'.format( balance ) ) + ')'
			record.available_balance_str = str_balance

class BranchAccounts(models.Model):
	_name = 'branch.account'
	_rec_name = 'company_id'
	_order = 'id desc'

	company_id = fields.Many2one('res.company', string='The Company',default= lambda self:self.env.user.company_id.id)

	company_ids = fields.One2many('branch.account.line','branch_account_id')

class BranchAccountsLine(models.Model):
	_name = 'branch.account.line'


	branch_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)	
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	
	account_id = fields.Many2one('account.account', string='Account', domain=[('is_group','=','sub_account')])

	branch_account_id = fields.Many2one('branch.account')



class User(models.Model):
	_inherit = 'res.users'

	email = fields.Char(default='user@example.com')



