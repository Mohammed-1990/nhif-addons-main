
# -*- coding:utf-8 -*-
from odoo import models, fields, api


class AccountStatementReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.statement_template'


	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		revenue_account_ids = data['from']['revenue_account_ids']
		type = data['from']['type']

		domain = []
		if date_from:
			domain.append(('date_maturity','>=',date_from))
		if date_to:
			domain.append(('date_maturity','<=',date_to))

		docs = []	

		if type == 'account_statment':
			account_move_line = self.env['account.move.line']
			if revenue_account_ids:
				domain.append(('id','in',revenue_account_ids))
			domain2 = [('code','=like','1%'),('is_group','=','sub_account')]
			if revenue_account_ids:
				domain2.append(('id','in',revenue_account_ids))

			accounts = self.env['account.account'].search(domain2)
			budget = self.env['crossovered.budget'].search([('state','=','validate')], limit=1)


			print('\n\n\n')
			print('#########  domain ', domain)
			print('#########  domain ', domain2)
			print('#########')
			print('\n\n\n')

			for account in accounts:
				vals = []
				planned_value = 0.0
				

				account_move = account_move_line.search([('account_id','=',account.id),('date_maturity','>=',date_from),('date_maturity','<=',date_to)])
				
				for move in account_move:
					for rec in budget.revenues_line_ids:
						for line in rec.general_budget_id.accounts_value_ids:
							if line.account_id.id == account.id:
								planned_value += line.planned_value

					
					vals.append({
							'name':move.account_id.code + ' ' + move.account_id.name,
							'date':move.date,
							'ref':move.move_id.document_number or move.name or move.move_id.name,
							'debit':move.debit,
							'credit':move.credit,
							'description':move.name or move.move_id.name
						})
					print('\n\n\n')
					print('%%%%%%%%%% planned_value = ', planned_value)
					print('%%%%%%%%%% move.credit = ', move.credit)
					print('%%%%%%%%%% move.credit = ', move.credit)
					print('\n\n\n')
				docs.append({
					'account_name':account.name,
					'planned_value':planned_value,
					'vals': vals
					})

				print('\n\n\n')
				print('############  vals = ',vals)
				print('\n\n\n')
		else:
			domain2 = [('code','=like','1%'),('is_group','=','group')]
			if revenue_account_ids:
				domain2.append(('id','in',revenue_account_ids))

				
			accounts = self.env['account.account'].search(domain2)
			for account in accounts:
				debit = credit = 0.0
				account_move_line = self.env['account.move.line']
				for line in account_move_line.search([('account_id.code','=like',(account.code + '%'))]):
					debit += line.debit
					credit += line.credit
				docs.append({
					'group_name': account.name,
					'debit':debit,
					'credit':credit,
					'net_term':credit - debit
				})


		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to, 
			'type':type
		}


		