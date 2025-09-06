# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class BalanceSheetReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.balance_sheet_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		
		date_to = data['from']['date_to']
		date_from_ = data['from']['date_from_']
		date_to_ = data['from']['date_to_']
		revenue_account_id = data['from']['revenue_account_id']
		company_id_logo = self.env.user.company_id.logo
		date_from = date(fields.Date.from_string(date_to).year , 1, 1) 
		date_from1 = date(date_from.year-1, 1, 1)
		date_to1 = date(date_from1.year, 12, 31)

		company_ids = data['from']['company_ids']
		selected_company_ids = data['from']['selected_company_ids']

		selected_company_names = []
		for company_id in self.env['res.company'].search([('id','in', selected_company_ids)]):
			selected_company_names.append( company_id.short_name or company_id.name )

		if len(company_ids) == 1:
			company_where_clause = " l.company_id = " + str(company_ids[0])
		else:
			company_where_clause = " l.company_id in " + str( tuple(company_ids))



		account_codes_list = []
		account_lines = []
		for account in self.env['account.account'].sudo().search(['|',('code','=ilike','3'+'%'),('code','=ilike','4'+'%'),('company_id','in',company_ids)]):
			if account.code not in account_codes_list:
				account_codes_list.append( account.code )
				if account.code[:1] == '3':
					if len(account.code) == 1:
						account_lines.append({
							'code' : account.code,
							'level' : 0,
							'id' : account.id,
							'name' : account.code + ' ' + account.name,
							'clarification_number' : '',
							'is_line' : False,
							'class' : 'table-active',
							})
					if len(account.code) == 2:
						account_lines.append({	
							'code' : account.code,			
							'level' : 50,
							'id' : account.id,
							'name' : account.code + ' ' + account.name,
							'clarification_number' : '',
							'is_line' : False,
							'class' : 'table-active',
							})

					if len(account.code) == 3:
						account_lines.append({
							'code' : account.code,
							'level': 75,
							'id' : account.id,
							'name' : account.code + ' ' + account.name,
							'clarification_number' : account.clarification_number,
							'is_line' : True,
							'class' : '',
							})

				if account.code[:1] == '4':
					#  and account.code != '42'
					if len(account.code) == 1:
						account_lines.append({
							'code' : account.code,
							'level' : 0,
							'id' : account.id,
							'name' : account.code + ' ' + account.name,
							'clarification_number' : '',
							'is_line' : False,
							'class' : 'table-active',
							})
					if len(account.code) == 2:
						account_lines.append({
							'code' : account.code,
							'level' : 50,
							'id' : account.id,
							'name' : account.code + ' ' + account.name,
							'clarification_number' : account.clarification_number,
							'is_line' : True,
							'class' : '',
							})
		for account_line in account_lines:
			if account_line['code'][:1] == '3':
				select_clause = " sum( COALESCE(l.debit, 0)) - sum( COALESCE(l.credit, 0)) "
			if account_line['code'][:1] == '4':
				select_clause = " sum( COALESCE(l.credit, 0)) - sum( COALESCE(l.debit, 0)) "
			branches_balance_list = []
			vals = []
			group_list = []
			group_list2 = []
			current_account_balance = 0
			total_debit = 0
			total_credit = 0
			last_account_balance = 0
			current_net_profit = 0
			last_net_profit = 0	
			style_class = ''
			for company_id in company_ids:
				######################################
				######################################
				######################################
				#net profit
				if account_line['code'] == '41':
					style_class = 'table-active'
				if account_line['code'] == '4' or account_line['code'] == '41':
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
					current_total_revenues = 0
					current_total_expenses = 0
					current_total_ = 0
					last_total_revenues = 0
					last_total_expenses = 0
					for account in account_list:
						current_line_balance = last_line_balance = 0
						self._cr.execute( "select COALESCE(sum(COALESCE( debit, 0 )), 0 ) debit, COALESCE(sum(COALESCE( credit, 0 )), 0) credit  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account['code']+'%') +"' and l.date between '" + str(date_from) + "' and  '" + str(date_to) + "' and l.company_id = " + str(company_id)  )
						current_balances1 = self.env.cr.fetchall()
						self._cr.execute( "select COALESCE(sum(COALESCE( debit, 0 )), 0 ) debit, COALESCE(sum(COALESCE( credit, 0 )), 0) credit  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account['code']+'%') +"' and l.date between '" + str(date_from1) + "' and  '" + str(date_to1) + "' and l.company_id = " + str(company_id)  )
						last_balances1 = self.env.cr.fetchall()
						current_debit = current_balances1[0][0]
						current_credit = current_balances1[0][1]
						current_total_ = current_credit
						last_debit = last_balances1[0][0]
						last_credit = last_balances1[0][1]
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
						if current_line_balance < 0:
							current_line_balance = '(' + str('{:,.2f}'.format( abs(current_line_balance) ) ) + ')'
						else:
							current_line_balance = str('{:,.2f}'.format( current_line_balance ) )
						if last_line_balance < 0:
							last_line_balance = '(' + str('{:,.2f}'.format( abs(last_line_balance) ) ) + ')'
						else:
							last_line_balance = str('{:,.2f}'.format( last_line_balance ) )
					current_net_profit = current_total_revenues - current_total_expenses
					last_net_profit = last_total_revenues - last_total_expenses
				###############################################	
				###############################################	
				###############################################	
				depreciation_current_balance = 0.0
				depreciation_last_balance = 0.0
				# if account_line['code'] == '4':
				# 	self._cr.execute( "select  " + select_clause + "  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account_line['code']+'%') +"' and a.code not like '"+ str('42'+'%') +"'  and l.date <= '" + str(date_to) + "' and l.company_id = " + str(company_id)  )
				# 	current_balance = self.env.cr.fetchone()[0] or 0.0
				# 	self._cr.execute( "select  " + select_clause + "  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account_line['code']+'%') +"' and a.code not like '"+ str('42'+'%') +"' and l.date <= '" + str(date_to1) + "' and l.company_id = " + str(company_id)  )
				# 	last_balance = self.env.cr.fetchone()[0] or 0.0
				if account_line['code'] == '4':
					self._cr.execute( "select  " + select_clause + "  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account_line['code']+'%') +"' and l.date <= '" + str(date_to) + "' and l.company_id = " + str(company_id)  )
					current_balance = self.env.cr.fetchone()[0] or 0.0
					self._cr.execute( "select  " + select_clause + "  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account_line['code']+'%') +"' and l.date <= '" + str(date_to1) + "' and l.company_id = " + str(company_id)  )
					last_balance = self.env.cr.fetchone()[0] or 0.0
				else:
					self._cr.execute( "select  " + select_clause + "  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account_line['code']+'%') +"'  and l.date <= '" + str(date_to) + "' and l.company_id = " + str(company_id)  )
					current_balance = self.env.cr.fetchone()[0] or 0.0
					self._cr.execute( "select  " + select_clause + "  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account_line['code']+'%') +"' and l.date <= '" + str(date_to1) + "' and l.company_id = " + str(company_id)  )
					last_balance = self.env.cr.fetchone()[0] or 0.0
				if account_line['code'] == '3' or account_line['code'] == '30':
					self._cr.execute( "select  " + select_clause + "  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str('42'+'%') +"'  and l.date <= '" + str(date_to) + "' and l.company_id = " + str(company_id)  )
					depreciation_current_balance = self.env.cr.fetchone()[0] or 0.0
					self._cr.execute( "select  " + select_clause + "  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str('42'+'%') +"' and l.date <= '" + str(date_to1) + "' and l.company_id = " + str(company_id) )
					depreciation_last_balance = self.env.cr.fetchone()[0] or 0.0
				the_opening_balance = 0
				accounts = self.env['account.account'].search([('id', '=', revenue_account_id)])
				account_move_line = self.env['account.move.line']
				code = int(accounts.code[:1])
				account2 = self.env['account.account'].search(
					[('code', '=like', (accounts.code + '%')), ('id', '!=', accounts.id)])
				for account in account2:
					credit = debit = balance = 0.0
					lines = account_move_line.search(
						[('account_id.id', '=', account.id), ('date', '>=', date_from_), ('date', '<=', date_to_)])

					for line in lines:
						debit += line.debit
						credit += line.credit

					if code == 1 or code == 4:
						balance = credit - debit
						self._cr.execute(
							"select sum( COALESCE( credit, 0 ) )-sum( COALESCE( debit, 0 ) ) from account_move_line where account_id=" + str(
								account.id) + " AND date <  '" + str(date_from_) + "'  ")

						opening_balance = abs(self.env.cr.fetchone()[0] or 0.0)
						balance = balance + opening_balance

						the_opening_balance = opening_balance

					else:
						balance = debit - credit
						self._cr.execute(
							"select sum( COALESCE( debit, 0 ) )-sum(COALESCE( credit, 0 )) from account_move_line where account_id=" + str(
								account.id) + " AND date <  '" + str(date_from_) + "'  ")

						opening_balance = abs(self.env.cr.fetchone()[0] or 0.0)
						balance = balance + opening_balance
						the_opening_balance = opening_balance

						# revenue and expenses are not carried
						month = datetime.strptime(date_from_, '%Y-%m-%d').month
						day = datetime.strptime(date_from_, '%Y-%m-%d').day
						if account.code[:1] in ('1', '2') and month == 1 and day == 1:
							balance -= the_opening_balance
							the_opening_balance = 0.00
					if balance:
						vals.append({
							'balance':balance,
						})

						group_list.append({'vals': vals})

					for line in group_list:
						if balance:
							group_list2.append(line)
				last_total = 0
				for p in vals:
					last_total += p['balance']
				############################
				current_carry_over_balance = current_balance  
				last_carry_over_balance = last_balance
				total_total_last = last_total - last_carry_over_balance
				# Add Net Profit 
				last_balance += last_net_profit
				#Deduct Depreciation
				# current_balance -= abs(depreciation_current_balance)
				# last_balance -= abs(depreciation_last_balance)
				############################
				current_net_profit_ = current_net_profit + last_net_profit
				last_account_balance += last_balance
				if account_line['code'] == '41':
					if len(company_ids) == 1:
						current_balance = current_net_profit + last_net_profit + current_carry_over_balance
						current_account_balance = current_balance
					else:
						current_balance += current_net_profit
						current_account_balance += current_balance
				elif account_line['code'] == '4':
					current_balance += current_net_profit + last_net_profit
					current_account_balance += current_balance
				else :
					current_balance += current_net_profit
					current_account_balance += current_balance
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
						'branch_name' : company.short_name or company.name,
						'id' : account_line['id'],
						'current_balance' : current_balance, 
						'last_balance' : last_balance,
					})

					if account_line['code'] == '41':
						if current_carry_over_balance < 0:
							current_carry_over_balance1 = '(' + str('{:,.2f}'.format( abs(current_carry_over_balance) ) ) + ')'
						else:
							current_carry_over_balance1 = str('{:,.2f}'.format( current_carry_over_balance ) )

						if last_carry_over_balance < 0:
							last_carry_over_balance1 = '(' + str('{:,.2f}'.format( abs(last_carry_over_balance) ) ) + ')'
						else:
							last_carry_over_balance1 = str('{:,.2f}'.format( last_carry_over_balance ) )
						#################
						if current_net_profit_ < 0:
							current_net_profit1 = '(' + str('{:,.2f}'.format( abs(current_net_profit_) ) ) + ')'
						else:
							current_net_profit1 = str('{:,.2f}'.format( current_net_profit_ ) )

						if last_net_profit < 0:
							last_net_profit1 = '(' + str('{:,.2f}'.format( abs(last_net_profit) ) ) + ')'
						else:
							last_net_profit1 = str('{:,.2f}'.format( last_net_profit ) )
						branches_balance_list.append({
							'branch_name' : 'الرصيد المرحل',
							'id' : '',
							'current_balance' : current_carry_over_balance1, 
							'last_balance' : last_carry_over_balance1,
						})
						branches_balance_list.append({
							'branch_name' : 'صافي رصيد التشغيل',
							'id' : '',
							'current_balance' : current_net_profit1, 
							'last_balance' : last_net_profit1,
						})

					
			if current_account_balance < 0:
				current_account_balance = '(' + str('{:,.2f}'.format( abs(current_account_balance) ) ) + ')'
			else:
				current_account_balance = str('{:,.2f}'.format( current_account_balance ) )
			if last_account_balance < 0:
				last_account_balance = '(' + str('{:,.2f}'.format( abs(last_account_balance) ) ) + ')'
			else:
				last_account_balance = str('{:,.2f}'.format( last_account_balance ) )
			account_line['current_account_balance'] = current_account_balance
			account_line['last_account_balance'] = last_account_balance
			account_line['branches_balance_list'] = branches_balance_list
			account_line['vals'] = group_list2
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'date_to' : date_to, 
			'current_year' : fields.Date.from_string(date_to).year,
			'company_id_logo': company_id_logo,
			'last_year' : fields.Date.from_string(date_to1).year,
			'account_lines' : account_lines,
			'selected_company_names':selected_company_names,
		}


		
