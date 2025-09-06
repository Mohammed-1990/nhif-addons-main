# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime

class AssetsRegistryReport(models.AbstractModel):
	_name = 'report.kamil_accounting_assets.assets_registry_template'


	@api.model
	def _get_report_values(self, docids, data=None):
		
		date = data['form']['date']
		first_day = data['form']['first_day']
		last_day = data['form']['last_day']
		asset_category_ids = data['form']['asset_category_ids']
				
		print('\n\n\n')
		print('############## date = ',date)
		print('############## first_day = ', first_day)
		print('############## last_day = ', last_day)
		print('############## asset_category_ids = ',asset_category_ids)

		docs = []
		
		if not asset_category_ids:
			asset_category_ids = self.env['account.asset.category'].search([])._ids

		for asset in self.env['account.asset.asset'].search([('category_id','in',asset_category_ids),('state','!=', 'draft')]):
			
			asset_account_id = asset.category_id.account_asset_id.id
			account_dep_expense_id = asset.category_id.account_depreciation_expense_id.id 
			account_dep_id = asset.category_id.account_depreciation_expense_id.id 

			move_ids = []
			print('\n\n\n')
			for account_move in self.env['account.move'].search([('asset_id','=',asset.id)]):
				move_ids.append( account_move.id )
			for dep_line in asset.depreciation_line_ids:
				if dep_line.move_id:
					move_ids.append( dep_line.move_id.id )
			
			if not move_ids:
				move_ids.append(0)
				move_ids.append(0)
				move_ids_tuple = str(tuple(move_ids))
			else:
				if len(move_ids) == 1:
					move_ids.append(0)
				move_ids_tuple = str(tuple(move_ids))

			self._cr.execute("select sum(credit)-sum(debit) from account_move_line where account_id="  + str(asset_account_id) + " AND date < '" + str(first_day)+ "' AND move_id in   " +  move_ids_tuple + " " )
			balance_in_1_1 = abs(self.env.cr.fetchone()[0] or 0.0)

			self._cr.execute("select sum(debit) from account_move_line where account_id="  + str(asset_account_id) + " AND date >= '" + str(first_day)+ "' AND move_id in " +  move_ids_tuple + " "  )
			year_addition = abs(self.env.cr.fetchone()[0] or 0.0)

			self._cr.execute("select sum(credit) from account_move_line where account_id="  + str(asset_account_id) + " AND date >= '" + str(first_day)+ "' AND move_id in " +  move_ids_tuple + " "  )
			year_exclude = abs(self.env.cr.fetchone()[0] or 0.0)

			self._cr.execute("select sum(credit)-sum(debit) from account_move_line where account_id="  + str(account_dep_expense_id) + " AND date < '" + str(first_day)+ "'  AND move_id in " +  move_ids_tuple + " "   )
			dept_in_1_1 = abs(self.env.cr.fetchone()[0] or 0.0)


			self._cr.execute("select sum(credit)-sum(debit) from account_move_line where account_id="  + str(account_dep_expense_id) + " AND date >= '" + str(first_day)+ "'   AND move_id in " +  move_ids_tuple + " "  )
			year_dept = abs(self.env.cr.fetchone()[0] or 0.0)

			age_value = 0
			if asset.annual_dep_ratio > 0:
				age_value = 100 / asset.annual_dep_ratio

			docs.append({
				'dept_name' : asset.admin_id.name,
				'section_name' : asset.dept_id.name,
				'category_name' : asset.category_id.name,
				'asset_name' : asset.product_id.name,
				'purchase_date' : asset.date,
				'value' : asset.value,
				'last_revaluation_value': asset.last_revaluation_value,
				'total' : asset.last_revaluation_value or asset.value ,
				'balance_in_1_1' : balance_in_1_1 ,
				'addition' : year_addition,
				'execlude' : year_exclude,
				'age' :  age_value ,
				'annual_dep' :asset.annual_dep_value,
				'using_years' : 0 ,
				'dept_in_1_1': dept_in_1_1 ,
				'year_balance_in_1_1' : (asset.last_revaluation_value or asset.value ) - dept_in_1_1 ,
				'year_dept' : year_dept,
				'dept_at_end' :dept_in_1_1 + year_dept,
				'value_at_end': ((asset.last_revaluation_value or asset.value ) - dept_in_1_1) - year_dept ,
				})
								
						
		print('$$$$$$$$$$ asset_category_ids =  ',asset_category_ids)

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date': date,
			'test' : 'this is a test',
		}