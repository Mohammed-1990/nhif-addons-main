# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime



class ConsolidatedGroupStatement(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.consolidated_g_stm_temp'


	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		account_id = data['form']['account_id']
		company_ids = data['form']['company_ids']
		company_id_logo = self.env.user.company_id.logo

		account_id = self.env['account.account'].search([('id','=',account_id)])[0]
		account_type = ''
		if account_id.code[:1] == '1':
			account_type = 'revenues'
		elif account_id.code[:1] == '2':
			account_type = 'expenses'
		elif account_id.code[:1] == '3':
			account_type = 'assets'
		elif account_id.code[:1] == '4':
			account_type = 'liabilities'

		docs = []

		total_opening_balance = total_budget_value = total_total_debit = total_total_credit = total_period_net = total_total_balance = 0

		state_account_count_dict = {}
		branch_total_dict = {}
		for company_id in self.env['res.company'].sudo().search([('id','in',company_ids)]):
			state_account_count = 0
			is_state_total_added = False
			branch_total = 0
			for account in self.env['account.account'].sudo().search([('code','=ilike',account_id.code+'%'),('company_id','=',company_id.id),('is_group','=','sub_account')]):
			
				opening_balance = budget_value = 0
				
				if account_type in ['revenues','expenses']:
					for budget in self.env['crossovered.budget'].sudo().search([('date_from','<=',date_from),('date_to','>=',date_to),('company_id','=',company_id.id)]):
						if account_type == 'expenses':
							the_budget_type_line = budget.expenses_line_ids
						if account_type == 'revenues':
							the_budget_type_line = budget.revenues_line_ids					
						for budget_type_line in the_budget_type_line:
							for budget_line in budget_type_line.general_budget_id.accounts_value_ids:
								if budget_line.account_id.id == account.id:
									found = True
									if budget_line.approved_value > 0:
										budget_value = budget_line.approved_value
										total_budget_value += budget_value

				if account_type in ['assets','liabilities']:
					if account_type == 'assets':
						balance_statement = " sum(COALESCE( debit, 0 )) - sum(COALESCE( credit, 0 )) "
					if account_type == 'liabilities':
						balance_statement = " sum(COALESCE( credit, 0 )) - sum(COALESCE( debit, 0 )) "

					self._cr.execute("SELECT  " + balance_statement + "  from account_move_line where account_id="  + str(account.id) + " AND date <  '" + str(date_from) +  "'  AND company_id = " + str( company_id.id )   )

					opening_balance = self.env.cr.fetchone()[0] or 0.0
					total_opening_balance += opening_balance
				

				self._cr.execute("SELECT COALESCE(sum(COALESCE( debit, 0 )), 0 ), COALESCE(sum(COALESCE( credit, 0 )), 0) from account_move_line where account_id="  + str(account.id) + " AND date >= '" + str(date_from) +  "' AND date <= '" + str(date_to) + "' AND company_id = " + str( company_id.id )   )

				all_balances = self.env.cr.fetchall()

				total_debit = all_balances[0][0]
				total_credit = all_balances[0][1]

				total_total_debit += total_debit
				total_total_credit += total_credit




				period_net = 0
				total_balance = 0

				if account_type == 'assets':
					period_net = total_debit - total_credit
					total_balance = period_net + opening_balance

				if account_type == 'liabilities':
					period_net = total_credit - total_debit
					total_balance = period_net + opening_balance

				if account_type == 'revenues':
					total_balance = total_credit - total_debit

				if account_type == 'expenses':
					total_balance = total_debit - total_credit


				total_period_net += period_net
				total_total_balance += total_balance

				branch_total = branch_total + total_balance

				if budget_value < 0:
					budget_value = '(' + str('{:,.2f}'.format( abs(budget_value) ) ) + ')'
				else:
					budget_value = str('{:,.2f}'.format( budget_value ) )

				if opening_balance < 0:
					opening_balance = '(' + str('{:,.2f}'.format( abs(opening_balance) ) ) + ')'
				else:
					opening_balance = str('{:,.2f}'.format( opening_balance ) )

				if total_debit < 0:
					total_debit = '(' + str('{:,.2f}'.format( abs(total_debit) ) ) + ')'
				else:
					total_debit = str('{:,.2f}'.format( total_debit ) )

				if total_credit < 0:
					total_credit = '(' + str('{:,.2f}'.format( abs(total_credit) ) ) + ')'
				else:
					total_credit = str('{:,.2f}'.format( total_credit ) )

				if period_net < 0:
					period_net = '(' + str('{:,.2f}'.format( abs(period_net) ) ) + ')'
				else:
					period_net = str('{:,.2f}'.format( period_net ) )

				if total_balance < 0:
					total_balance = '(' + str('{:,.2f}'.format( abs(total_balance) ) ) + ')'
				else:
					total_balance = str('{:,.2f}'.format( total_balance ) )
				state_account_count = state_account_count + 1
				

				docs.append({
					'branch' : company_id.name,
					'branch_id' : company_id.id,
					'account_name' : account.name,
					'budget_value' : budget_value,
					'opening_balance' : opening_balance,
					'total_debit' : total_debit,
					'total_credit' : total_credit,
					'period_net' : period_net,
					'total_balance' : total_balance,
					'is_state_total_added' : is_state_total_added,
					})
				if not is_state_total_added:
					is_state_total_added = True

			state_account_count_dict[company_id.id] = state_account_count
	
			
			if branch_total < 0:
				branch_total = '(' + str('{:,.2f}'.format( abs(branch_total) ) ) + ')'
			else:
				branch_total = str('{:,.2f}'.format( branch_total ) )
				
			branch_total_dict[company_id.id] = branch_total

		if total_budget_value < 0:
			total_budget_value = '(' + str('{:,.2f}'.format( abs(total_budget_value) ) ) + ')'
		else:
			total_budget_value = str('{:,.2f}'.format( total_budget_value ) )

		if total_opening_balance < 0:
			total_opening_balance = '(' + str('{:,.2f}'.format( abs(total_opening_balance) ) ) + ')'
		else:
			total_opening_balance = str('{:,.2f}'.format( total_opening_balance ) )

		if total_total_debit < 0:
			total_total_debit = '(' + str('{:,.2f}'.format( abs(total_total_debit) ) ) + ')'
		else:
			total_total_debit = str('{:,.2f}'.format( total_total_debit ) )

		if total_total_credit < 0:
			total_total_credit = '(' + str('{:,.2f}'.format( abs(total_total_credit) ) ) + ')'
		else:
			total_total_credit = str('{:,.2f}'.format( total_total_credit ) )

		if total_period_net < 0:
			total_period_net = '(' + str('{:,.2f}'.format( abs(total_period_net) ) ) + ')'
		else:
			total_period_net = str('{:,.2f}'.format( total_period_net ) )

		if total_total_balance < 0:
			total_total_balance = '(' + str('{:,.2f}'.format( abs(total_total_balance) ) ) + ')'
		else:
			total_total_balance = str('{:,.2f}'.format( total_total_balance ) )

		return {
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to, 
			'account_type' : account_type,
			'total_budget_value' : total_budget_value,
			'total_opening_balance' : total_opening_balance,
			'total_total_debit':total_total_debit,
			'total_total_credit':total_total_credit,
			'total_period_net' : total_period_net,
			'total_total_balance':total_total_balance,
			'company_id_logo': company_id_logo,
			'state_account_count_dict' : state_account_count_dict,
			'branch_total_dict' : branch_total_dict,
			'companies_len' : len(company_ids),
		}
