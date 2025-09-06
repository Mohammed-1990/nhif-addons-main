# -*- coding:utf-8 -*-
from odoo import models, fields, api


class BudgetMonthReport(models.AbstractModel):
	_name = 'report.kamil_accounting_budget.budget_month_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		budget_ids = data['from']['budget_ids']

		domain = []

		if date_from:
			domain.append(('date','<=',date_from))
		if date_to:
			domain.append(('date','>=',date_to))
		if budget_ids:
			budget = self.env['crossovered.budget.lines'].search([('analytic_account_id','in',budget_ids)])
			domain.append(('line_ids','in',budget.ids))
		
		docs = []	
		budget = self.env['crossovered.budget.lines'].search(domain)
		for line in budget:
			docs.append({
					'analytic_account_id':line.analytic_account_id.analytic_account_id,
					'planned_amount':line.analytic_account_id.planned_amount,
					'month':line.analytic_account_id.remaining_value,
					'percentage':line.analytic_account_id.percentage
					})
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to, 
		}


		