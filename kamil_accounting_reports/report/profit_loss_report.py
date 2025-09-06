# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class ProfitLossReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.profit_loss_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		date_from1 = date(fields.Date.from_string(date_from).year-1, 1, 1) 
		date_to1 = date(fields.Date.from_string(date_to).year-1, 12, 31)
		company_ids = data['from']['company_ids']
		selected_company_ids = data['from']['selected_company_ids']
		company_id_logo = self.env.user.company_id.logo

		selected_company_names = []
		for company_id in self.env['res.company'].search([('id','in', selected_company_ids)]):
			selected_company_names.append( company_id.short_name or company_id.name )

		date_where_clause = "  l.date between '" + str(date_from) + "' and  '" + str(date_to) + "'  "
		date_where_clause2 = "  l.date between '" + str(date_from1) + "' and  '" + str(date_to1) + "'  "

		if len(company_ids) == 1:
			company_where_clause = " l.company_id = " + str(company_ids[0])
		else:
			company_where_clause = " l.company_id in " + str( tuple(company_ids))

		account_list = []
		account_code = ['1','2']

		account_account = self.env['account.account']

		account_codes_list = []
		for code in account_code:
			accounts = account_account.search([('code','=like',(code + '%'))])

			for line in accounts:
				if code in ['1','2']:
					if len(line.code) == 2 :
						if line.code not in account_codes_list:
							account_codes_list.append(line.code)
							account_list.append({
								'name': line.code + ' ' + line.name ,
								'id':line.id,
								'code': line.code,
								'number':code,
								'clarification_number' : line.clarification_number
								})


		revenues_data_rows = []
		expenses_data_rows = []
		current_total_revenues = current_total_expenses = 0
		last_total_revenues = last_total_expenses = 0

		current_net_profit = last_net_profit = 0

		for account in account_list:
			
			current_line_balance = last_line_balance = 0

			branches_balance_list = []
			for company_id in company_ids:
				
				self._cr.execute( "select COALESCE(sum(COALESCE( debit, 0 )), 0 ) debit, COALESCE(sum(COALESCE( credit, 0 )), 0) credit  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account['code']+'%') +"' and l.date between '" + str(date_from) + "' and  '" + str(date_to) + "' and l.company_id = " + str(company_id)  )
				current_balances = self.env.cr.fetchall()

				self._cr.execute( "select COALESCE(sum(COALESCE( debit, 0 )), 0 ) debit, COALESCE(sum(COALESCE( credit, 0 )), 0) credit  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account['code']+'%') +"' and l.date between '" + str(date_from1) + "' and  '" + str(date_to1) + "' and l.company_id = " + str(company_id)  )
				last_balances = self.env.cr.fetchall()

				current_debit = current_balances[0][0]
				current_credit = current_balances[0][1]

				last_debit = last_balances[0][0]
				last_credit = last_balances[0][1]

				current_balance = last_balance = 0
				if account['code'][:1] == '1':
					current_balance = current_credit - current_debit
					last_balance = last_credit - last_debit
					current_total_revenues += current_balance
					last_total_revenues += last_balance 
				else:
					current_balance = current_debit - current_credit
					last_balance = last_debit - last_credit
					current_total_expenses += current_balance
					last_total_expenses += last_balance

				current_line_balance += current_balance
				last_line_balance += last_balance

				company = self.env['res.company'].sudo().search([('id','=',company_id)])[0]
				if current_balance or last_balance:
					

					if current_balance < 0:
						current_balance = '(' + str('{:,.2f}'.format( abs(current_balance) ) ) + ')'
					else:
						current_balance = str('{:,.2f}'.format( current_balance ) )

					if last_balance < 0:
						last_balance = '(' + str('{:,.2f}'.format( abs(last_balance) ) ) + ')'
					else:
						last_balance = str('{:,.2f}'.format( last_balance ) )


					branches_balance_list.append({
						'brach_name' : company.short_name or company.name,
						'account_id' : account['id'],
						'account_name' : account['name'],
						'current_balance' : current_balance, 
						'last_balance' : last_balance, 
					})


			if current_line_balance < 0:
				current_line_balance = '(' + str('{:,.2f}'.format( abs(current_line_balance) ) ) + ')'
			else:
				current_line_balance = str('{:,.2f}'.format( current_line_balance ) )


			if last_line_balance < 0:
				last_line_balance = '(' + str('{:,.2f}'.format( abs(last_line_balance) ) ) + ')'
			else:
				last_line_balance = str('{:,.2f}'.format( last_line_balance ) )



			if account['code'][:1] == '1':
				
				revenues_data_rows.append({
					'account_id' : account['code'],
					'account_name' :  account['name'],
					'clarification_number' : account['clarification_number'],
					'current_balance' : current_line_balance,
					'last_balance' : last_line_balance,
					'braches_list' : branches_balance_list,
					})

			if account['code'][:1] == '2':

				expenses_data_rows.append({
					'account_id' : account['code'],
					'account_name' :  account['name'],
					'clarification_number' : account['clarification_number'],
					'current_balance' : current_line_balance,
					'last_balance' : last_line_balance,
					'braches_list' : branches_balance_list,
					})

		current_net_profit = current_total_revenues - current_total_expenses
		last_net_profit = last_total_revenues - last_total_expenses

		if current_net_profit > 0:
			current_type = 'دائن'
		else:
			current_type = 'مدين'


		if last_net_profit > 0:
			last_type = 'دائن'
		else:
			last_type = 'مدين'
			


		if current_total_revenues < 0:
			current_total_revenues = '(' + str('{:,.2f}'.format( abs(current_total_revenues) ) ) + ')'
		else:
			current_total_revenues = str('{:,.2f}'.format( current_total_revenues ) )


		if last_total_revenues < 0:
			last_total_revenues = '(' + str('{:,.2f}'.format( abs(last_total_revenues) ) ) + ')'
		else:
			last_total_revenues = str('{:,.2f}'.format( last_total_revenues ) )



		if current_total_expenses < 0:
			current_total_expenses = '(' + str('{:,.2f}'.format( abs(current_total_expenses) ) ) + ')'
		else:
			current_total_expenses = str('{:,.2f}'.format( current_total_expenses ) )



		if last_total_expenses < 0:
			last_total_expenses = '(' + str('{:,.2f}'.format( abs(last_total_expenses) ) ) + ')'
		else:
			last_total_expenses = str('{:,.2f}'.format( last_total_expenses ) )



		if current_net_profit < 0:
			current_net_profit = '(' + str('{:,.2f}'.format( abs(current_net_profit) ) ) + ')'
		else:
			current_net_profit = str('{:,.2f}'.format( current_net_profit ) )

		if last_net_profit < 0:
			last_net_profit = '(' + str('{:,.2f}'.format( abs(last_net_profit) ) ) + ')'
		else:
			last_net_profit = str('{:,.2f}'.format( last_net_profit ) )


		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'date_from': date_from,
			'date_to' : date_to, 

			'current_year' : fields.Date.from_string(date_from).year,
			'last_year' : fields.Date.from_string(date_from1).year,
			'revenues_data_rows' : revenues_data_rows,
			'expenses_data_rows' : expenses_data_rows,

			'current_total_revenues' : current_total_revenues,
			'last_total_revenues' : last_total_revenues,
			'current_total_expenses' : current_total_expenses,
			'last_total_expenses':last_total_expenses,

			'current_net_profit' : current_net_profit,
			'last_net_profit' : last_net_profit,
			'company_id_logo': company_id_logo,

			'current_type' : current_type,
			'last_type' : last_type,

			'selected_company_names' : selected_company_names,
		}


		