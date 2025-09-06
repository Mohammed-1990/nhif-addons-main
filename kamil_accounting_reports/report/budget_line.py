from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError
from datetime import date



class BudgetLine(models.Model):
	_inherit = 'crossovered.budget.lines'


	remaining_value = fields.Float(string='Remaining Amount' , compute='compute_remaining_value', store=True)
	planned_amount = fields.Float(compute='compute_values',store=True)
	analytic_account_id = fields.Many2one('account.analytic.account', realted='general_budget_id.analytic_account_id',store=True)
	practical_amount = fields.Float(compute='compute_values',store=True)