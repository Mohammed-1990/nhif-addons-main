from odoo import models,fields,api,_ 
import json


class Claim(models.Model):
	_inherit = 'claim.claim'

	integration_claim_id = fields.Char()

	@api.model
	def create_claim(self, param=False):

		if param:
			for claim in param:
				partner_id = False

				for partner in self.env['res.partner'].search([('medical_center_id','=', claim['medical_center_id'] )]):
					partner_id = partner.id 
				if not partner_id:
					partner = self.env['res.partner'].create({
						'name': claim['medical_center_name'],
						'medical_center_id' : claim['medical_center_id'],
						})
					partner_id = partner.id 

				branch_id = self.env['res.company'].search([('integration_number','=',claim['branch_id'])])[0].id
				# date = claim['date']
				year = claim['year']
				month = claim['month']
				claim_type = claim['claim_type']
				line_ids = []

				for line in claim['items']:

					account_id = False
					parent_budget_item_id = False
					for account in self.env['account.account'].search([('integration_number','=', int(line['item_id'])  )]):
						account_id = account.id
						if account.parent_budget_item_id:
							parent_budget_item_id = account.parent_budget_item_id.id

					line_ids.append( (0,0,{
						'the_type' : 'accounts_payable',
						'accounts_payable_types' : 'service_provider_claim',
						'account_id' : account_id,
						'analytic_account_id' : parent_budget_item_id,
						'amount' : line['amount'],
						'branch_id' : self.env['res.company'].search([('integration_number','=',line['branch_id'])])[0].id,
						'name' : line['name'],
						}) )


				self.env['claim.claim'].create({
					'partner_id' : partner_id,
					'branch_id': branch_id,
					'year' : year,
					'month': month,
					'claim_type' : claim_type,
					'ratification_line_ids' : line_ids,

					})

		return True



class IntegrationInfo(models.Model):
	_name = 'kamil.integration.info'


	name = fields.Char(string='Description')
	

	branch_ids = fields.One2many('res.company', 'integration_id')
	item_ids = fields.One2many('account.account', 'integration_id')

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	

	@api.multi
	def do_reset(self):

		for account in self.env['account.account'].search([]):
			account.integration_id = False
		for account in self.env['account.account'].search([('code','=ilike','22%'),('is_group','=','sub_account')]):
			account.integration_id = self.id

		for account in self.env['res.company'].search([]):
			account.integration_id = False
		for account in self.env['res.company'].search([]):
			account.integration_id = self.id



class Branch(models.Model):
	_inherit = 'res.company'

	integration_number = fields.Char()

	integration_id = fields.Many2one('kamil.integration.info')



class Account(models.Model):
	_inherit = 'account.account'

	integration_number = fields.Char()

	integration_id = fields.Many2one('kamil.integration.info')



class Parnter(models.Model):
	_inherit = 'res.partner'

	medical_center_id = fields.Char()
