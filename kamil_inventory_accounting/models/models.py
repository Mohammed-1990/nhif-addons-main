from odoo import models, fields, api, _
from datetime import datetime
from lxml import etree
from odoo.exceptions import UserError, ValidationError



class stockPicking(models.Model):
	_inherit = 'stock.picking'

	# def _calculate_incoming_account_moves(self):
	# 	entry_lines = []
	# 	debit_amount = 0.0
	# 	credit_amount = 0.0
		
	# 	for move in self.move_ids_without_package:
	# 		# Get debit and credit accounts, throw validation error if not found
	# 		debit_account = self.location_dest_id.account_id or False
	# 		if not debit_account:
	# 			raise ValidationError(_("Please define an a stock account on location: %s") % self.location_dest_id.name)
			
	# 		credit_account = move.product_id.property_account_expense_id or move.product_id.categ_id.property_account_expense_categ_id or False
	# 		if not credit_account:
	# 			raise ValidationError(_("Please define an expense account for item: %s, or category: %s") % (move.product_id.name, move.product_id.categ_id.name))
			
	# 		# if transfer created from PO
	# 		if self.purchase_id:
	# 			for line in self.purchase_id.order_line:
	# 				if move.product_id == line.product_id:
	# 					debit_amount = credit_amount = line.price_subtotal or 0.0		
	# 		# if transfer created directly
	# 		else:
	# 			debit_amount = credit_amount = (move.product_id.standard_price*move.quantity_done) or 0.0

	# 		credit_entry_line = {
	# 			'account_id': credit_account.id,
	# 			'name': 'Incoming stock of '+move.product_id.name,
	# 			'debit': 0.0,
	# 			'credit': credit_amount,
	# 			'company_id': self.company_id.id,
	# 			'company_currency_id': self.company_id.currency_id.id,
	# 			}
	# 		entry_lines.append((0,0,credit_entry_line))
	# 		debit_entry_line = {
	# 			'account_id': debit_account.id,
	# 			'name': 'Incoming stock of '+move.product_id.name,
	# 			'debit': debit_amount,
	# 			'credit': 0.0,
	# 			'company_id': self.company_id.id,
	# 			'company_currency_id': self.company_id.currency_id.id,
	# 			}
	# 		entry_lines.append((0,0,debit_entry_line))
	# 	return entry_lines


	# def _calculate_internal_account_moves(self):

	# 	entry_lines = []
	# 	debit_amount = 0.0
	# 	credit_amount = 0.0
	# 	for move in self.move_ids_without_package:
	# 		# Get debit and credit accounts, throw validation error if not found
	# 		credit_account = self.location_id.account_id or False
	# 		if not credit_account:
	# 			raise ValidationError(_("Please define a stock account on location: %s") % self.location_id.name)
	# 		debit_account = self.branch_location.with_context(force_company=self.branch_id.id).account_id or False
	# 		if not debit_account:
	# 			raise ValidationError(_("Please define a stock account on location: %s") % self.branch_location.name)
			
	# 		debit_amount = credit_amount = (move.product_id.standard_price*move.quantity_done) or 0.0
	# 		credit_entry_line = {
	# 			'account_id': credit_account.id,
	# 			'name': 'Branch Transfer stock of '+move.product_id.name,
	# 			'debit': 0.0,
	# 			'credit': credit_amount,
	# 			'company_id': self.company_id.id,
	# 			'company_currency_id': self.company_id.currency_id.id,
	# 			}
	# 		entry_lines.append((0,0,credit_entry_line))
	# 		debit_entry_line = {
	# 			'account_id': debit_account.id,
	# 			'name': 'Branch Transfer stock of '+move.product_id.name,
	# 			'debit': debit_amount,
	# 			'credit': 0.0,
	# 			'company_id': self.company_id.id,
	# 			'company_currency_id': self.company_id.currency_id.id,
	# 			}
	# 		entry_lines.append((0,0,debit_entry_line))
	# 	return entry_lines

	# def _calculate_outgoing_account_moves(self):
	# 	entry_lines = []
	# 	debit_amount = 0.0
	# 	credit_amount = 0.0
	# 	for move in self.move_ids_without_package:
	# 		# # Get debit and credit accounts, throw validation error if not found
	# 		credit_account = self.location_id.account_id or False
	# 		if not credit_account:
	# 			raise ValidationError(_("Please define an a stock account on location: %s") % self.location_id.name)
			
	# 		debit_account = move.product_id.property_account_expense_id or move.product_id.categ_id.property_account_expense_categ_id or False
	# 		if not debit_account:
	# 			raise ValidationError(_("Please define an expense account for item: %s, or category: %s") % (move.product_id.name, move.product_id.categ_id.name))
			
	# 		debit_amount = credit_amount = (move.product_id.standard_price*move.quantity_done) or 0.0
	# 		credit_entry_line = {
	# 			'account_id': credit_account.id,
	# 			'name': 'Outgoing stock of '+move.product_id.name,
	# 			'debit': 0.0,
	# 			'credit': credit_amount,
	# 			'company_id': self.company_id.id,
	# 			'company_currency_id': self.company_id.currency_id.id,
	# 			}
	# 		entry_lines.append((0,0,credit_entry_line))
	# 		debit_entry_line = {
	# 			'account_id': debit_account.id,
	# 			'name': 'Outgoing stock of '+move.product_id.name,
	# 			'debit': debit_amount,
	# 			'credit': 0.0,
	# 			'company_id': self.company_id.id,
	# 			'company_currency_id': self.company_id.currency_id.id,
	# 			}
	# 		entry_lines.append((0,0,debit_entry_line))
	# 		budget_item_id = move.product_id.categ_id.property_account_expense_categ_id.parent_budget_item_id.id or False
	# 		if not budget_item_id:
	# 			raise ValidationError(_('Please define a budget item account on product: %s, or its category: %s.')%(move.product_id.name, move.product_id.categ_id.name))
	# 		analytic_vals = {
	# 		'name':'Outgoing stock of '+move.product_id.name,
	# 		'account_id':budget_item_id,
	# 		'amount':debit_amount or credit_amount or 0.0,
	# 		'unit_amount':move.quantity_done,
	# 		'product_id':move.product_id.id,
	# 		}
	# 		analytic_item = self.env['account.analytic.line'].create(analytic_vals)
	# 	return entry_lines

	# @api.multi
	# def button_validate(self):
	# 	res = super(stockPicking, self).button_validate()

	# 	stock_loaction_account_id = self.location_id.account_id 
	# 	if not stock_loaction_account_id: 
	# 		raise ValidationError(_('عليك تحديد حساب المخزن اولاً')) 

	# 	for move in self.env['account.move'].search([('stock_move_id','=',self.id)]):
	# 		if self.picking_type_id.code == 'incoming':
	# 			move.button_cancel()
	# 			move.unlink()
	# 			continue;
	# 		if self.picking_type_id.code == 'outgoing':
	# 			move.button_cancel()
	# 			for move_line in move.line_ids:
	# 				if move_line.credit > 0:
	# 					move_line.account_id = stock_loaction_account_id.id
		


		# lines = []
		# vals = {}
		
		# if self.picking_type_id.code == 'internal' and self.internal_transfer_type == 'branch':
		# 	journal_id = self.env['account.journal']
		# 	lines = self._calculate_internal_account_moves()
		# 	vals = {
		# 		'ref':'Branch Transfer of Stock /%s' % str(fields.date.today()),
		# 		'line_ids':lines,
		# 	}

		# 	for move in self.move_ids_without_package:
		# 		journal_id = move.product_id.categ_id.property_stock_journal
		# 		if not journal_id:
		# 			raise ValidationError(_("There's no accounting journal assgined to handle stock moves for product category ( %s ), please contact system administrator!") % move.product_id.categ_id.name)

		# 	vals.update({
		# 		'journal_id':journal_id.id,
		# 		'state':'draft',
		# 		})
		# 	account_move = self.env['account.move'].create(vals)
		return res
	