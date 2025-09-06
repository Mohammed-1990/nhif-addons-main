# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class clarificationsReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.clarifications_template'

	@api.model
	def _get_report_values(self, docids, data=None):
		date_to = data['from']['date_to']
		clarification_number = data['from']['clarification_number']
		account_id = self.env['account.account'].search([('id','=',data['from']['account_id'])])
		company_id = data['from']['company_id']
		company_ids = data['from']['company_ids']
		company_id_logo = self.env.user.company_id.logo

		domain = []
		if len(company_ids) == 1:
			company_where_clause = " and l.company_id = " + str(company_id)
			domain.append(('code','=like',(account_id.code + '%')))
			domain.append(('company_id','=',company_id))
		else:
			company_where_clause = " and l.company_id in " + str( tuple(company_ids))
			domain.append(('code','=like',(account_id.code + '%')))
			domain.append(('company_id','in',company_ids))

		account_list = []
		for account in self.env['account.account'].sudo().search(domain):
			if account not in account_list and account != account_id:
				account_list.append(account)

		count = 1
		docs = []
		line = []
		temp_docs = []
		temp_line = []
		domain = []
		total = 0.00
		for account in account_list:
			state_lines = []
			amount = 0
			self._cr.execute( "select COALESCE(sum(COALESCE( debit, 0 )), 0 ) debit, COALESCE(sum(COALESCE( credit, 0 )), 0) credit  from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '"+ str(account.code+'%') +"' and " + " l.date <= '" + str(date_to) + "' " + company_where_clause )
			state_balances = self.env.cr.fetchall()
			debit = state_balances[0][0]
			credit = state_balances[0][1]

			if account.code[0] in ['1','4']:
				amount = credit - debit
			elif account.code[0] in ['2','3']:
				amount = debit - credit


			if amount != 0.00:
				if account.code not in [a['code'] for a in docs]:
					docs.append({
						'count': count,
						'id': account.id,
						'account_name':account.name,
						'is_group': account.is_group,
						'amount':amount,
						'code': account.code,
						})
				if account.code not in [a['code'] for a in line]:
					line.append({
						'count': count,
						'account_name':account.name,
						'parent_id': account.parent_id.id,
						'is_group': account.is_group,
						'amount':amount,
						'code': account.code,
						})
					count += 1

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs' : docs,
			'line' : line,
			'clarification_number':clarification_number,
			'account':account_id.name,
			'company_id_logo': company_id_logo,
			'total':total,
		}


		