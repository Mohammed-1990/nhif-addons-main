# *.* coding:utf-8 *.*

from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class AccountAssetCategory(models.Model):
	_inherit = 'account.asset.category'

	code = fields.Char(string="Reference")
	account_evaluation_id = fields.Many2one('account.account','Evaluation Account')
	account_maintenance_id = fields.Many2one('account.account','Mainteneance Asset Account')
	account_grant_kind_id = fields.Many2one('account.account','Grant Kind Account')
	account_profit_id = fields.Many2one('account.account','Asset Scrap :Profit Account')
	account_loss_id = fields.Many2one('account.account','Asset Scrap :Lost Account')



	@api.model
	def create(self, vals):
		vals['code'] = self.env['ir.sequence'].next_by_code('account.asset.category')
		return super(AccountAssetCategory, self).create(vals)
		

class AccountAsset(models.Model):
	_inherit = 'account.asset.asset'
	_order = 'id desc'

	code = fields.Char(default='/')
	product_id = fields.Many2one('product.product', 'Product')
	name = fields.Char(required=True,)
	# related='product_id.name'
	admin_id = fields.Many2one('hr.department', string="Administration", default= lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id.parent_id)
	dept_id = fields.Many2one('hr.department', 'Department',default= lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id)
	count = fields.Integer(default=1)
	salvage = fields.Float(default=1)
	balance_1_1 = fields.Float('Balance 1/1')
	additions = fields.Float('Additions')
	exclusion = fields.Float('Exclusion')
	annual_dep_ratio = fields.Float('Annual Depreciation Ratio')
	annual_dep_value = fields.Float('Annual Depreciation value', compute='_compute_annual_dep_value')
	depreciation_year = fields.Float('Year Depreciation')
	dep_firt_period = fields.Float('Depreciation first Period')
	dep_last_period = fields.Float('Depreciation last Period')
	years_use = fields.Integer('Years of use', compute='_compute_year')
	amount_firt_period = fields.Float('Amount first Period')
	location_id = fields.Many2one('stock.location', 'Location', domain="[('usage','=','internal')]")
	inv_account_id = fields.Many2one('account.account','Inventory Account')
	inv_move_id = fields.Many2one('account.move', string='Inventory Journal Entry')
	inv_move_date = fields.Datetime('Date', default=datetime.now())
	depreciation_id = fields.Many2one('account.move', 'Asset Depreciation')
	depreciation_sum_value = fields.Float(compute='_compute_depreciation_value')
	depreciation_value = fields.Float(compute='_compute_depreciation_value')
	asset_evaluation = fields.Float('Asset Evaluation')
	state = fields.Selection(selection_add=[('freeze','Freeze'),('scrap','Scrap')])
	scrap_count = fields.Integer(compute='_compute_scrap_count')

	@api.multi
	def _compute_scrap_count(self):
		for asset in self:
			account = self.env['collection.collection'].search_count([('asset_id','=',self.id)])
			asset.scrap_count = account

	@api.multi
	def _compute_year(self):
		for rec in self:
			rec._onchange_year_number()


	@api.onchange('location_id')
	def _onchange_location_id(self):
		if self.location_id:
			self.inv_account_id = self.location_id.account_id.id


	@api.multi
	@api.depends('value','annual_dep_ratio')
	def _compute_annual_dep_value(self):
		for rec in self:
			if rec.value and rec.annual_dep_ratio:
				rec.annual_dep_value = rec.value * rec.annual_dep_ratio / 100
			# if rec.annual_dep_ratio and rec.value_residual:
			# 	rec.annual_dep_value = rec.value_residual / rec.method_number


	@api.onchange('first_depreciation_manual_date')
	def _onchange_year_number(self):
		date = datetime.today()
		self.years_use = relativedelta(date, self.first_depreciation_manual_date).years


	@api.multi
	@api.depends('depreciation_line_ids.move_id')
	def _entry_count(self):
		for asset in self:
			res = self.env['account.asset.depreciation.line'].search_count([('asset_id', '=', asset.id), ('move_id', '!=', False)])
			account = self.env['account.move'].search_count([('asset_id', '=', self.id)])
			asset.entry_count = res or 0
			asset.entry_count += account


	@api.multi
	def _compute_depreciation_value(self):
		for rec in self:
			rec.depreciation_sum_value = rec.value - rec.salvage_value
			rec.depreciation_value = rec.depreciation_sum_value / rec.method_number


	@api.model
	def create(self, vals):
		res = super(AccountAsset, self).create(vals)
		number = self.env['ir.sequence'].next_by_code('account.asset')
		res['code'] =  res['category_id'].code + '/' + number
		if res['annual_dep_ratio']:
			res['method_number'] = 100 / int(res['annual_dep_ratio'])
		return res


	@api.model
	def default_get(self, default_fields):
		res = super(AccountAsset, self).default_get(default_fields)
		res['method_period'] = 12
		return res


	@api.onchange('annual_dep_ratio')
	def onchange_annual_dep_ratio(self):
		if self.annual_dep_ratio:
			self.method_number = 100 / int(self.annual_dep_ratio)


	@api.multi
	def add_asset(self):
		created_moves = self.env['account.move']
		for line in self:
			if line.location_id:
				if line.value and line.salvage_value:
					amount = line.value - line.salvage_value
					move_vals = self._prepare_move(line, from_account=line.inv_account_id,to_account=line.category_id.account_asset_id,amount_line=amount)
					account = self.env['account.move'].create(move_vals)
					account.write({'asset_id':self.id,'ref':account.ref + ' - Add Asset'})
				else:
					raise UserError(_('The salvage value is not exsist!!!'))
			else:
				raise UserError(_('The Location is not exsist!!!'))


	@api.multi
	def evaluation_asset(self,value, account):
		created_moves = self.env['account.move']
		for line in self:
			if line.location_id:
				if line.value and line.salvage_value:
					move_vals = self._prepare_move(line, from_account=account,to_account=line.category_id.account_asset_id,amount_line=value)
					account = self.env['account.move'].create(move_vals)
					account.write({'asset_id':self.id,'ref':account.ref + ' - Evaluation Asset'})
					self.write({'value_residual':line.asset_evaluation})
				else:
					raise UserError(_('The salvage value is not exsist!!!'))
			else:
				raise UserError(_('The Location is not exsist!!!'))

	@api.multi
	def asset_depreciation(self):
		self.write({'state':'open'})

	@api.multi
	def action_donation(self):
		created_moves = self.env['account.move']
		for line in self:
			if line.location_id:
				if line.value and line.salvage_value:
					move_vals = self._prepare_move(line, from_account=line.category_id.account_asset_id,to_account=line.category_id.account_grant_kind_id,amount_line=line.value_residual)
					account = self.env['account.move'].create(move_vals)
					account.write({'asset_id':self.id,'ref':account.ref + ' - Donation Asset'})
				else:
					raise UserError(_('The salvage value is not exsist!!!'))
			else:
				raise UserError(_('The Location is not exsist!!!'))
			self.write({'state':'scrap'})


	@api.multi
	def action_loss(self):
		created_moves = self.env['account.move']
		for line in self:
			if line.location_id:
				if line.value and line.salvage_value:
					move_vals = self._prepare_move(line, from_account=line.category_id.account_asset_id,to_account=line.category_id.account_loss_id,amount_line=line.value_residual)
					account = self.env['account.move'].create(move_vals)
					account.write({'asset_id':self.id,'ref':account.ref + ' - Scrap or loss Asset'})
				else:
					raise UserError(_('The salvage value is not exsist!!!'))
			else:
				raise UserError(_('The Location is not exsist!!!'))
		self.write({'state':'scrap'})



	@api.multi
	def asset_freez(self):
		created_moves = self.env['account.move']
		for line in self:
			if line.location_id:
				if line.value and line.salvage_value:
					amount = line.value - line.salvage_value
					move_vals = self._prepare_move(line, from_account=line.category_id.account_asset_id,to_account=line.inv_account_id,amount_line=amount)
					account = self.env['account.move'].create(move_vals)
					account.write({'asset_id':self.id,'ref':account.ref + ' - Freez Asset'})
				else:
					raise UserError(_('The salvage value is not exsist!!!'))
			else:
				raise UserError(_('The Location is not exsist!!!'))
		self.write({'state':'freeze'})
	

	@api.multi
	def reset_freez(self):
		self.write({'state':'draft'})

	def _prepare_move(self, line, from_account, to_account, amount_line):
		category_id = line.category_id
		account_analytic_id = line.account_analytic_id
		analytic_tag_ids = line.analytic_tag_ids
		date = fields.Date.context_today(self)
		company_currency = line.company_id.currency_id
		current_currency = line.currency_id
		prec = company_currency.decimal_places
		amount = current_currency._convert(
			amount_line, company_currency, line.company_id, date)
		asset_name = line.name 
		move_line_1 = {
			'name': asset_name,
			'account_id': from_account.id,
			'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
			'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
			'partner_id': line.partner_id.id,
			'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
			'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
			'currency_id': company_currency != current_currency and current_currency.id or False,
			'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
		}
		move_line_2 = {
			'name': asset_name,
			'account_id': to_account.id,
			'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
			'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
			'partner_id': line.partner_id.id,
			'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
			'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
			'currency_id': company_currency != current_currency and current_currency.id or False,
			'amount_currency': company_currency != current_currency and line.amount or 0.0,
		}
		move_vals = {
			'name':line.code,
			'ref': line.code,
			'date': date or False,
			'journal_id': category_id.journal_id.id,
			'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
		}
		return move_vals


	@api.multi
	def asset_scrap(self):
		for asset in self:
			self.write({'state':'scrap'})

		return {
			'name': _('Collection'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'collection.collection',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'context': {'default_asset_id':self.id, 'create':'0'},
		}


	@api.multi
	def open_entries(self):
		move_ids = []
		for asset in self:
			for depreciation_line in asset.depreciation_line_ids:
				if depreciation_line.move_id:
					move_ids.append(depreciation_line.move_id.id)
		return {
			'name': _('Journal Entries'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.move',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': ['|',('id', 'in', move_ids),('asset_id','=',self.id)],
		}


		
class ProductTemplate(models.Model):

	_inherit = 'product.template'
	
	is_asset = fields.Boolean('Is Asset')

class StockLocation(models.Model):
	_inherit = 'stock.location'

	account_id = fields.Many2one('account.account', 'Location Account')

class  AccountMove(models.Model):
	_inherit = 'account.move'

	asset_id = fields.Many2one('account.asset.asset','Asset')

class Collection(models.Model):
	_inherit = 'collection.collection'

	asset_id = fields.Many2one('account.asset.asset','asset')



		


