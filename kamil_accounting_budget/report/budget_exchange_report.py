# -*- coding:utf-8 -*-
from odoo import models, fields, api


class BudgetExchangeReport(models.AbstractModel):
	_name = 'report.kamil_accounting_budget.exchange_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']

		domain = []         
		if date_from:
			domain.append(('date','<=',date_from))
		if date_to:
			domain.append(('date','>=',date_to))
		
		docs = []	
		budget = self.env['crossovered.budget.lines'].search(domain)
		for line in budget:
			docs.append({
					'analytic_account_id':line.analytic_account_id,
					'reserved_value':line.reserved_value,
					'practical_amount':line.practical_amount,
					'remaining_value':line.remaining_value,
					'percentage':line.percentage,
					})
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to, 
		}


		