# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class DetailedExpensesSynthesisReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.general_journal_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		company_id_logo = self.env.user.company_id.logo

		company_id = str(self.env.user.company_id.id)
		self._cr.execute(" select distinct account_id from account_move_line l inner join account_move m on m.id = l.move_id where m.date >= '"+ date_from +"' and m.date <= '"+ date_to +"' and m.company_id ='"+ company_id +"' ")

		move_line_accounts = self.env.cr.fetchall()

		group_accounts = []
		for account in move_line_accounts:
			for parent in self.env['account.account'].search([('id','parent_of',account),('is_group','=','group')]):
				if parent.code[0] == '3':
					if len(parent.code) == 3 and parent not in group_accounts:
						group_accounts.append(parent)
				elif len(parent.code) == 2 and parent not in group_accounts:
					group_accounts.append(parent)

		docs = []
		count = 1
		for move in self.env['account.move'].search([('date','>=',date_from),('date','<=',date_to)]):
			tot_row_debit = 0.00
			tot_row_credit = 0.00
			move_data = []
			for account in group_accounts:
				debit = 0.00 
				credit = 0.00
				for line in move.line_ids:
					if account.id in self.env['account.account'].search([('id','parent_of',line.account_id.id),('is_group','=','group')])._ids:
						debit = debit + line.debit
						credit = credit + line.credit
				
				tot_row_debit = tot_row_debit + debit
				tot_row_credit = tot_row_credit + credit
				move_data.append({'debit':debit,
					'credit':credit})
			move_data.append({'debit':tot_row_debit,
					'credit':tot_row_credit})

			docs.append({
				'count':count,
				'date':move.date,
				'ref':move.ref,
				'document_number':move.document_number,
				'move_data':move_data,
				})
			count += 1
		total_cols = []
		for col in range(0,len(group_accounts)+1):
			tot_debit = 0.00
			tot_credit = 0.00
			for doc in docs:
				data = doc['move_data'][col]
				tot_debit += data['debit']  
				tot_credit += data['credit']  
			total_cols.append({'debit':tot_debit,
				'credit':tot_credit})
			col += 1

		return {
			'date_from': date_from,
			'date_to' : date_to, 
			'docs' : docs,
			'company_id_logo': company_id_logo,
			'group_accounts':group_accounts,
			'total_cols':total_cols
		}

