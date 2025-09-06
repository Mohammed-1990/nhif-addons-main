
# -*- coding:utf-8 -*-
from odoo import models, fields, api


class AccountStatementReport(models.AbstractModel):
	_name = 'report.kamil_accounting_revenues_collection.statement_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		revenue_account_id = data['from']['revenue_account_id']
		# estimated_collection = data['from']['budget_ids']
		domain = []

		if date_from:
			domain.append(('date','>=',date_from))
		if date_to:
			domain.append(('date','<=',date_to))
		if revenue_account_id:
			domain.append(('account_id','in',revenue_account_id))
		# if budget_ids:
		# 	budget = self.env['collection.collection.line'].search([('analytic_account_id','in',budget_ids)])
		# 	domain.append(('line_ids','in',budget.ids))


		docs = []	
		account_statement = self.env['collection.collection'].search(domain)
		for line in account_statement:
			debit = ''
			if line.e_15_no:
				debit = line.collector.account_id.name
			else:
				debit = line.journal_id.default_debit_account_id.name
			docs.append({
					'date':line.date,
					'ref':line.ref,
					'debit':debit,
					'credit':debit,
					'description':line.name
					})
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to, 
		}


		