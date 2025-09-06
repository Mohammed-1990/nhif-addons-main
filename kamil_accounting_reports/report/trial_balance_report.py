# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class TrialBalanceReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.trial_balance_tempate'


	def get_type(self,field=False):
		if field:
			return type(field)
		else:
			return False

	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		type = data['from']['type']
		company_ids = data['from']['company_ids']
		selected_company_ids = data['from']['selected_company_ids']
		company_id_logo = self.env.user.company_id.logo

		selected_company_names = []
		for company_id in self.env['res.company'].search([('id','in', selected_company_ids)]):
			selected_company_names.append( company_id.short_name or company_id.name )

		docs = []	
		
		account_list = []
		account_code = ['1','2','3','4']

		move_line = self.env['account.move.line']
		account_account = self.env['account.account']
		
		account_codes_list = []
		for code in account_code:
			accounts = account_account.sudo().search([('code','=like',(code + '%')),('company_id','in',company_ids)])

			for line in accounts:

				if code == '1':
					if len(line.code) == 1:
						if line.code not in account_codes_list:
							account_codes_list.append(line.code)
							account_list.append({
								'name': line.code + ' ' + line.name,
								'id':line.id,
								'code': line.code,
								'number':code
							})

				if code in ['2','4']:
					if len(line.code) == 2 :
						if line.code not in account_codes_list:
							account_codes_list.append(line.code)
							account_list.append({
								'name': line.code + ' ' + line.name,
								'id':line.id,
								'code': line.code,
								'number':code

								})
				if code == '3':
					if len(line.code) == 3:
						if line.code not in account_codes_list:
							account_codes_list.append(line.code)
							account_list.append({
								'name': line.code + ' ' +  line.name,
								'id':line.id,
								'code': line.code,
								'number':code
							})



		if len(company_ids) == 1:
			company_where_clause = " l.company_id = " + str(company_ids[0])

		else:
			company_where_clause = " l.company_id in " + str( tuple(company_ids))



		if type == 'totals':

			date_where_clause = "  l.date between '" + str(date_from) + "' and  '" + str(date_to) + "'  "

			for account in account_list:
				state_lines = []
				debit = credit = 0

				for company_id in company_ids:
					
					self._cr.execute( "select COALESCE(sum(COALESCE( debit, 0 )), 0 ) debit, COALESCE(sum(COALESCE( credit, 0 )), 0) credit  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account['code']+'%') +"' and " + date_where_clause + " and l.company_id = " + str(company_id) )
				
					state_balances = self.env.cr.fetchall()

					state_debit = state_balances[0][0]
					state_credit = state_balances[0][1]

					debit += state_debit
					credit += state_credit

					company = self.env['res.company'].sudo().search([('id','=',company_id)])[0]

					if state_debit or state_credit:
						state_lines.append({
							'account_id' : account['id'],
							'branch_name' : company.short_name or company.name,
							'state_debit' : state_debit,
							'state_credit' : state_credit,
							'class':'',
							})


				if debit or credit:
					docs.append({
						'account_id' : account['id'],
						'account_name':account['name'],
						'debit':debit,
						'credit':credit,
						'state_lines' : state_lines,
						})
		else: 
			if type == 'balances':
				for account in account_list:
					if account['code'][:1] in ['1','2']:
						date_from = date(datetime.strptime(date_to,'%Y-%m-%d').year, 1, 1)
						date_where_clause = "  l.date between '" + str(date_from) + "' and  '" + str(date_to) + "'  "
					else:
						date_where_clause = " l.date <= '" + str(date_to) + "' "
					state_lines = []
					debit = credit = 0
					net_profit = 0

					for company_id in company_ids:
						######################################
						######################################
						######################################
						#net profit
						if account['code'] == '41':
							date_from1 = date(date_from.year - 1, 1, 1)
							date_to1 = date(date_from1.year, 12, 31)
							account_list1 = []
							account_code1 = ['1','2']
							account_account1 = self.env['account.account']
							account_codes_list1 = []
							for code_profit in account_code1:
								accounts1 = account_account1.search([('code','=like',(code_profit + '%'))])
								for line_profit in accounts1:
									if code_profit in ['1','2']:
										if len(line_profit.code) == 2 :
											if line_profit.code not in account_codes_list1:
												account_codes_list1.append(line_profit.code)
												account_list1.append({
													'name': line_profit.code + ' ' + line_profit.name ,
													'id':line_profit.id,
													'code': line_profit.code,
													'number':code_profit,
													'clarification_number' : line_profit.clarification_number
													})

							total_revenues = 0
							total_expenses = 0
							for account1 in account_list1:
								line_balance1 = 0
								self._cr.execute( "select COALESCE(sum(COALESCE( debit, 0 )), 0 ) debit, COALESCE(sum(COALESCE( credit, 0 )), 0) credit  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account1['code']+'%') +"' and l.date between '" + str(date_from1) + "' and  '" + str(date_to1) + "' and l.company_id = " + str(company_id)  )
								balances1 = self.env.cr.fetchall()
								debit1 = balances1[0][0]
								credit1 = balances1[0][1]
								balance1 = 0
								if account1['code'][:1] == '1':
									balance1 = credit1 - debit1
									total_revenues += balance1
								else:
									balance1 = debit1 - credit1
									total_expenses += balance1
							net_profit = total_revenues - total_expenses
						###############################################	
						###############################################	
						###############################################	
						self._cr.execute( "select COALESCE(sum(COALESCE( debit, 0 )), 0 ) debit, COALESCE(sum(COALESCE( credit, 0 )), 0) credit  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account['code']+'%') +"' and " + date_where_clause + " and l.company_id = " + str(company_id) )
						state_balances = self.env.cr.fetchall()
						state_debit = state_balances[0][0]
						state_credit = state_balances[0][1]
						debit += state_debit
						credit += state_credit

						company = self.env['res.company'].sudo().search([('id','=',company_id)])[0]
						
						if state_debit or state_credit:
							line_credit = line_debit = 0
							if account['code'][:1] in ['1','4']:
								#carry_over_balance
								line_balance = state_credit - state_debit
								if line_balance > 0:
									carry_over_balance_credit = line_balance
									carry_over_balance_debit = 0
								else:
									carry_over_balance_credit = 0
									carry_over_balance_debit = abs(line_balance)
								#net profit
								if net_profit > 0:
									net_profit_credit = net_profit
									net_profit_debit = 0
								else:
									net_profit_credit = 0
									net_profit_debit = abs(net_profit)
									print("/n/n/n")
								#balance
								line_balance += net_profit
								if line_balance > 0:
									line_credit = line_balance
									line_debit = 0
								else:
									line_credit = 0
									line_debit = abs(line_balance)
							if account['code'][:1] in ['2','3']:
								line_balance = state_debit - state_credit
								if line_balance > 0:
									line_debit = line_balance
									line_credit = 0
								else:
									line_credit = abs(line_balance)
									line_debit = 0

							state_lines.append({
								'account_id' : account['id'],
								'branch_name' : company.short_name or company.name,
								'state_debit' : line_debit,
								'state_credit' : line_credit,
								})
							if account['code'] == '41':
								state_lines.append({
									'branch_name' : 'الرصيد المرحل',
									'account_id' : account['id'],
									'state_debit' : carry_over_balance_debit,
									'state_credit' : carry_over_balance_credit,
								})
								state_lines.append({
									'branch_name' : 'صافي رصيد التشغيل',
									'state_debit' : net_profit_debit,
									'state_credit' : net_profit_credit,
								})


					if debit or credit:
						line_credit = line_debit = 0
						if account['code'][:1] in ['1','4']:
							line_balance = credit - debit
							line_balance += net_profit
							if line_balance > 0:
								line_credit = line_balance
								line_debit = 0
							else:
								line_credit = 0
								line_debit = abs(line_balance)
						if account['code'][:1] in ['2','3']:
							line_balance = debit - credit
							if line_balance > 0:
								line_debit = line_balance
								line_credit = 0
							else:
								line_credit = abs(line_balance)
								line_debit = 0

						docs.append({
							'account_id' : account['id'],
							'account_name':account['name'],
							'debit':line_debit,
							'credit':line_credit,
							'state_lines' : state_lines,
							})


		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to,
			'company_id_logo': company_id_logo,
			'report_type' : type,
			'selected_company_names':selected_company_names,
			
		}


		