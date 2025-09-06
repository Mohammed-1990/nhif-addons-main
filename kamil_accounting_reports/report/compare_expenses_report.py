
# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class CompareExpensesReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.compare_expenses_template'


	@api.model
	def _get_report_values(self, docids, data=None):
		date_from1 = data['from']['date_from1']
		date_to1 = data['from']['date_to1']
		date_from2 = data['from']['date_from2']
		date_to2 = data['from']['date_to2']
		budget_item_ids = data['from']['budget_item_ids']
		revenue_account_ids = data['from']['budget_item_ids']
		company_id_logo = self.env.user.company_id.logo


		budget_id = data['from']['budget_id']
		budget_id = self.env['crossovered.budget'].search([('id','=',budget_id)])

		account_id = data['from']['account_id']
		account_id = self.env['account.account'].search([('id','=',account_id)])

		all_accounts = self.env['account.account'].search([('code','=ilike', str(account_id.code) + '%'),('is_group','=','sub_account')])
	
		###########################################
	
		docs = []
		total_expenses1 = total_expenses2 = 0

		for account in all_accounts:
			
			budget_value = estimated_expense1 = estimated_expense2 = actual_expense1 = actual_expense2 = remaing_value = percentege1 = percentege2 = 0.0
			found = False

			for budget in budget_id:
				for expenses_line in budget.expenses_line_ids:
					for budget_line in expenses_line.general_budget_id.accounts_value_ids:
						if budget_line.account_id == account:
							found = True
							if budget_line.approved_value > 0:
								budget_value = budget_line.approved_value

			if found :
				
				date1 = datetime.strptime(date_from1, "%Y-%m-%d")
				date2 = datetime.strptime(date_to1, "%Y-%m-%d")
				days1 = ((date2 - date1).days + 1)
				months1 = days1 / 30
				if months1 < 1:
					months1 = 1


				date3 = datetime.strptime(date_from2, "%Y-%m-%d")
				date4 = datetime.strptime(date_to2, "%Y-%m-%d")
				days2 = ((date3 - date4).days + 1)
				
				months2 = days2 / 30
				if months2 < 1:
					months2 = 1


				estimated_expense1 = estimated_expense2 = 0
				remaing_value = 0

				if budget_value > 0:
					estimated_expense1 = (budget_value / 12) * months1				
					estimated_expense2 = (budget_value / 12) * months2				
					 
				self._cr.execute("select sum(COALESCE( debit, 0 ) ) - sum(COALESCE( credit, 0 ) )  from account_move_line where account_id="  + str(account.id) + " AND date >= '" + str(date_from1) + "'  AND date <=  '" + str(date_to1) +  "'  " )

				actual_expense1 = self.env.cr.fetchone()[0] or 0.0


				self._cr.execute("select sum(COALESCE( debit, 0 ) ) - sum(COALESCE( credit, 0 ) )  from account_move_line where account_id="  + str(account.id) + " AND date >= '" + str(date_from2) + "'  AND date <=  '" + str(date_to2) +  "'  " )

				actual_expense2 = self.env.cr.fetchone()[0] or 0.0

				if account.is_inventory_account:
					if actual_expense1 != 0:
						actual_expense1 = actual_expense1 * -1
					if actual_expense2 != 0:
						actual_expense2 = actual_expense2 * -1

				# str_remaing_value = '0'

				# if budget_value > 0:
				# 	remaing_value = budget_value - actual_expense  

				# 	if remaing_value < 0:
				# 		str_remaing_value = '(' + str('{:,.2f}'.format( abs(remaing_value) ) ) + ')'
				# 	else:
				# 		str_remaing_value = str('{:,.2f}'.format( abs(remaing_value) ) )

				percentege1 =percentege2 = 0
				if actual_expense1 > 0 and estimated_expense1 > 0:
					percentege1 = actual_expense1 / estimated_expense1 * 100
				str_actual_expense1 = '0'
				if actual_expense1 < 0:
					str_actual_expense1 = '(' + str('{:,.2f}'.format( abs(actual_expense1) ) ) + ')'
				else:
					str_actual_expense1 = str('{:,.2f}'.format( abs(actual_expense1) ) )



				if actual_expense2 > 0 and estimated_expense2 > 0:
					percentege2 = actual_expense2 / estimated_expense2 * 100
				str_actual_expense2 = '0'
				if actual_expense2 < 0:
					str_actual_expense2 = '(' + str('{:,.2f}'.format( abs(actual_expense2) ) ) + ')'
				else:
					str_actual_expense2 = str('{:,.2f}'.format( abs(actual_expense2) ) )

				total_expenses1 = total_expenses1 + actual_expense1
				total_expenses2 = total_expenses2 + actual_expense2

				docs.append({
					'item':account.name,
					'planned_amount1':estimated_expense1,
					'practical_amount1':actual_expense1,
					'str_actual_expense1' : str_actual_expense1,
					'remaining_value1':percentege1,
					'planned_amount2':estimated_expense2,
					'practical_amount2':actual_expense2,
					'str_actual_expense2' : str_actual_expense2,
					'remaining_value2':percentege2,
					'compare_percentage':percentege1 - percentege2,
					'percentege' : percentege1,
					'percentege2' : percentege2,
					})

	
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from1,
			'date_to' : date_to1, 
			'date_from2': date_from2,
			'date_to2' : date_to2,
			'company_id_logo': company_id_logo,
		}


		