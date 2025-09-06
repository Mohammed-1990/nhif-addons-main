from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError
from . import amount_to_text as amount_to_text_ar

from dateutil.relativedelta import relativedelta


class CustomizationResult(models.Model):

	_name = 'kamil.customization.result'
	_rec_name = 'branch_id'

	branch_id = fields.Many2one('res.company')
	year = fields.Char()
	month = fields.Char()
	operation_date = fields.Date()

	customization_amount = fields.Float(compute='get_amounts')
	clearance_amount = fields.Float(compute='get_amounts')
	transfered_amount = fields.Float(compute='get_amounts')


	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('journal_moves_created','Journal Moves Created')], default='draft')

	customization_line_ids = fields.One2many('customization.result.customization','line_id')
	income_line_ids = fields.One2many('customization.result.income','line_id')
	deduction_line_ids = fields.One2many('customization.result.deduction','line_id')

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	

	@api.multi
	@api.onchange('customization_line_ids','income_line_ids','deduction_line_ids')
	def get_amounts(self):
		for record in self:
			customization_amount = 0
			income_amount = 0
			deduction_amount = 0

			for line in record.customization_line_ids:
				customization_amount = customization_amount + line.amount

			for line in record.income_line_ids:
				income_amount = income_amount + line.amount
			
			for line in record.deduction_line_ids:
				deduction_amount = deduction_amount + line.amount

			record.customization_amount = customization_amount
			record.clearance_amount =  abs( income_amount - deduction_amount)
			record.transfered_amount = customization_amount + (income_amount - deduction_amount)




class CustomizationResultCustomization(models.Model):

	_name = 'customization.result.customization'

	the_type = fields.Selection([('customization','customization'),('deduction','deduction'),('income','income')])
	branch_id = fields.Many2one('res.company')
	name = fields.Char(string='Description')
	account_id = fields.Many2one('account.account')
	analytic_account_id = fields.Many2one('account.analytic.account')
	amount = fields.Float()
	reserved_amount = fields.Float()
	remaining_amount = fields.Float()

	line_id = fields.Many2one('kamil.customization.result')

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	


class CustomizationResultIncome(models.Model):

	_name = 'customization.result.income'

	the_type = fields.Selection([('customization','customization'),('deduction','deduction'),('income','income')])
	branch_id = fields.Many2one('res.company')
	name = fields.Char(string='Description')
	account_id = fields.Many2one('account.account')
	analytic_account_id = fields.Many2one('account.analytic.account')
	amount = fields.Float()
	reserved_amount = fields.Float()
	remaining_amount = fields.Float()

	line_id = fields.Many2one('kamil.customization.result')

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	



class CustomizationResultDeduction(models.Model):

	_name = 'customization.result.deduction'

	the_type = fields.Selection([('customization','customization'),('deduction','deduction'),('income','income')])
	branch_id = fields.Many2one('res.company')
	name = fields.Char(string='Description')
	account_id = fields.Many2one('account.account')
	analytic_account_id = fields.Many2one('account.analytic.account')
	amount = fields.Float()
	reserved_amount = fields.Float(string='The Reserved Amount')
	remaining_amount = fields.Float()

	line_id = fields.Many2one('kamil.customization.result')
	
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	
