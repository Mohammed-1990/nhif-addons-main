
# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class CompareExpensesCompaniesReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.compare_exp_comp_template'

	def get_accounting_format(self, number):
		if number < 0:
			number = '(' + str('{:,.2f}'.format( abs(number) ) ) + ')'
		else:
			number = str('{:,.2f}'.format( abs(number) ) )
		return number

	@api.model
	def _get_report_values(self, docids, data=None):
		date_from1 = data['from']['date_from1']
		date_to1 = data['from']['date_to1']
		date_from2 = data['from']['date_from2']
		date_to2 = data['from']['date_to2']
		company_id_logo = self.env.user.company_id.logo
		

		docs = []
		total_budget_value1 = total_budget_value2 = total_actual1 = total_actual2 = 0

		for company_id in self.env['res.company'].sudo().search([]):

			budget_value1 = budget_value2 = estimated_expense1 = estimated_expense2 = actual_expense1 = actual_expense2  = percentege1 = percentege2 = 0.0

			found1 = found2 = False
			
			for budget in self.env['crossovered.budget'].sudo().search([('date_from','<=',date_from1 ),('date_to','>=', date_to1 ),('company_id','=',company_id.id)]):
				accounts_list = []
				for expenses_line in budget.expenses_line_ids:
					for budget_line in expenses_line.general_budget_id.accounts_value_ids:
						if budget_line.account_id.id not in accounts_list and budget_line.approved_value > 0:
							accounts_list.append( budget_line.account_id.id )
							found1 = True
							budget_value1 += budget_line.approved_value

			
			date1 = datetime.strptime(date_from1, "%Y-%m-%d")
			date2 = datetime.strptime(date_to1, "%Y-%m-%d")
			days1 = ((date2 - date1).days + 1)
			months1 = days1 / 30
			if months1 < 1:
				months1 = 1

			if budget_value1 > 0:
				estimated_expense1 = (budget_value1 / 12) * months1	
				total_budget_value1 += estimated_expense1

			self._cr.execute("select sum( coalesce(l.debit,0) ) - sum( coalesce(l.credit, 0) ) from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '2%' and l.date between '" + str(date_from1) + "' and '" + str(date_to1) + "' and l.company_id = " + str(company_id.id) )

			actual_expense1 = self.env.cr.fetchone()[0] or 0.0
			total_actual1 += actual_expense1

			if estimated_expense1 > 0:
				percentege1 = actual_expense1 / estimated_expense1 * 100
				




			for budget in self.env['crossovered.budget'].sudo().search([('date_from','<=',date_from2 ),('date_to','>=', date_to2 ),('company_id','=',company_id.id)]):
				accounts_list = []
				for expenses_line in budget.expenses_line_ids:
					for budget_line in expenses_line.general_budget_id.accounts_value_ids:
						if budget_line.account_id.id not in accounts_list and budget_line.approved_value > 0:
							accounts_list.append( budget_line.account_id.id )
							found2 = True
							budget_value2 += budget_line.approved_value
			

			date3 = datetime.strptime(date_from2, "%Y-%m-%d")
			date4 = datetime.strptime(date_to2, "%Y-%m-%d")
			days2 = ((date3 - date4).days + 1)
			
			months2 = days2 / 30
			if months2 < 1:
				months2 = 1

			if budget_value2 > 0:
				estimated_expense2 = (budget_value2 / 12) * months2	
				total_budget_value2 += estimated_expense2
				
			self._cr.execute("select sum( coalesce(l.debit,0) ) - sum( coalesce(l.credit, 0) ) from account_move_line l inner join account_account a on l.account_id = a.id where a.code ilike '2%' and l.date between '" + str(date_from2) + "' and '" + str(date_to2) + "' and l.company_id = " + str(company_id.id) )

			actual_expense2 = self.env.cr.fetchone()[0] or 0.0
			total_actual2 += actual_expense2

			if estimated_expense2 > 0:
				percentege2 = actual_expense2 / estimated_expense2 * 100
				

			if budget_value1 or actual_expense1 or budget_value2 or actual_expense2:
				docs.append({
					'company':company_id.short_name or company_id.name,
					'planned_amount1': self.get_accounting_format(estimated_expense1),
					'practical_amount1': self.get_accounting_format(actual_expense1),
					'percentege1':self.get_accounting_format(percentege1),
					'planned_amount2':self.get_accounting_format(estimated_expense2),
					'practical_amount2': self.get_accounting_format(actual_expense2),
					'percentege2':self.get_accounting_format(percentege2),
					'compare_percentage':self.get_accounting_format(percentege1 - percentege2),
					})

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			
			'date_from1': date_from1,
			'date_to1' : date_to1, 
			'date_from2': date_from2,
			'date_to2' : date_to2, 

			'total_budget_value1' : self.get_accounting_format(total_budget_value1),
			'total_budget_value2' : self.get_accounting_format(total_budget_value2),
			'total_actual1' : self.get_accounting_format(total_actual1),
			'total_actual2' : self.get_accounting_format(total_actual2),
			'company_id_logo': company_id_logo,
		}


		