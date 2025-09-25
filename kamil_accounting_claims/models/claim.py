from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError
from . import amount_to_text as amount_to_text_ar


class Claim(models.Model):
	_name = 'claim.claim'
	_description = 'Claim'
	_order = 'id desc'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']

	name = fields.Char(string='Number',track_visibility='always')
	partner_id = fields.Many2one('res.partner', string='The Partner',track_visibility='always')
	year = fields.Char(track_visibility='always')
	month = fields.Selection([('January','January'),('February', 'February'),('March', 'March'),('April', 'April'),('May', 'May'),('June', 'June'),('July', 'July'),('August', 'August'),('September', 'September'),('October', 'October'),('November', 'November'),('December', 'December')], default='January',track_visibility='always')

	amount_before_audit = fields.Integer(track_visibility='always')
	amount_after_audit = fields.Integer(track_visibility='always')
	branch_id = fields.Many2one('res.company', string='Branch', default= lambda self:self.env.user.company_id.id,track_visibility='always')
	claim_type = fields.Selection([('Claim','Claim'),('Contribution','Contribution'),('Recovery','Recovery')], default='Claim')
	date = fields.Date(default=lambda self: fields.Date.today(),track_visibility='always')
	total_amount = fields.Float(string='Amount', compute='get_total_amount',store=True ,track_visibility='always')
	total_amount_in_words = fields.Char(string='Amount in Words', compute='get_total_in_words',track_visibility='always')
	state = fields.Selection([('draft','Draft'),('Auditors Audited','Auditors Audited'),('Internal Auditor Audited', 'Internal Auditor Audited'),('General Manager Approved', 'General Manager Approved'),('Transfered to Director of Financial and Administrative Affairs', 'Transfered to Director of Financial and Administrative Affairs'),('Transfered to Director of Financial Affairs', 'Transfered to Director of Financial  Affairs'), ('Transfered to Ratifications Department', 'Transfered to Ratifications Department') ], default='draft',track_visibility='always')
	line_ids = fields.One2many('claim.line', 'claim_id', copy=True)
	ratification_line_ids = fields.One2many('ratification.line', 'claim_id', copy=True)
	attachment = fields.Binary( track_visibility="always")


	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	

	@api.multi
	def do_auditors_audit(self):
		self.state = 'Auditors Audited'

	@api.multi
	def do_internal_audit(self):
		self.state = 'Internal Auditor Audited'

	@api.multi
	def do_gm_approval(self):
		self.state = 'General Manager Approved'

	@api.multi
	def do_transfer_to_finance_admin(self):
		self.state = 'Transfered to Director of Financial and Administrative Affairs'

	@api.multi
	def do_transfer_to_finance(self):
		self.state = 'Transfered to Director of Financial Affairs'


	@api.multi
	def do_transfer_to_ratifications(self):
		self.state = 'Transfered to Ratifications Department'


	@api.model 
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('claim.sequence') or '/'
		created = super(Claim, self).create(vals)
		return created


	@api.multi
	@api.depends('total_amount')
	def get_total_in_words(self):
		for record in self:
			record.total_amount_in_words = amount_to_text_ar.amount_to_text( record.total_amount )


	@api.depends('ratification_line_ids')
	def get_total_amount(self):
		for record in self:
			total = 0
			for line in record.ratification_line_ids:
				total = total + line.amount
			record.total_amount = total



	@api.multi
	def show_ratifications(self):


		for ratification in self.env['ratification.ratification'].search([('claim_id','=',self.id)]):
			
			return {
				'type' : 'ir.actions.act_window',
				'view_mode' : 'form',
				'res_model' : 'ratification.ratification',
				'res_id' : ratification.id,
				'domain' : [('claim_id','=', self.id )],
				'context': {
					'default_partner_id': self.partner_id.id,
					'default_state_id': self.branch_id.id,
					'default_name' : str( _('Claim for ') +  self.partner_id.name + _('  for Month ') + str(self.month) + _(' of Year ') + str(self.year) ) ,
					'default_the_name' : str( _('Claim for ') +  self.partner_id.name + _('  for Month ') + str(self.month) + _(' of Year ') + str(self.year) ) ,
					'default_claim_id' : self.id,
				},
			}			


		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'ratification.ratification',
			'domain' : [('claim_id','=', self.id )],
			'context': {
				'default_partner_id': self.partner_id.id,
				'default_state_id': self.branch_id.id,
				'default_name' : str( _('Claim for ') +  self.partner_id.name + _('  for Month ') + str(self.month) + _(' of Year ') + str(self.year) ) ,
				'default_the_name' : str( _('Claim for ') +  self.partner_id.name + _('  for Month ') + str(self.month) + _(' of Year ') + str(self.year) ) ,
				'default_claim_id' : self.id,
			},
		}			



	@api.multi
	def show_claim_complex(self):

		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'form',
			'res_model' : 'claim.complex',
			'res_id' : self.complex_id.id,
		}			



class ClaimLine(models.Model):
	_name = 'claim.line'

	branch_id = fields.Many2one('res.company', string='Branch', default= lambda self:self.env.user.company_id.id)
	account_id = fields.Many2one('account.account', string='Account')
	budget_item_id = fields.Many2one('account.analytic.account', string='Budget Item')
	cost_center_id = fields.Many2one('kamil.account.cost.center',string='Cost Center')
	analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Analytic Tags')
	amount = fields.Float()
	subscriber_id = fields.Many2one('res.partner', string='Subscriber')
	claim_id = fields.Many2one('claim.claim')

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	



	# @api.multi
	# @api.onchange('account_id')
	# def onchange_account(self):
	# 	for record in self:
	# 		if record.account_id:
	# 			record.budget_item_id = record.account_id.parent_budget_item_id


	@api.multi
	def get_account_domain(self):
		account_ids = []
		for account in self.env['account.account'].search([('is_group','=','sub_account')]):
			if account.code[:1] in ['2','3','4']:
				account_ids.append( account.id )
		return [('id','in',account_ids)]

		# return {
		# 	'domain' : {
		# 		'id':[('id','in',account_ids)]
		# 	}
		# }


class Ratification(models.Model):
	_inherit = 'ratification.ratification'

	claim_id = fields.Many2one('claim.claim')


	@api.multi
	@api.onchange('claim_id')
	def onchange_claim_id(self):
		for record in self:

			if record.claim_id:
				record.line_ids = False
				record.tax_ids = False

				for line in record.claim_id.ratification_line_ids:
					line.ratification_id = record.id


			# if record.claim_id:
			# 	record.partner_id = record.claim_id.partner_id
			# 	record.line_ids = False
			# 	for claim_line in record.claim_id.line_ids:
			# 		record.line_ids = [(0,0,{
			# 			'name' : claim_line.subscriber_id.name,
			# 			'analytic_account_id' : claim_line.budget_item_id.id,
			# 			'account_id' : claim_line.account_id.id,
			# 			'cost_center_id' : claim_line.cost_center_id.id,
			# 			'amount' : claim_line.amount,
			# 			'analytic_tag_ids' : [(6,0, claim_line.analytic_tag_ids._ids )],
			# 			'ratification_type' : 'service_provider_claim',
			# 			'branch_id' : claim_line.branch_id.id,
			# 			})]


class RatificationLine(models.Model):
	_inherit = 'ratification.line'

	claim_id = fields.Many2one('claim.claim', copy=False)
