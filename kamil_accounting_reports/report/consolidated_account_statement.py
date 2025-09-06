# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime

from odoo import http
from odoo.http import request




class ConsolidatedAccountStatement(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.consolidated_a_stm_temp'


	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		account_id = data['form']['account_id']
		company_ids = data['form']['company_ids']
		selected_company_ids = data['form']['selected_company_ids']
		company_id_logo = self.env.user.company_id.logo

		selected_company_names = []
		for company_id in self.env['res.company'].search([('id','in', selected_company_ids)]):
			selected_company_names.append( company_id.short_name or company_id.name )

		account_id = self.env['account.account'].search([('id','=',account_id)])[0]
		account_name = account_id.code + ' ' +  account_id.name 
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

			for account in self.env['account.account'].sudo().search([('code','=',account_id.code),('company_id','=',company_id.id)]):
			
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
					period_net = total_credit - total_debit
					total_balance = total_credit - total_debit

				if account_type == 'expenses':
					period_net = total_debit - total_credit
					total_balance = total_debit - total_credit


				total_period_net += period_net
				total_total_balance += total_balance

				branch_total = branch_total + total_balance

				self._cr.execute("select m.date, m.document_number,COALESCE(p.payment_type, 'move') payment_type , COALESCE(c.collection_type, 'move') collection_type, COALESCE(sum(l.debit),0.0) debit, COALESCE(sum(l.credit),0.0) credit, m.ref , m.id, m.ratification_payment_id payment_id , m.collection_id, m.money_movement_id, m.money_supply_id, m.petty_cash_clearance_id from account_move m inner join account_move_line l on m.id = l.move_id left outer join ratification_payment p on p.id = m.ratification_payment_id left outer join collection_collection c on c.id = m.collection_id  where  l.account_id = "+str(account.id)+" and m.date >= '"+str(date_from)+"' and m.date <= '"+str(date_to)+"' and m.company_id = "+str(company_id.id)+"  group by m.id, p.payment_type, c.collection_type order by m.date asc;")
				

				all_moves = self.env.cr.fetchall()
				# 0 -> date    | 
				# 1 document_number 
				# 2 -> payment_type | 
				# 3-> collection_type | 
				# 4 -> debit    |   
				# 5 -> credit    |     
				# 6 -> description 
				# 7 -> move_id

				# 8 -> payment_id 
				# 9 -> collection_id 

				# 10 -> money_movement_id
				# 11 -> money_supply_id 
				# 12 -> clearance_id




				for move in all_moves:

					payment_id = move[8]
					collection_id = move[9]

					money_movement_id = move[10]
					money_supply_id = move[11]
					clearance_id = move[12]


					if collection_id == None:
						collection_id = False

					if payment_id == None:
						payment_id = False


					if money_movement_id == None:
						money_movement_id = False

					if money_supply_id == None:
						money_supply_id = False
					
					if clearance_id == None:
						clearance_id = False


					state_account_count = state_account_count + 1
					if move[2] != 'move':
						document_type = move[2]
					else:
						document_type = move[3]

					if document_type == 'Cheque':
						document_type = 'شيك'
					if document_type == 'cash':
						document_type = 'نقد'
					if document_type == 'bank_transfer':
						document_type = 'تحويل بنكي'
					if document_type == 'counter_cheque':
						document_type = 'شيك مصرفي'
					if document_type == 'move':
						document_type = 'قيد'


					debit = move[4]
					credit = move[5]
					if debit < 0:
						debit = '(' + str('{:,.2f}'.format( abs(debit) ) ) + ')'
					else:
						debit = str('{:,.2f}'.format( debit ) )
					if credit < 0:
						credit = '(' + str('{:,.2f}'.format( abs(credit) ) ) + ')'
					else:
						credit = str('{:,.2f}'.format( credit ) )

					docs.append({
						'branch' : company_id.short_name or company_id.name,
						'branch_id' : company_id.id,
						'date' : move[0],
						'document_type' : document_type,
						'document_number' : move[1],
						'debit' : debit,
						'credit' : credit,
						'description' : move[6],
						'is_state_total_added' : is_state_total_added,
						'move_id' : move[7],
						'payment_id' : payment_id,
						'collection_id' : collection_id,
						'money_movement_id' : money_movement_id,
						'money_supply_id' : money_supply_id,
						'clearance_id' : clearance_id,
						})



					if clearance_id == None:
						clearance_id = False


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
			'account_name' : account_name,
			'account_type' : account_type,
			'total_budget_value' : total_budget_value,
			'total_opening_balance' : total_opening_balance,
			'total_total_debit':total_total_debit,
			'total_total_credit':total_total_credit,
			'total_period_net' : total_period_net,
			'total_total_balance':total_total_balance,
			'state_account_count_dict' : state_account_count_dict,
			'branch_total_dict' : branch_total_dict,
			'company_id_logo': company_id_logo,
			'companies_len' : len(company_ids),
			'selected_company_names':selected_company_names,
		}


