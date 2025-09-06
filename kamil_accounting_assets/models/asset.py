
from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta



class Account(models.Model):
	_inherit = 'account.account'

	is_asset_account = fields.Boolean()
	asset_category_id = fields.Many2one('account.asset.category', string='Asset Category')


class Asset(models.Model):
	_inherit = 'account.asset.asset'

	company_id = fields.Many2one('res.company',default= lambda self:self.env.user.company_id.id)

	last_revaluation_value = fields.Float()
	collection_id = fields.Many2one('collection.collection')

	state = fields.Selection([('draft','Draft'),('open','Open'),('sold','Sold'),('granted','Granted'),('lost','Lost or Damaged'),('freez','Freezed')], default='draft')

	operation_ids = fields.One2many('account.asset.operation','asset_id')

	# value_residual = fields.Float(compute='compute_residual_value', string='Current Value')

	@api.multi
	@api.depends('depreciation_line_ids')
	def compute_residual_value(self):
		for record in self:
			residual_amount = 0
			for line in record.depreciation_line_ids:
				if line.move_check == False:
					residual_amount = residual_amount + line.remaining_value
			record.value_residual = residual_amount 

	@api.multi
	def do_add_asset(self):
		self.validate()
		for line in self.depreciation_line_ids:
			if line.remaining_value == 0:
				line.amount = line.amount - 1
				line.depreciated_value = line.depreciated_value - 1
				line.remaining_value = line.remaining_value + 1
		self.validate()

		self.env['account.asset.operation'].create({
			'name' : self.product_id.name,
			'value' : self.value,
			'date' : self.date, 
			'type' : 'addition',
			'asset_id' : self.id,
			})

		# if self.inv_account_id:
		# 	move_id = self.create_move(
		# 		ref=_('Add Asset'), 
		# 		journal_id=self.category_id.journal_id.id, 
		# 		asset_id=self.id, 
		# 		date=self.first_depreciation_manual_date) 

		# 	self.create_move_line(
		# 		name=_('Add Asset'), 
		# 		move_id=move_id.id, 
		# 		account_id=self.inv_account_id.id,
		# 		credit=self.value)

		# 	self.create_move_line(
		# 		name=_('Add Asset'), 
		# 		move_id=move_id.id, 
		# 		account_id=self.category_id.account_asset_id.id,
		# 		debit=self.value)
		# 	self.validate()
		# 	move_id.post()

		# 	for line in self.depreciation_line_ids:
		# 		if line.remaining_value == 0:
		# 			line.amount = line.amount - 1
		# 			line.depreciated_value = line.depreciated_value - 1
		# 			line.remaining_value = line.remaining_value + 1
		# else:
		# 	raise ValidationError(_('Please Add Inventory Account !'))



	@api.multi
	def do_asset_revaluation(self):
		
		dep_value = 0
		for line in self.depreciation_line_ids:
			if line.move_check == False:
				dep_value = line.remaining_value + line.amount
				break

		return {
			'name': _('Asset Re-evaluation'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'account.asset.operation',
			'type': 'ir.actions.act_window',
			'target':'new',
			'context' : {'default_type':'revaluation', 'default_value':dep_value,'default_old_value' : dep_value, 'default_asset_id': self.id }
		}



	@api.multi
	def do_asset_dispose(self):
		
		current_value = 0
		for line in self.depreciation_line_ids:
			if line.move_check == False:
				current_value = line.remaining_value + line.amount
				break


		return {
			'name': _('Asset Dispose'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'account.asset.operation',
			'type': 'ir.actions.act_window',
			'target':'new',
			'context' : {'default_type':'dispose', 'default_value':current_value,'default_old_value':current_value, 'default_asset_id': self.id}
		}


	@api.multi
	def do_asset_freez(self):

		dep_value = 0
		for line in self.depreciation_line_ids:
			if line.move_check == False:
				dep_value = line.remaining_value + line.amount
				break

		return {
			'name': _('Asset Freez'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'account.asset.operation',
			'type': 'ir.actions.act_window',
			'target':'new',
			'context' : {'default_type':'freez', 'default_value':dep_value,'default_old_value':dep_value, 'default_asset_id': self.id}
		}




	@api.multi
	def do_asset_unfreez(self):

		dep_value = 0
		for line in self.depreciation_line_ids:
			if line.move_check == False:
				dep_value = line.remaining_value + line.amount
				break

		return {
			'name': _('Asset unFreez'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'account.asset.operation',
			'type': 'ir.actions.act_window',
			'target':'new',
			'context' : {'default_type':'unfreez', 'default_value':dep_value,'default_old_value':dep_value, 'default_asset_id': self.id}
		}



	def create_move(self, ref, journal_id,asset_id=False, date=False):
		move = self.env['account.move']
		vals = {
			'ref': ref,
			'journal_id': journal_id,
			'date' : date,
			'asset_id' : asset_id,
		}
		return move.create(vals)

	def create_move_line(self, partner_id=False, name=False, move_id=False, account_id=False, debit=False, credit=False, date=False, amount_currency=False, currency_id=False, analytic_account_id=False, analytic_tag_ids=False,cost_center_id=False):
		move_line = self.env['account.move.line']
		vals = {
			'partner_id': partner_id,
			'name': name,
			'move_id': move_id,
			'account_id': account_id,
			'debit': debit,
			'credit': credit,
			'date_maturity' : date,
			'amount_currency' : amount_currency,
			'currency_id' : currency_id,
			'analytic_account_id' : analytic_account_id, 
			'analytic_tag_ids': analytic_tag_ids,
			'cost_center_id': cost_center_id,
		}
		return move_line.with_context(check_move_validity=False).create(vals)



class AssetOperation(models.Model):
	_name = 'account.asset.operation'

	name = fields.Char()
	value = fields.Float()
	date = fields.Date(default=lambda self: fields.Date.today())
	type = fields.Selection([('addition','Addition'),('revaluation','Re-evaluation'),('dispose','Dispose'),('freez','Freez'),('unfreez','unFreez')])
	dispose_type = fields.Selection([('sale','Sale'),('give','Grant'),('lost','Lost or Damaged')], default='sale')
	old_value = fields.Float()
	asset_id = fields.Many2one('account.asset.asset', ondelete='cascade')
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	

	@api.multi
	def do_operation(self):
	
		if self.type == 'revaluation':
			for asset in self.env['account.asset.asset'].search([('id','in',self._context['active_ids'])]):
				if not asset.category_id.revaluation_account_id:
					raise ValidationError(_('Please Add Re-evaluation Account to the Category'))

				asset.last_revaluation_value = self.value

				remaining_dep_no = 0
				for line in asset.depreciation_line_ids:
					if not line.move_check:
						remaining_dep_no = remaining_dep_no + 1

				dep_value = self.value / remaining_dep_no
				asset_new_value = dep_value
				dep_total_value = self.value

				for line in asset.depreciation_line_ids:
					if not line.move_check:
						line.amount = dep_value
						line.depreciated_value = (asset_new_value)

						asset_new_value = asset_new_value + dep_value 

						line.remaining_value = abs(dep_total_value - dep_value)

						dep_total_value = abs(dep_total_value - dep_value)

				for line in asset.depreciation_line_ids:
					if line.remaining_value == 0 or line.remaining_value <= 1 :
						line.amount = abs(abs(line.amount) - 1)
						line.depreciated_value = abs(abs(line.depreciated_value) - 1)
						line.remaining_value = abs(line.remaining_value) + 1


				current_value = self.old_value
				new_value = self.value

				# for line in asset.depreciation_line_ids:				
				# 	if line.remaining_value == 0:
				# 		line.amount = line.amount - 1
				# 		line.depreciated_value = line.depreciated_value - 1
				# 		line.remaining_value = line.remaining_value + 1


				if self.value > current_value:
					move_id = self.create_move(
						ref=_('Asset Re-evaluation'),
						journal_id=asset.category_id.journal_id.id,
						asset_id=asset.id,
						date=self.date )


					self.create_move_line(
						name=_('Asset Re-evaluation'), 
						move_id=move_id.id, 
						account_id=asset.category_id.account_asset_id.id, 
						credit=False, 
						debit=(self.value - current_value) , 
						date=self.date )
					
					self.create_move_line(
						name=_('Asset Re-evaluation'), 
						move_id=move_id.id, 
						account_id=asset.category_id.revaluation_account_id.id, 
						debit=False, 
						credit=(self.value - current_value) , 
						date=self.date )
					move_id.post()


				if self.value < current_value:
					move_id = self.create_move(
						ref=_('Asset Re-evaluation'),
						journal_id=asset.category_id.journal_id.id,
						asset_id=asset.id,
						date=self.date )

					self.create_move_line(
						name=_('Asset Re-evaluation'), 
						move_id=move_id.id, 
						account_id=asset.category_id.account_asset_id.id, 
						debit=False, 
						credit=( current_value - self.value) , 
						date=self.date )
					
					self.create_move_line(
						name=_('Asset Re-evaluation'), 
						move_id=move_id.id, 
						account_id=asset.category_id.revaluation_account_id.id, 
						credit=False, 
						debit=(current_value - self.value) , 
						date=self.date )
					move_id.post()




				# dep_value = self.value * asset.annual_dep_ratio / 100

				# number_of_dep = int(100 / asset.annual_dep_ratio)

				# dep_accumulative_value = self.value				

				# print('######### number_of_dep= ', number_of_dep)
				# print('#########3 dep_value = ',dep_value)


				# for i in range( int(number_of_dep) ):
				# 	print('######## i = ',i)
				# 	asset.depreciation_line_ids = [(0,0,{
				# 		'amount' : dep_value,
				# 		'depreciated_value' : dep_accumulative_value,
				# 		'remaining_value' : 0,
				# 		'name' : '-',
				# 		'sequence' : i,
				# 		})]
				# 	dep_accumulative_value = dep_accumulative_value - dep_value

		if self.type == 'dispose':
			
			for asset in self.env['account.asset.asset'].search([('id','in',self._context['active_ids'])]):

				remaining_dep_no = 0
				for line in asset.depreciation_line_ids:
					if not line.move_check:
						remaining_dep_no = remaining_dep_no + 1

				dep_value = self.old_value / remaining_dep_no
				asset_new_value = dep_value
				dep_total_value = self.old_value

				for line in asset.depreciation_line_ids:
					if not line.move_check:
						line.amount = dep_value
						line.depreciated_value = (asset_new_value)

						asset_new_value = asset_new_value + dep_value 

						line.remaining_value = abs(dep_total_value - dep_value)

						dep_total_value = abs(dep_total_value - dep_value)

				for line in asset.depreciation_line_ids:
					if line.remaining_value == 0 or line.remaining_value <= 1 :
						line.amount = abs(abs(line.amount) - 1)
						line.depreciated_value = abs(abs(line.depreciated_value) - 1)
						line.remaining_value = abs(line.remaining_value) + 1

				if self.dispose_type == 'sale':			
					current_book_value = 0
					for line in asset.depreciation_line_ids:
						if line.move_check == False:
							current_book_value = line.remaining_value + line.amount
							break

					if self.value > self.old_value:
						if not asset.category_id.accusition_earning_account_id:
							raise ValidationError(_('Please Add Acqusition Earnings Account to the Category'))

						asset.collection_id = self.env['collection.collection'].create({
							'date' : self.date,
							'name' : _('Asset Sale'),
							'operation_type':'other_revenues',
							'line_ids' : [(0,0,{
								'account_id' : asset.category_id.account_asset_id.id,
								'amount' : self.old_value}),
								(0,0,{
									'account_id' : asset.category_id.accusition_earning_account_id.id,
								'amount' : self.value - self.old_value})]
								})
						asset.state = 'sold'

						return {
							'type' : 'ir.actions.act_window',
							'view_mode' : 'form',
							'res_model' : 'collection.collection',
							'res_id' : asset.collection_id.id,
						}

					if self.value == self.old_value:
						if not asset.category_id.accusition_earning_account_id:
							raise ValidationError(_('Please Add Acqusition Earnings Account to the Category'))

						asset.collection_id = self.env['collection.collection'].create({
							'date' : self.date,
							'name' : _('Asset Sale'),
							'operation_type' : 'other_revenues',
							'line_ids' : [(0,0,{
								'account_id' : asset.category_id.account_asset_id.id,
								'amount' : self.value})]
								})

						asset.state = 'sold'

						return {
							'type' : 'ir.actions.act_window',
							'view_mode' : 'form',
							'res_model' : 'collection.collection',
							'res_id' : asset.collection_id.id,
						}


					if self.value < self.old_value:
						if not asset.category_id.acqusition_lost_account_id:
							raise ValidationError(_('Please Add Acqusition Lost Account to the Category'))

						asset.collection_id = self.env['collection.collection'].create({
							'date' : self.date,
							'name' : _('Asset Sale'),
							'operation_type':'other_revenues',
							'line_ids' : [(0,0,{
								'account_id' : asset.category_id.account_asset_id.id,
								'amount' : self.value})]
								})



						move_id = self.create_move(
							ref=_('Asset Sale'),
							journal_id=asset.category_id.journal_id.id,
							asset_id=asset.id,
							date=self.date )

						move_id.collection_id=asset.collection_id.id

						move_id.line_ids = [
							(0,0,{
								'name' : ('Asset Sale'), 
								'account_id' : asset.category_id.account_asset_id.id, 
								'debit':False, 
								'credit':abs( self.old_value - self.value), 
								'date':self.date ,
							}),
							(0,0,{
								'name' : ('Asset Sale'), 
								'account_id' : asset.category_id.acqusition_lost_account_id.id, 
								'credit':False, 
								'debit':abs( self.old_value - self.value), 
								'date':self.date, 
								})]
						move_id.post()
						asset.state = 'sold'
						return {
							'type' : 'ir.actions.act_window',
							'view_mode' : 'form',
							'res_model' : 'collection.collection',
							'res_id' : asset.collection_id.id,
						}

					



				if self.dispose_type == 'give':
					print('############ Grant')
					print('\n\n\n')
					if not asset.category_id.grant_account_id:
						raise ValidationError(_('Please Add Grants Account to the Category'))


					move_id = self.create_move(
						ref=_('Asset Grant'),
						journal_id=asset.category_id.journal_id.id,
						asset_id=asset.id,
						date=self.date )

					move_id.line_ids = [
						(0,0,{
							'name' : ('Asset Grant'), 
							'account_id' : asset.category_id.account_asset_id.id, 
							'debit':False, 
							'credit':abs( self.old_value ), 
							'date':self.date ,
						}),
						(0,0,{
							'name' : ('Asset Give'), 
							'account_id' : asset.category_id.grant_account_id.id, 
							'credit':False, 
							'debit':abs( self.old_value ), 
							'date':self.date, 
							})]
					move_id.post()
					asset.state = 'granted'


							
				if self.dispose_type == 'lost':
					print('############ Lost')
					print('\n\n\n')

					if not asset.category_id.acqusition_lost_account_id:
						raise ValidationError(_('Please Add Acqusition Lost Account to the Category'))

					move_id = self.create_move(
						ref=_('Asset Lost'),
						journal_id=asset.category_id.journal_id.id,
						asset_id=asset.id,
						date=self.date )

					move_id.line_ids = [
						(0,0,{
							'name' : ('Asset Lost'), 
							'account_id' : asset.category_id.account_asset_id.id, 
							'debit':False, 
							'credit':abs( self.old_value ), 
							'date':self.date ,
						}),
						(0,0,{
							'name' : ('Asset Lost'), 
							'account_id' : asset.category_id.acqusition_lost_account_id.id, 
							'credit':False, 
							'debit':abs( self.old_value ), 
							'date':self.date, 
							})]
					move_id.post()
					asset.state = 'lost'




		if self.type == 'freez':

			for asset in self.env['account.asset.asset'].search([('id','in',self._context['active_ids'])]):
				if asset.inv_account_id:
					move_id = self.create_move(
						ref=_('Asset Freez'), 
						journal_id=asset.category_id.journal_id.id, 
						asset_id=asset.id, 
						date=self.date) 

					self.create_move_line(
						name=_('Asset Freez'), 
						move_id=move_id.id, 
						account_id=asset.category_id.account_asset_id.id,
						credit=self.value)

					self.create_move_line(
						name=_('Asset Asset'), 
						move_id=move_id.id, 
						account_id=asset.inv_account_id.id,
						debit=self.value)
					move_id.post()

					for line in asset.depreciation_line_ids:
						if line.remaining_value == 0:
							line.amount = line.amount - 1
							line.depreciated_value = line.depreciated_value - 1
							line.remaining_value = line.remaining_value + 1

				else:
					raise ValidationError(_('Please Add Inventory Account !'))

				asset.state = 'freez'


		if self.type == 'unfreez':

			for asset in self.env['account.asset.asset'].search([('id','in',self._context['active_ids'])]):
				if asset.inv_account_id:
					move_id = self.create_move(
						ref=_('Asset unFreez'), 
						journal_id=asset.category_id.journal_id.id, 
						asset_id=asset.id, 
						date=self.date) 

					self.create_move_line(
						name=_('Asset unFreez'), 
						move_id=move_id.id, 
						account_id=asset.inv_account_id.id,
						credit=self.value)

					self.create_move_line(
						name=_('Asset Asset'), 
						move_id=move_id.id, 
						account_id=asset.category_id.account_asset_id.id,
						debit=self.value)


					move_id.post()

					for line in asset.depreciation_line_ids:
						if line.remaining_value == 0:
							line.amount = line.amount - 1
							line.depreciated_value = line.depreciated_value - 1
							line.remaining_value = line.remaining_value + 1

				else:
					raise ValidationError(_('Please Add Inventory Account !'))

				asset.state = 'open'








	def create_move(self, ref, journal_id,asset_id=False, date=False):
		move = self.env['account.move']
		vals = {
			'ref': ref,
			'journal_id': journal_id,
			'date' : date,
			'asset_id' : asset_id,
		}
		return move.create(vals)

	def create_move_line(self, partner_id=False, name=False, move_id=False, account_id=False, debit=False, credit=False, date=False, amount_currency=False, currency_id=False, analytic_account_id=False, analytic_tag_ids=False,cost_center_id=False):
		move_line = self.env['account.move.line']
		vals = {
			'partner_id': partner_id,
			'name': name,
			'move_id': move_id,
			'account_id': account_id,
			'debit': debit,
			'credit': credit,
			'date_maturity' : date,
			'amount_currency' : amount_currency,
			'currency_id' : currency_id,
			'analytic_account_id' : analytic_account_id, 
			'analytic_tag_ids': analytic_tag_ids,
			'cost_center_id': cost_center_id,
		}
		return move_line.with_context(check_move_validity=False).create(vals)



class AssetCategory(models.Model):
	_inherit = 'account.asset.category'

	percentage = fields.Float(string='Annual Depreciation Percentage')
	revaluation_account_id = fields.Many2one('account.account', string='Re-evaluation Account')
	accusition_earning_account_id = fields.Many2one('account.account', string='Acqusition Earnings Account')
	acqusition_lost_account_id = fields.Many2one('account.account', string='Acqusition Losts Account')
	grant_account_id = fields.Many2one('account.account', string='Grant Account')

class AccountMove(models.Model):
	_inherit = 'account.move'

	asset_id = fields.Many2one('account.asset.asset')


class Payment(models.Model):
	_inherit = 'ratification.payment'

	@api.multi
	def do_create(self):
		res = super(Payment,self).do_create()

		for line in self.line_ids:
			if line.account_id.is_asset_account and line.account_id.asset_category_id:
				asset_id = self.env['account.asset.asset'].sudo().create({
						'category_id' : line.account_id.asset_category_id.id,
						'date' : self.date,
						'value': line.amount,
					})

		return res