from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError
from . import amount_to_text as amount_to_text_ar

class ClaimsComplex(models.Model):
	_name = 'claim.complex'
	_description = 'Claim Complex'
	_order = 'id desc'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']
	_rec_name = 'company_id'

	company_id = fields.Many2one('res.company', string='Branch',default= lambda self:self.env.user.company_id.id,track_visibility='always')
	date = fields.Date(default=lambda self: fields.Date.today())
	year = fields.Char(track_visibility='always')
	month = fields.Selection([('January','January'),('February', 'February'),('March', 'March'),('April', 'April'),('May', 'May'),('June', 'June'),('July', 'July'),('August', 'August'),('September', 'September'),('October', 'October'),('November', 'November'),('December', 'December')], default='January',track_visibility='always')
	state = fields.Selection([('draft','Draft'),('Auditors Audited','Auditors Audited'),('Internal Auditor Audited', 'Internal Auditor Audited'),('General Manager Approved', 'General Manager Approved'),('Transfered to Director of Financial and Administrative Affairs', 'Transfered to Director of Financial and Administrative Affairs'),('Transfered to Director of Financial Affairs', 'Transfered to Director of Financial  Affairs'), ('Transfered to Ratifications Department', 'Transfered to Ratifications Department') ], default='draft',track_visibility='always')

	amount = fields.Float(compute='compute_amount', track_visibility='always')
	amount_in_words = fields.Char(compute='get_total_in_words' ,track_visibility='always')


	claim_ids = fields.One2many('claim.claim', 'complex_id')

	line_ids = fields.One2many('claim.complex.line', 'complex_id')

	ratification_list_ids = fields.One2many('ratification.list','complex_id')



	payable_account_id = fields.Many2one(
	'account.account', string='Payable Account', domain=[('is_service_center_account', '=', True)],default=lambda self: self.env['account.account'].search([('is_service_center_account', '=', True)], limit=1))

	journal_id = fields.Many2one('account.journal',string='Journal')

	@api.onchange('payable_account_id')
	def _onchange_payable_account_id(self):
		if self.payable_account_id:
			journals = self.env['account.journal'].search([
				'|',
				('default_debit_account_id', '=', self.payable_account_id.id),
				('default_credit_account_id', '=', self.payable_account_id.id),
			], limit=1)
			
			return {
				'domain': {
					'journal_id': [
						'|',
						('default_debit_account_id', '=', self.payable_account_id.id),
						('default_credit_account_id', '=', self.payable_account_id.id),
					]
				},
				'value': {
					'journal_id': journals.id if journals else False
				}
			}
		else:
			return {
				'domain': {'journal_id': []},
				'value': {'journal_id': False}
			}

	

	

	

	
	


		

	# domain=lambda self:self._domain_account())

	# def _domain_account(self):
	# 	request = self.env['account.journal'].search([('default_debit_account_id', '=', self.payable_account_id.id)])
	# 	return [('id','in',[v.id for v in request])]


	

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	
	@api.multi
	def show_move(self):

		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'tree,form',
			'res_model' : 'account.move',
			'domain' : [('complex_id','=', self.id  )],
		}




	@api.multi
	def show_ratification_list(self):

		for ratification_list in self.env['ratification.list'].search([('complex_id','=',self.id)]):
			return {
				'type' : 'ir.actions.act_window',
				'view_mode' : 'form',
				'res_model' : 'ratification.list',
				'res_id' : ratification_list.id,
				'context':{'default_complex_id' : self.id, 'default_name' :  str( _('Claims of Month ') + str(_(self.month)) + _(' of Year ') + str(self.year) ) ,'default_date':self.date},
				'domain' : [('complex_id','=', self.id  )],
			}

		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'ratification.list',
			'context':{'default_complex_id' : self.id, 'default_name' :  str( _('Claims of Month ') + str(_(self.month)) + _(' of Year ') + str(self.year) ),'default_date':self.date},
			'domain' : [('complex_id','=', self.id  )],
		}





	@api.multi
	@api.onchange('month','year')
	def onchange_month_year(self):
		for record in self:
			for claim in self.env['claim.claim'].search([('complex_id','=',False),('year','=',record.year),('month','=',record.month),('branch_id','=',record.company_id.id)]):
				# pass
				claim.complex_id = record.id
				print(claim.complex_id)

			record.line_ids = False
			lines = []

			for claim in record.claim_ids:
				for line in claim.ratification_line_ids:

					found = False
					for list_line in lines:

						if list_line['subscriber_company_id'] == line.branch_id.id and list_line['account_id'] == line.account_id.id :
							list_line['amount'] = list_line['amount'] + line.amount
							found = True
					if not found:
						lines.append({
							'partner_id' : claim.partner_id.id,
							'company_id' : claim.branch_id.id,
							'subscriber_company_id' : line.branch_id.id,
							'account_id' : line.account_id.id,
							'budget_item_id' : line.analytic_account_id.id,
							'amount' : line.amount,
							})

			for line in lines:
				record.line_ids = [(0,0,line)]

			for line in record.line_ids:
				if line.subscriber_company_id != record.company_id:
					for company_line in self.env['branch.account.line'].search([('company_id','=',line.subscriber_company_id.id)]):
						line.account_id = company_line.account_id.id
						line.budget_item_id = False

			firest_list = []
			for line in record.line_ids:
				firest_list.append({
					'partner_id' : line.partner_id.id,
					'subscriber_company_id' : line.subscriber_company_id.id,
					'account_id' : line.account_id.id,
					'budget_item_id' : line.budget_item_id.id,
					'amount' : line.amount,
					})

			second_list = []
			for fst_line in firest_list:
				found = False
				for sec_line in second_list:
					if sec_line['subscriber_company_id'] == fst_line['subscriber_company_id'] and sec_line['account_id'] == fst_line['account_id']:
						sec_line['amount'] = sec_line['amount'] + fst_line['amount']
						found = True

				if not found:
					second_list.append({
						'partner_id' : fst_line['partner_id'],
						'subscriber_company_id' : fst_line['subscriber_company_id'],
						'account_id' : fst_line['account_id'],
						'budget_item_id' : fst_line['budget_item_id'],
						'amount' : fst_line['amount'],
						})

			record.line_ids = False
			for line in second_list:
				record.line_ids = [(0,0,line)]


	@api.multi
	def compute_amount(self):
		for record in self:
			total = 0
			for line in record.line_ids:
				total = total + line.amount
			record.amount = total


	@api.multi
	def get_total_in_words(self):
		for record in self:
			record.amount_in_words = amount_to_text_ar.amount_to_text( record.amount )



	@api.multi
	def do_auditors_audit(self):
		for claim in self.claim_ids:
			claim.state = 'Auditors Audited'
		self.state = 'Auditors Audited'


	@api.multi
	def do_return_to_auditors(self):
		for claim in self.claim_ids:
			claim.state = 'draft'
		self.state = 'draft'

	@api.multi
	def do_return_to_internal_auditor(self):
		for claim in self.claim_ids:
			claim.state = 'Auditors Audited'
		self.state = 'Auditors Audited'


	@api.multi
	def do_internal_audit(self):
		for claim in self.claim_ids:
			claim.state = 'Internal Auditor Audited'
		self.state = 'Internal Auditor Audited'


	@api.multi
	def do_gm_approval(self):
		for claim in self.claim_ids:
			claim.state = 'Transfered to Director of Financial and Administrative Affairs'
		self.state = 'Transfered to Director of Financial and Administrative Affairs'


	@api.multi
	def do_return_to_general_manager(self):
		for claim in self.claim_ids:
			claim.state = 'Internal Auditor Audited'
		self.state = 'Internal Auditor Audited'

	@api.multi
	def do_transfer_to_finance_admin(self):
		for claim in self.claim_ids:
			claim.state = 'Transfered to Director of Financial and Administrative Affairs'
		self.state = 'Transfered to Director of Financial and Administrative Affairs'

	@api.multi
	def do_return_to_finance_admin(self):
		for claim in self.claim_ids:
			claim.state = 'Transfered to Director of Financial and Administrative Affairs'
		self.state = 'Transfered to Director of Financial and Administrative Affairs'




	@api.multi
	def do_return_to_finance_and_admin(self):
		for claim in self.claim_ids:
			claim.state = 'Transfered to Director of Financial and Administrative Affairs'
		self.state = 'Transfered to Director of Financial and Administrative Affairs'

	

	@api.multi
	def do_transfer_to_finance(self):

		for claim in self.claim_ids:
			claim.state = 'Transfered to Director of Financial Affairs'
		self.state = 'Transfered to Director of Financial Affairs'


	@api.multi
	def do_transfer_to_ratifications(self):

		total = 0
		lines = []

		# for line in self.line_ids:
		# 	if line.amount > 0:
		# 		total = total + line.amount

		# lines.append( (0,0,{
		# 	'account_id' : self.payable_account_id.id,
		# 	'credit' : total,
		# 	'debit': 0,
		# 	'date' : self.date,
		# 	'complex_id' : self.id,
		# 	}) )

		for claim in self.claim_ids:
			for line in claim.ratification_line_ids:

				analytic_account_id = line.analytic_account_id.id
				account_id = line.account_id.id

				print('\n\n\n')
				print('########### analytic_account_id = ',analytic_account_id)
				print('########### account_id = ', account_id)

				if line.branch_id.id != claim.branch_id.id:
					for company_line in self.env['branch.account.line'].search([('company_id','=',line.branch_id.id)]):
						account_id = company_line.account_id.id
						analytic_account_id = False

						print('########### INNN  EQUAAAALS')
						print('########### analytic_account_id = ',analytic_account_id)
						print('########### account_id = ', company_line.account_id.id)





					print('$$$$$$$$$$$$  EQUAAAALS ')

				print('Aftttter')

				print('########### analytic_account_id = ',analytic_account_id)
				print('########### account_id = ', account_id)

				print('\n\n\n')
				for amoun in line.deduction_ids:
					print('///////////       ' + str(amoun.amount) + ' //////////////////////////')
				print('\n\n\n')

				lines.append((0, 0, {
					'account_id': self.payable_account_id.id,
					'credit': line.amount,
					'debit': 0,
					'date': self.date,
					'partner_id': claim.partner_id.id,
					}))

				lines.append((0, 0, {
					'account_id': account_id,
					'analytic_account_id': analytic_account_id,
					'debit': line.amount,
					'credit': 0,
					'date': self.date,
					'partner_id': claim.partner_id.id,
				}))


		# for line in self.line_ids:
		# 	if line.amount > 0:
		# 		analytic_account_id = False
		# 		if line.budget_item_id:
		# 			analytic_account_id = line.budget_item_id.id


		# 		lines.append( (0,0,{
		# 			'account_id' : self.payable_account_id.id,
		# 			'credit' : line.amount,
		# 			'debit': 0,
		# 			'date' : self.date,
		# 			'complex_id' : self.id,
		# 			'partner_id' : line.partner_id.id,
		# 			}) )

		# 		lines.append( (0,0,{
		# 			'account_id' : line.account_id.id,
		# 			'analytic_account_id': analytic_account_id,
		# 			'debit': line.amount,
		# 			'credit' : 0,
		# 			'date' : self.date,
		# 			'partner_id' : line.partner_id.id,
		# 		}) )

		move_id = self.env['account.move'].create({
			'complex_id' : self.id,
			'journal_id' : self.journal_id.id,
			'date' : self.date,
			'ref' : _( 'مطالبة  ' +  _(self.month) + '   /  ' + _( self.year ) ),

			'line_ids' : lines,
			})

		move_id.post()

		for claim in self.claim_ids:
			claim.state = 'Transfered to Ratifications Department'
		self.state = 'Transfered to Ratifications Department'





class ClaimsComplexLine(models.Model):
	_name = 'claim.complex.line'

	company_id = fields.Many2one('res.company', string='Branch')
	partner_id = fields.Many2one('res.partner')
	subscriber_company_id = fields.Many2one('res.company', string='Subscriber Branch')
	account_id = fields.Many2one('account.account', string='Account')
	budget_item_id = fields.Many2one('account.analytic.account', string='Budget Item')
	amount = fields.Float()

	complex_id = fields.Many2one('claim.complex', ondelete='cascade')
	
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	

class Claim(models.Model):
	_inherit = 'claim.claim'

	complex_id = fields.Many2one('claim.complex')

class RatificationList(models.Model):
	_inherit = 'ratification.list'

	complex_id = fields.Many2one('claim.complex')

	@api.multi
	@api.onchange('complex_id')
	def onchange_complex(self):
		
		if self.complex_id:
			for claim in self.complex_id.claim_ids:

				for line in claim.ratification_line_ids:

					account_id = line.account_id.id
					analytic_account_id = line.analytic_account_id.id 
					account_code = line.account_id.code 

					if self.complex_id.company_id.id != line.branch_id.id:
						analytic_account_id = False
						for company_line in self.env['branch.account.line'].search([('company_id','=',line.branch_id.id)]):
							account_id = company_line.account_id.id

					if line.amount > 0:

						the_type = 'accounts_payable'
						ratification_type = 'accounts_payable'
						accounts_payable_types = 'service_provider_claim'
						if self.complex_id.company_id.id == line.branch_id.id:
							the_type = 'budget'
							ratification_type = 'expenses'
							accounts_payable_types = False
						total_deduction_amount = 0.0

						for i in line.deduction_ids:
							total_deduction_amount += i.amount

						self.ratification_line_ids = [(0,0,{
							'partner_id' : claim.partner_id.id,
							'the_type' : the_type,
							'ratification_type' : ratification_type,
							'accounts_payable_types' : accounts_payable_types,
							'account_id' : account_id,
							'amount' : line.amount,
							'branch_id' : line.branch_id.id,
							'analytic_account_id' : analytic_account_id,
							'name' : line.name,
							'deduction_ids': [(0,0,{
								'tax_id': i.tax_id,
								'name': i.name,
								'amount': i.amount,
							})for i in line.deduction_ids],
							'account_code' : account_code,
							})]
			self.name  = self.the_name = _('claims of ' + self.complex_id.month + ' / ' + _(self.complex_id.year) )


class AccountMove(models.Model):
	_inherit = 'account.move'

	complex_id = fields.Many2one('claim.complex')
