# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class DetailedRevenuesSynthesisReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.detail_rev_temp'


	def get_accounting_format(self, number):
		if number < 0:
			number = '(' + str('{:,.2f}'.format( abs(number) ) ) + ')'
		else:
			number = str('{:,.2f}'.format( abs(number) ) )
		return number


	@api.model
	def _get_report_values(self, docids, data=None):

		group_ids = data['from']['group_ids']
		
		year = data['from']['year']
		company_ids = data['from']['company_ids']
		account_id =  data['from']['account_id']
		company_id_logo = self.env.user.company_id.logo

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']

		account_id = self.env['account.account'].sudo().search([('id','=',account_id)])[0]


		all_accounts_codes = []
		all_accounts_names = []

		accounts_names_codes = []

		data_rows = {}
		budget_rows = {}
		percentage_rows = {}

		company_total = {}
		budget_company_total = {}
		percentage_company_total = {}


		for account in self.env['account.account'].sudo().search([('code','=ilike',account_id.code+'%'),(['company_id','in',company_ids]),('is_group','=','group')]):
			if len(account.code) == 3:
				if account.code not in all_accounts_codes:
					all_accounts_codes.append( account.code )
					accounts_names_codes.append({
					'account_code' : account.code,
					'account_name' : account.name
					})
					data_rows[account.code] = {}
					budget_rows[account.code] = {}
					percentage_rows[account.code] = {}


		account_total = {}
		company_names_ids = []
		all_companies_total = 0
		all_budget_total = 0
		all_percentage_total = 0

		budget_account_total = {}
		percentage_account_total = {}



		for company_id in self.env['res.company'].sudo().search([('id','in',company_ids)]):
			
			company_total[company_id.id] = 0
			budget_company_total[company_id.id] = 0
			percentage_company_total[company_id.id] = 0

			for account in accounts_names_codes:

				self._cr.execute("select COALESCE(sum(COALESCE( l.credit, 0 )), 0 ) - COALESCE(sum(COALESCE( l.debit, 0 )), 0) from account_move_line l inner join account_account a on l.account_id = a.id where a.code like '" + account['account_code'] + '%' + "' and l.date >= '" + str(date_from) + "' and l.date <= '" + str(date_to) + "' and l.company_id = " + str(company_id.id) )

				actual_balance = self.env.cr.fetchone()[0] or 0.0

				account_budget_value = 0
				for account_line in self.env['account.account'].sudo().search([('code','=ilike',account['account_code']+'%'),('company_id','=',company_id.id),('is_group','=','sub_account')]):
					for budget in self.env['crossovered.budget'].sudo().search([('date_from','<=',date_from),('date_to','>=',date_to),('company_id','=',company_id.id)]):
						for expenses_line in budget.revenues_line_ids:
							for budget_line in expenses_line.general_budget_id.accounts_value_ids:
								if budget_line.account_id == account_line:
									if budget_line.approved_value > 0:
										account_budget_value += budget_line.approved_value

				budget_company_total[company_id.id] += account_budget_value

				if budget_account_total.get( account['account_code'], False ):
					budget_account_total[account['account_code']] += account_budget_value
				else:					
					budget_account_total[account['account_code']] = account_budget_value

				percentage = 0
				if account_budget_value > 0 :
					percentage = actual_balance / account_budget_value * 100

				data_rows[account['account_code']][company_id.id] = self.get_accounting_format(actual_balance)
				budget_rows[account['account_code']][company_id.id] = self.get_accounting_format(account_budget_value)
				percentage_rows[account['account_code']][company_id.id] = self.get_accounting_format(percentage)
				



				company_total[company_id.id] += actual_balance

				all_companies_total += actual_balance
				all_budget_total += account_budget_value


				if account_total.get( account['account_code'], False ):
					account_total[account['account_code']] += actual_balance
				else:					
					account_total[account['account_code']] = actual_balance

				percentage_account_total[account['account_code']] = 0
				if budget_account_total[account['account_code']] > 0:
					percentage_account_total[account['account_code']] = account_total[account['account_code']] / budget_account_total[account['account_code']] * 100



			if company_total[company_id.id] > 0:
				company_names_ids.append({
					'company_id' : company_id.id,
					'company_name' : company_id.short_name or company_id.name,
					})

				if budget_company_total[company_id.id] > 0:
					percentage_company_total[company_id.id] = company_total[company_id.id] / budget_company_total[company_id.id] * 100 


		if all_budget_total > 0:
			all_percentage_total = all_companies_total / all_budget_total * 100

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'year': year,

			'date_from' : date_from,
			'date_to' : date_to,
		
			'all_accounts_names' : all_accounts_names,
			'accounts_names_codes' : accounts_names_codes,
			'company_names_ids' : company_names_ids,

			'data_rows' : data_rows,
			'budget_rows' : budget_rows,
			'percentage_rows' : percentage_rows,

			'company_total' : company_total,
			'budget_company_total' : budget_company_total,
			'percentage_company_total' : percentage_company_total,

			'account_total' : account_total,
			'budget_account_total' : budget_account_total,
			'percentage_account_total' : percentage_account_total,
			'company_id_logo': company_id_logo,

			'all_companies_total' : all_companies_total,
			'all_budget_total' : all_budget_total,
			'all_percentage_total' : all_percentage_total,
			
		}


		