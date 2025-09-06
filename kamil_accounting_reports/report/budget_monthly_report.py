# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar

class BudgetMonthlyReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.budget_monthly_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		group_id = data['from']['group_id']
		account_id = data['from']['account_id']
		budget_id = data['from']['budget_id']
		company_id_logo = self.env.user.company_id.logo


		account = self.env['account.account'].search([('id','=',account_id)])[0]
		
		all_accounts = self.env['account.account'].search([('code','=ilike', str(account.code + '%') ),('is_group','=','sub_account')])

		budget =  self.env['crossovered.budget'].search([('id','=',budget_id)])[0]

		docs = []

		total_expenses = 0
		str_total_expenses = '0'

		if account.code[:1] == '1':
			the_type = 'revenues'
		else:
			the_type = 'expenses'

		for account in all_accounts:
			budget_value = actual_expense = remaing_value = percentege = 0.0
			found = False

			for budget in budget:
				
				if the_type == 'revenues':
					the_budget_lines = budget.revenues_line_ids
				else:
					the_budget_lines = budget.expenses_line_ids

				for revenue_line in the_budget_lines:
					for budget_line in revenue_line.general_budget_id.accounts_value_ids:
						if budget_line.account_id == account:
							found = True
							if budget_line.approved_value > 0:
								budget_value = budget_line.approved_value

			if found:
				months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
				month_amount = []
				total = 0.0
				account_total = 0
				for month in months:
											
					start_date = datetime(int(budget.date_from.year), month, 1)
					end_date = start_date + relativedelta(day= calendar.monthrange(budget.date_from.year, month)[1] )

					if the_type == 'revenues':
						self._cr.execute("select sum(COALESCE( credit, 0 ) ) - sum(COALESCE( debit, 0 ) )  from account_move_line where account_id="  + str(account.id) + " AND date >= '" + str(start_date) + "'  AND date <=  '" + str(end_date) +  "'  " )
						actual_expense = self.env.cr.fetchone()[0] or 0.0
					else:
						self._cr.execute("select sum(COALESCE( debit, 0 ) ) - sum(COALESCE( credit, 0 ) )  from account_move_line where account_id="  + str(account.id) + " AND date >= '" + str(start_date) + "'  AND date <=  '" + str(end_date) +  "'  " )
						actual_expense = self.env.cr.fetchone()[0] or 0.0

					str_actual_expense = '0'
					if actual_expense < 0:
						str_actual_expense = '(' + str('{:,.2f}'.format( abs(actual_expense) ) ) + ')'
					else:
						str_actual_expense = str('{:,.2f}'.format( abs(actual_expense) ) )

					account_total = account_total + actual_expense

					month_amount.append({str(month): actual_expense})
				
				if budget_value > 0:
					rate = (account_total / budget_value) * 100
					remaining_value = budget_value - account_total
				else:
					rate = 0
					remaining_value = 0

				if budget_value > 0:
					docs.append({
						'item':account.name,
						'planned_amount':budget_value,
						'month_amount': month_amount,
						'total': account_total,
						'remaining_value':remaining_value,
						'exchange_rate': rate,
						})



		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to,
			'company_id_logo': company_id_logo,
			'budget_name' : budget.name,
		}


		