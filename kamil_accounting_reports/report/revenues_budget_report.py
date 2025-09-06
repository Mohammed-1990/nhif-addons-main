
# -*- coding:utf-8 -*-
from odoo import models, fields, api


class RevenuesBudgetReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.revenues_budget_template'


	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		budget_ids = data['from']['budget_ids']
		budget_item_ids = data['from']['budget_item_ids']
		company_id_logo = self.env.user.company_id.logo
		domain = [('revenues_budget_id','!=',False)]

		if date_from:
			domain.append(('date_from','<=',date_from))
		if date_to:
			domain.append(('date_to','>=',date_to))
		if budget_ids:
			domain.append(('revenues_budget_id','in',budget_ids))
		if budget_item_ids:
			domain.append(('analytic_account_id','in',budget_item_ids))


		docs = []	
		budget = self.env['crossovered.budget.lines'].search(domain)
		for line in budget:
			docs.append({
					'item':line.analytic_account_id.name,
					'planned_amount':line.planned_amount,
					'practical_amount':line.practical_amount,
					'remaining_value':line.remaining_value,
					'percentage':(line.practical_amount / line.remaining_value)* 100 
					})
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'company_id_logo': company_id_logo,
			'date_from': date_from,
			'date_to' : date_to, 
		}


		