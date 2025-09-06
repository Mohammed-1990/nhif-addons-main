# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class ExpensesJournalReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.expenses_journal_template'

	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		group_id = data['from']['group_id']
		company_id_logo = self.env.user.company_id.logo

		account_id = data['from']['group_id']		
		account_id = self.env['account.account'].search([('id','=',account_id)])

		all_accounts = self.env['account.account'].search([('code','=ilike', str(account_id.code) + '%'),('is_group','=','sub_account')])

		accounts_total = {}
		
		for account in all_accounts:
			accounts_total[account.id] = {'debit' : 0, 'credit':0}



		all_data = {}

		row_keys = []
		column_keys = []



		self._cr.execute(" select  m.ref, m.date , m.document_number, m.id move_id,l.account_id account_id, sum(COALESCE( l.debit, 0 )) sum_of_debit, sum(COALESCE( l.credit, 0 )) sum_of_credit from account_move_line l inner join account_move m  on m.id = l.move_id where l.account_id in " + str(tuple( all_accounts._ids )) + " AND m.date >= '"+ date_from +"' and m.date <= '"+ date_to +"' group by l.account_id, m.id")

		all_records = self.env.cr.fetchall()

		self._cr.execute(" select  m.id move_id from account_move_line l inner join account_move m  on m.id = l.move_id where l.account_id in " + str(tuple( all_accounts._ids )) + " AND m.date >= '"+ date_from +"' and m.date <= '"+ date_to +"' ")

		move_ids = self.env.cr.fetchall()

		# # 0 -> name 
		# # 1 -> date 
		# # 2 -> document_number 
		# # 3 -> move_id 
		# # 4 -> account_id 
		# # 5 -> debit 
		# # 6 -> credit 
		
		self._cr.execute(" select  m.ref, m.date, m.id, document_number  from account_move_line l inner join account_move m  on m.id = l.move_id where l.account_id in " + str(tuple( all_accounts._ids )) + " AND m.date >= '"+ date_from +"' and m.date <= '"+ date_to +"' ")
		moves_data = self.env.cr.fetchall()

		move_ids_list = []
		for move in move_ids:
			if move[0] not in move_ids_list:
				move_ids_list.append( move[0]  )


		net_moves_data = {}
		for move_id in move_ids_list:
			for move in moves_data:
				if move[2] == move_id:
					net_moves_data[move_id] = {
						'name': move[0],
						'date' : move[1],
						'move_id' : move[2],
						'document_number' : move[3],
					}
						
		for move_line in self.env['account.move.line'].search([('account_id','in',all_accounts._ids),('date','>=',date_from),('date','<=',date_to)],order='date asc'):

			found = False	

			move_found = False
			account_found = False

			accounts_total[ move_line.account_id.id ]['debit'] += move_line.debit
			accounts_total[ move_line.account_id.id ]['credit'] += move_line.credit


			if all_data.get(move_line.move_id.id, False):
				move_found = True
				if all_data[move_line.move_id.id].get(move_line.account_id.id, False):

					account_found = True
					found = True					
					
					all_data[move_line.move_id.id][move_line.account_id.id]['debit'] += move_line.debit
					all_data[move_line.move_id.id][move_line.account_id.id]['credit'] += move_line.credit


					all_data[move_line.move_id.id][move_line.account_id.id]['str_debit'] = '{:,.2f}'.format( all_data[move_line.move_id.id][move_line.account_id.id]['debit'] )

					all_data[move_line.move_id.id][move_line.account_id.id]['str_credit'] = '{:,.2f}'.format( all_data[move_line.move_id.id][move_line.account_id.id]['credit'] )


			if not found:
				if not move_found and not account_found:
					all_data[move_line.move_id.id] = {}
					all_data[move_line.move_id.id][move_line.account_id.id] = {
						'name' : move_line.move_id.ref,
						'date' : move_line.move_id.date,
						'document_number' : move_line.move_id.document_number,
						'debit' : move_line.debit,
						'credit' : move_line.credit,

						'str_debit' : '{:,.2f}'.format( move_line.debit ), 
						'str_credit' : '{:,.2f}'.format( move_line.credit ),

						'account_id' : move_line.account_id.id,
						'account_id_str' : str(move_line.account_id.id),
						'move_id' : move_line.move_id.id, 
						
						}
				if move_found and not account_found:
					all_data[move_line.move_id.id][move_line.account_id.id] = {
						'name' : move_line.move_id.ref,
						'date' : move_line.move_id.date,
						'document_number' : move_line.move_id.document_number,
						'debit' : move_line.debit,
						'credit' : move_line.credit, 
						
						'str_debit' : '{:,.2f}'.format( move_line.debit ), 
						'str_credit' : '{:,.2f}'.format( move_line.credit ),

						'account_id' : move_line.account_id.id,
						'account_id_str' : str(move_line.account_id.id),
						'move_id' : move_line.move_id.id, 
						
						}

				if move_line.move_id.id not in row_keys:
					row_keys.append( move_line.move_id.id )
				if move_line.account_id.id not in column_keys:
					column_keys.append( move_line.account_id.id )
			

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'date_from': date_from,
			'date_to' : date_to, 
			'all_accounts' : all_accounts,
			'move_ids_list' : move_ids_list,
			'all_records' : all_records,
			'net_moves_data' : net_moves_data,
			'accounts_total' : accounts_total,
			'company_id_logo': company_id_logo,
			'all_data' : all_data,
			'row_keys' : row_keys,
			'column_keys' : column_keys,
		}

		