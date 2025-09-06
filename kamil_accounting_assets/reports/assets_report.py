# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime

class AssetsReport(models.AbstractModel):
	_name = 'report.kamil_accounting_assets.assets_template'


	@api.model
	def _get_report_values(self, docids, data=None):
		date = data['form']['date']
		first_day = data['form']['first_day']
		last_day = data['form']['last_day']
				

		# assets_accounts = self.env['account.account'].search(['|',('code','=ilike','300%'),('code','=ilike','302%'),('is_group','=','sub_account')])
		assets_accounts = self.env['account.account'].search([('is_asset_account','=',True)])

		docs = []

		for account_id in assets_accounts._ids:
			
			balance_in_1_1 = 0
			year_addition = 0
			year_exclude = 0
			balance_in_31_12 = 0
			dep_percentage = 0
			account_dep_expense_id = False
			account_dep_id = False
			year_dep = 0
			accumulative_dep = 0

			dep_in_1_1 = 0
			net_asset = 0

			self._cr.execute("select sum(credit)-sum(debit) from account_move_line where account_id="  + str(account_id) + " AND date < '" + str(first_day)+ "'  " )
			balance_in_1_1 = abs(self.env.cr.fetchone()[0] or 0.0)

			self._cr.execute("select sum(debit) from account_move_line where account_id="  + str(account_id) + " AND date >= '" + str(first_day)+ "'  " )
			year_addition = abs(self.env.cr.fetchone()[0] or 0.0)

			self._cr.execute("select sum(credit) from account_move_line where account_id="  + str(account_id) + " AND date >= '" + str(first_day)+ "'  " )
			year_exclude = abs(self.env.cr.fetchone()[0] or 0.0)

			if (year_addition - year_exclude) > 0:
				year_addition = year_addition - year_exclude
				year_exclude = 0
			elif (year_exclude - year_addition) > 0:
				year_exclude = year_exclude - year_addition
				year_addition = 0
			elif year_exclude == year_addition :
				year_addition = 0
				year_exclude = 0


			balance_in_31_12 = balance_in_1_1 + year_addition - year_exclude

			for category in self.env['account.asset.category'].search([]):
				if category.account_asset_id.id == account_id:
					dep_percentage = category.percentage
					account_dep_expense_id = category.account_depreciation_expense_id
					account_dep_id = category.account_depreciation_expense_id
					break

			if account_dep_expense_id:
				self._cr.execute("select sum(credit)-sum(debit) from account_move_line where account_id="  + str(account_dep_expense_id.id) + " AND date < '" + str(first_day)+ "'  " )
				dep_in_1_1 = abs(self.env.cr.fetchone()[0] or 0.0)

				self._cr.execute("select sum(credit)-sum(debit) from account_move_line where account_id="  + str(account_dep_expense_id.id) + " AND date >= '" + str(first_day)+ "'  " )
				year_dep = abs(self.env.cr.fetchone()[0] or 0.0)

			accumulative_dep = dep_in_1_1 + year_dep

			net_asset = balance_in_31_12 - accumulative_dep




			docs.append( {
				'name' : self.env['account.account'].search([('id','=',account_id)])[0].name,
				'balance_in_1_1' : balance_in_1_1,
				'year_addition' : year_addition,
				'year_exclude' : year_exclude,
				'balance_in_31_12' : balance_in_31_12,
				'dep_percentage' : dep_percentage,
				'dep_in_1_1' : dep_in_1_1,
				'year_dep' : year_dep,
				'accumulative_dep' : accumulative_dep,
				'net_asset' : net_asset,
				} )
		

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date': date,
			'test' : 'this is a test',
		}