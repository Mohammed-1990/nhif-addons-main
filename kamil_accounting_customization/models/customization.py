from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError
from . import amount_to_text as amount_to_text_ar

from dateutil.relativedelta import relativedelta

class Customization(models.Model):
	_name = 'kamil.customization'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']
	_description = 'Customization'
	_order = 'id desc'

	name = fields.Char(string='Description', track_visibility='always')
	year = fields.Char(track_visibility='always')
	month = fields.Selection([(1,'January'),(2, 'February'),(3, 'March'),(4, 'April'),(5, 'May'),(6, 'June'),(7, 'July'),(8, 'August'),(9, 'September'),(10, 'October'),(11, 'November'),(12, 'December')], default=1,track_visibility='always')
	state = fields.Selection([('draft','Draft'),('customization_calculated','Customization Calculated'),('confirmed','Confirmed'),('validated','Validated'),('canceled','Canceled')], default='draft',track_visibility='always')

	line_ids = fields.One2many('kamil.customization.line','customization_id')

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	
	
	@api.multi
	def do_calculate_customization(self):
		self.line_ids = False
		for branch in self.env['res.company'].sudo().search([]):
			customization_line = self.line_ids = [(0,0,{
				'branch_id' : branch.id,
				'customization_id' : self.id,
				})]		

		for line in self.line_ids:
			line.compute_lines()
		self.state = 'customization_calculated'

	@api.multi
	def do_confirm(self):
		self.state = 'confirmed'
	
	@api.multi
	def do_validate(self):
		for line in self.line_ids:
			line.do_confirm()



			customization_lines = []
			for customization_line in line.customization_ids:
				account_id = False

				for account in self.env['account.account'].search([('company_id','=',line.branch_id.id),('code','=', customization_line.account_id.code )]):
					account_id = account.id 

				customization_lines.append( (0,0,{
					'name' : customization_line.line_id.name,
					'account_id' : account_id,
					'amount' : customization_line.amount,
					'reserved_amount' : customization_line.reserved_amount,
					'remaining_amount' : customization_line.remaining_amount,
					}) )



			income_lines = []
			for income_line in line.income_from_branches_ids:
				
				account_id = False
				code = income_line.account_code or income_line.account_id.code
				for account in self.env['account.account'].search([('company_id','=',line.branch_id.id),('code','=', code )]):
					account_id = account.id 

				income_lines.append( (0,0,{
					'name' : income_line.name,
					'account_id' : account_id,
					'amount' : income_line.amount,
					'branch_id' : income_line.branch_id.id,
					}) )

			deduction_lines = []
			for deduction_line in line.deduction_ids:
				
				account_id = False
				analytic_account_id = False

				code = deduction_line.account_code or deduction_line.account_id.code
				for account in self.env['account.account'].search([('company_id','=',line.branch_id.id),('code','=', code )]):
					account_id = account.id 
					analytic_account_id = account.parent_budget_item_id.id

				deduction_lines.append( (0,0,{
					'name' : deduction_line.name,
					'account_id' : account_id,
					'amount' : deduction_line.amount,
					'branch_id' : deduction_line.the_payment_branch_id.id,
					'analytic_account_id' : analytic_account_id,
					}) )


			self.env['kamil.customization.result'].create({
				'branch_id' : line.branch_id.id ,
				'year' : line.year,
				'month' : line.month,
				'operation_date' : fields.Date.today(),
				'customization_amount' : line.customized_amount,
				'clearance_amount' : line.abs_clearing_amount,
				'transfered_amount' : line.transfered_amount,
				'customization_line_ids' : customization_lines,
				'income_line_ids' : income_lines,
				'deduction_line_ids' : deduction_lines,
			})


	# branch_id = fields.Many2one('res.company')
	# year = fields.Char()
	# month = fields.Char()
	# operation_date = fields.Date()

	# customization_amount = fields.Float()
	# clearance_amount = fields.Float()
	# transfered_amount 



		self.state = 'validated'

	@api.multi
	def do_cancel(self):
		self.state = 'canceled'


	


class CustomizationLine(models.Model):
	_name = 'kamil.customization.line'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']
	_description = 'Customization Details'
	_order = 'id desc'

	branch_id = fields.Many2one('res.company', string='Branch',track_visibility='always')
	customized_amount = fields.Float(compute='get_customize_amount',track_visibility='always')
	clearing_amount = fields.Float(compute='get_clearing_amount',track_visibility='always',string='Clearing Amount')
	abs_clearing_amount = fields.Float(compute='get_clearing_amount',track_visibility='always',string='Clearing Amount')
	transfered_amount = fields.Float(compute='get_transfered_amount',track_visibility='always')

	customization_id = fields.Many2one('kamil.customization', ondelete='cascade',track_visibility='always')
	name = fields.Char(related='customization_id.name',track_visibility='always')
	year = fields.Char(related='customization_id.year',track_visibility='always')
	month = fields.Selection(related='customization_id.month',track_visibility='always')

	customization_ids = fields.Many2many('collection.collection.line', string="Customization")

	loans_from_branches_ids = fields.Many2many('payment.ratification.line','ratification_loan_rel','ratification_line_id','customization_id', string='Other Branchs Debts', domain=[('has_installments','=',False)])
	income_from_branches_ids = fields.Many2many('payment.ratification.line','ratification_income_rel','ratification_line_id','customization_id', string='Income from Other Branchs', domain=[('has_installments','=',False)])
	deduction_ids = fields.Many2many('payment.ratification.line','ratification_deduction_rel','ratification_line_id','customization_id', string='Other Deductions', domain=[('has_installments','=',False)])
	state = fields.Selection([('calculated','Calculated'),('confirmed','Confirmed'),('canceled','Canceled')], default='calculated',track_visibility='always')
	# state = fields.Selection([('calculated','Calculated'),('installment_calculated','Installment Calculated')], default='calculated')

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	

	@api.multi
	def action_open_customization_details(self):
		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'kamil.customization.line',
			'res_id' : self.id,
		}



	@api.multi
	def compute_lines(self):
		self.compute_customization()
		self.compute_loans_from_branches()
		self.compute_income_from_branches()
		self.compute_deduction()
		self.compute_installments()

	@api.multi
	def do_confirm(self):
		self.compute_lines()
		self.state = 'confirmed'

	@api.multi
	def do_cancel(self):
		self.state = 'canceled'

	@api.multi
	def compute_customization(self):
		# self.customization_ids = False
		for line in self.customization_ids:
			line.unlink()
		for collection_line in self.env['collection.collection.line'].sudo().search([('line_id.operation_type','=', 'customization'),('branch_id','=', self.branch_id.id),('line_id.state','in',['internal_auditor_audit','collected'])]):
			if (int(collection_line.line_id.subscription_date_from.year) <= int( self.year ) and int(collection_line.line_id.subscription_date_from.month) <= int(self.month) ) and (int(collection_line.line_id.subscription_date_to.year) >= int( self.year ) and int(collection_line.line_id.subscription_date_to.month) >= int(self.month) ):
				# self.customization_ids = [(4, collection_line.id )]
				self.customization_ids = [(0,0,{
					'branch_id' : collection_line.branch_id.id ,
					'name' : collection_line.line_id.name ,
					'analytic_account_id': collection_line.analytic_account_id.id,
					'account_id': collection_line.account_id.id,
					'amount': collection_line.amount,
					'customization_collection_line_id' : collection_line.line_id.id,
					})]
			

	@api.multi
	def compute_loans_from_branches(self):

		for line in self.loans_from_branches_ids:
			line.unlink()

		# for payment_line in self.env['payment.ratification.line'].sudo().search([('payment_id.branch_id.id','!=', self.branch_id.id ),('branch_id','=',self.branch_id.id),('ratification_type','=','service_provider_claim'),('payment_id.state','=','approved')]):
		# 	if int(payment_line.payment_id.date.month) == int(self.month) and int(payment_line.payment_id.date.year) == int(self.year) :
		# 		self.loans_from_branches_ids = [(0,0,{
		# 			'parent_branch_id': payment_line.payment_id.branch_id.id,
		# 			'name' : payment_line.name ,
		# 			'analytic_account_id': payment_line.analytic_account_id,
		# 			'account_id': payment_line.account_id,
		# 			'amount': payment_line.amount,
		# 			'is_linked_with_customization':True,
		# 			'date':payment_line.payment_id.date,
		# 			'line_type' : 'loan',
		# 			'customization_line_id' : self.id,
		# 			'branch_id' : payment_line.branch_id.id,
		# 			'payment_branch_id' : payment_line.payment_id.branch_id,
		# 			'ratification_type' : payment_line.ratification_type,
		# 			'the_payment_branch_id' : payment_line.payment_id.branch_id,
		# 			'item_type' : payment_line.item_type,
		# 			'account_code' : payment_line.account_code,
		# 			})]


	@api.multi
	def compute_income_from_branches(self):
		# self.income_from_branches_ids = False	
		for line in self.income_from_branches_ids:
			line.unlink()		
		for payment_line in self.env['payment.ratification.line'].sudo().search([('payment_id.branch_id.id','=', self.branch_id.id ),('branch_id','!=',self.branch_id.id),('payment_id.state','=','approved')]):
			if int(payment_line.payment_id.date.month) == int(self.month) and int(payment_line.payment_id.date.year) == int(self.year) :
				
					# self.income_from_branches_ids = [(4,payment_line.id)]
					self.income_from_branches_ids = [(0,0,{
						'branch_id': payment_line.branch_id.id,
						'name' : payment_line.name ,
						'analytic_account_id': payment_line.analytic_account_id,
						'account_id': payment_line.account_id,
						'amount': payment_line.amount,
						'is_linked_with_customization':True,
						'date':payment_line.payment_id.date,
						'line_type' : 'income',
						'customization_line_id' : self.id,
						'branch_id' : payment_line.branch_id.id,
						'payment_branch_id' : payment_line.payment_id.branch_id,
						'ratification_type' : payment_line.ratification_type,
						'the_payment_branch_id' : payment_line.payment_id.branch_id,
						'item_type' : payment_line.item_type,
						'account_code' : payment_line.account_code,
						})]

	@api.multi
	def compute_deduction(self):
		# self.deduction_ids = False	
		for line in self.deduction_ids:
			line.unlink()

		for payment_line in self.env['payment.ratification.line'].sudo().search([('payment_id.branch_id.id','!=', self.branch_id.id ),('branch_id','=',self.branch_id.id),('payment_id.state','=','approved')]):

			if int(payment_line.payment_id.date.month) == int(self.month) and int(payment_line.payment_id.date.year) == int(self.year) :			
				# self.deduction_ids = [(4,payment_line.id)]
				self.deduction_ids = [(0,0,{
					'branch_id': payment_line.branch_id.id,
					'name' : payment_line.name ,
					'analytic_account_id': payment_line.analytic_account_id,
					'account_id': payment_line.account_id,
					'amount': payment_line.amount,
					'is_linked_with_customization':True,
					'date':payment_line.payment_id.date,
					'line_type':'deduction',
					'customization_line_id' : self.id,
					'branch_id' : payment_line.branch_id.id,
					'payment_branch_id' : payment_line.payment_id.branch_id,
					'ratification_type' : payment_line.ratification_type,
					'the_payment_branch_id' : payment_line.payment_id.branch_id,
					'item_type' : payment_line.item_type,
					'account_code' : payment_line.account_code,
					})]


	@api.multi
	def compute_installments(self, line_id=False):

		line = False
		if line_id:
			line = self.env['payment.ratification.line'].search([('id','=',line_id)])
			if line:
				line = line[0]

			self.deduction_ids = [(3,line_id)]


		for payment_line in self.env['payment.ratification.line'].sudo().search([('is_installment','=',True),('customization_branch_id','=',self.branch_id.id)]):

			if line:			
			
				if not payment_line.account_id:
					payment_line.account_id = line.account_id.id
					
				if not payment_line.analytic_account_id:
					payment_line.analytic_account_id = line.analytic_account_id.id 
				
				if not payment_line.the_payment_branch_id:
					payment_line.the_payment_branch_id = line.the_payment_branch_id

				if not payment_line.ratification_type:
					payment_line.ratification_type = line.ratification_type

				if not payment_line.item_type:
					payment_line.item_type = line.item_type
				payment_line.is_installment = True


			if int(payment_line.date.month) == int(self.month) and int(payment_line.date.year) == int(self.year) :

				self.deduction_ids = [(4,payment_line.id)]


			
				for deduction_line in self.deduction_ids:
					if line:
						if not deduction_line.account_id:
							deduction_line.account_id = line.account_id.id

						if not deduction_line.analytic_account_id:
							deduction_line.analytic_account_id = line.analytic_account_id.id 
						
						if not deduction_line.the_payment_branch_id:
							deduction_line.the_payment_branch_id = line.the_payment_branch_id

						if not deduction_line.ratification_type:
							deduction_line.ratification_type = line.ratification_type

						if not deduction_line.item_type:
							deduction_line.item_type = line.item_type



	@api.multi 
	def action_open_installments(self):
		pass


	@api.multi
	@api.depends('customization_ids')
	def get_customize_amount(self):
		for record in self:
			total = 0
			for line in record.customization_ids:
				total = total + line.remaining_amount
			record.customized_amount = total

	@api.multi
	@api.depends('income_from_branches_ids','loans_from_branches_ids','deduction_ids')
	def get_clearing_amount(self):
		for record in self:
			total_income = 0
			total_loans = 0
			total_deduction = 0
			for line in record.income_from_branches_ids:
				total_income = total_income + line.amount
			for line in record.loans_from_branches_ids:
				total_loans = total_loans + line.amount
			for line in record.deduction_ids:
				total_deduction = total_deduction + line.amount
			record.clearing_amount = total_income - (total_loans + total_deduction)

			record.abs_clearing_amount = abs( total_income - (total_loans + total_deduction) )
		

	@api.multi
	@api.depends('customization_ids')
	def get_transfered_amount(self):
		for record in self:
			customized_amount = 0
			for line in record.customization_ids:
				customized_amount = customized_amount + line.remaining_amount

			record.transfered_amount = customized_amount + record.clearing_amount   


class PaymentLine(models.Model):
	_inherit = 'payment.ratification.line'
	_order = 'id desc'

	date = fields.Date()
	no_of_installments = fields.Integer(string='No. of Installmets')
	no_of_installment_ids = fields.One2many('payment.ratification.line', 'payment_line_id')
	is_linked_with_customization = fields.Boolean(default=False)
	has_installments = fields.Boolean(default=False)
	start_date = fields.Date(default=lambda self: fields.Date.today())
	payment_term = fields.Selection([(1,'Monthly'),(3,'Quarterly'),(6,'Biannual'),(12,'Annual')], default=1)
	payment_line_id = fields.Many2one('payment.ratification.line', ondelete='cascade')
	line_type = fields.Selection([('loan','loan'),('income','income'),('deduction','deduction')])
	customization_line_id = fields.Many2one('kamil.customization.line')
	customization_state = fields.Selection([('calculated','Calculated'),('confirmed','Confirmed')], default='calculated')

	customization_payment_line_id = fields.Many2one('ratification.payment')

	payment_branch_id = fields.Many2one('res.company')
	payment_date = fields.Date()
	is_installment = fields.Boolean(default=False)

	the_payment_branch_id = fields.Many2one('res.company', string="Branch")
	customization_branch_id = fields.Many2one('res.company')
	the_line_id = fields.Many2one('payment.ratification.line')
	the_line_number = fields.Integer()

	@api.multi
	def do_confirm(self):

		# self.customization_state = 'confirmed'
		# self.has_installments = True
		self.customization_line_id.compute_installments(line_id=self.id)
		
		# for line in self.no_of_installment_ids:
		# 	if self.line_type == 'loan':
		# 		self.customization_line_id.loans_from_branches_ids = [(0,0,{
		# 			'name' : line.name,
		# 			'branch_id': self.branch_id.id,
		# 			'analytic_account_id' : self.analytic_account_id.id,
		# 			'account_id' : self.account_id.id,
		# 			'amount' : line.amount,
		# 			'date' : self.date,
		# 			'is_linked_with_customization' : True,
		# 			'line_type' : self.line_type,
		# 			})]

		# 	if self.line_type == 'income':
		# 		self.customization_line_id.income_from_branches_ids = [(0,0,{
		# 			'name' : line.name,
		# 			'branch_id': self.branch_id.id,
		# 			'analytic_account_id' : self.analytic_account_id.id,
		# 			'account_id' : self.account_id.id,
		# 			'amount' : line.amount,
		# 			'date' : se.date,
		# 			'is_linked_with_customization' : True,
		# 			'line_type' : self.line_type,
		# 			})]

		# 	if self.line_type == 'deduction':
		# 		self.customization_line_id.deduction_ids = [(0,0,{
		# 			'name' : line.name,
		# 			'branch_id': self.branch_id.id,
		# 			'analytic_account_id' : self.analytic_account_id.id,
		# 			'account_id' : self.account_id.id,
		# 			'amount' : line.amount,
		# 			'date' : self.date,
		# 			'is_linked_with_customization' : True,
		# 			'line_type' : line.line_type,
		# 			})]
		self.customization_state = 'confirmed'


				
	@api.multi
	@api.onchange('no_of_installments','start_date','payment_term')
	def onchange_installment(self):
		if self.no_of_installments and self.start_date and self.payment_term:

			# self.no_of_installment_ids = [(5)]
			for record in self.no_of_installment_ids:
				record.payment_line_id = False
				record.is_installment = False

			for line in self.no_of_installment_ids:
				line.is_installment = False

			self.no_of_installment_ids = False
			ids_list = []
			for i in range(0,self.no_of_installments  ):
				self.no_of_installment_ids = [(0,0,{
					'name' : self.name,
					'branch_id': self.branch_id.id,
					'analytic_account_id' : self.analytic_account_id.id,
					'account_id' : self.account_id.id,
					'amount' : self.amount / self.no_of_installments,
					'date' : self.start_date + relativedelta(months=+ (i * int(self.payment_term))  ) ,
					'is_linked_with_customization' : True,
					'line_type' : self.line_type,
					'the_payment_branch_id' : self.the_payment_branch_id.id,
					'ratification_type' : self.ratification_type,
					'is_installment' : True,
					'customization_branch_id' : self.branch_id.id,
					'the_line_id': self.id,
					'the_line_number' : self.id,
					})]

			for line in self.no_of_installment_ids:
				line.name = self.name,
				line.branch_id = self.branch_id.id
				line.analytic_account_id = self.analytic_account_id.id
				line.account_id = self.account_id.id
				line.date = line.date
				line.is_linked_with_customization = True
				line.line_type = self.line_type
				line.the_payment_branch_id = self.the_payment_branch_id.id
				line.ratification_type =  self.ratification_type
				line.is_installment = True
				line.customization_branch_id = self.branch_id.id
				the_line_id = self.id
				the_line_number = self.id


	@api.multi
	def action_open_installments(self):
		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'payment.ratification.line',
			'res_id' : self.id,

		}


class PaymentLineInstallments(models.Model):
	_name = 'payment.ratification.line.installment'
	_order = 'id desc'

	date = fields.Date()
	amount = fields.Float()
	payment_line_id = fields.Many2one('payment.ratification.line')

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	

class Collection(models.Model):
	_inherit = 'collection.collection.line'

	customization_collection_line_id = fields.Many2one('collection.collection')

	is_reserved = fields.Boolean(string='Reserve')
	reserved_amount = fields.Float(string='The Reserved Amount')
	remaining_amount = fields.Float(compute='compute_remaining_amount')

	@api.multi
	@api.depends('is_reserved', 'reserved_amount')
	def compute_remaining_amount(self):
		for record in self:
			record.remaining_amount = record.amount - record.reserved_amount

	@api.multi
	@api.onchange('is_reserved')
	def onchange_is_reserved(self):
		if self.is_reserved:
			self.reserved_amount = self.amount
		else:
			self.reserved_amount = 0





	@api.multi
	def action_open_customization(self):
		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'collection.collection',
			'res_id' : self.customization_collection_line_id.id,

		}