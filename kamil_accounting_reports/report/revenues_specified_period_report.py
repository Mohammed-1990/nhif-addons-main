
# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta



class Account(models.Model):
	_inherit = 'account.account'

	is_inventory_account = fields.Boolean(string='Is Inventory Account')

class RevenuesSpecifiedPeriodReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.revenues_period_template'


	def get_accounting_format(self, number):
		if number < 0:
			number = '(' + str('{:,.2f}'.format( abs(number) ) ) + ')'
		else:
			number = str('{:,.2f}'.format( abs(number) ) )
		return number



	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		company_id_logo = self.env.user.company_id.logo

		company_ids = data['from']['company_ids']
		selected_company_ids = data['from']['selected_company_ids']

		selected_company_names = []
		for company_id in self.env['res.company'].search([('id','in', selected_company_ids)]):
			selected_company_names.append( company_id.short_name or company_id.name )


		account_id = data['from']['account_id']
		account_id = self.env['account.account'].sudo().search([('id','=',account_id)])

		###########################################


		all_accounts = []
		account_codes = []
		for account in self.env['account.account'].sudo().search([('is_group','=','sub_account'),('code','=ilike', str(account_id.code) + '%'),('company_id','in',company_ids)]):
			if account.code not in account_codes:
				account_codes.append( account.code )
				all_accounts.append( account )
		
		data_rows = []

		total_annual_budget_value = total_estimated_budget_value = total_actual_value = total_remaining_value = total_percentage = 0

		for account in all_accounts:
			row = {}
			row['account_id'] = account.id
			row['account_name'] = str(account.code) + ' ' +str(account.name)
			
			account_annual_budget_value = account_estimated_budget_value = account_actual_value = account_remaining_value = account_percentage = 0
			branches_rows = []
			for company_id in company_ids:
				
				annual_budget_value = estimated_budget_value = actual_value = remaining_value = percentage = 0

				account_id = self.env['account.account'].sudo().search([('code','=',account.code),('company_id','=',company_id)])
				if account_id:
					branch_row = {}
					branch_row['account_id'] = account.id
					branch_id = self.env['res.company'].sudo().search([('id','=',company_id)])[0]

					branch_row['branch_name'] = branch_id.short_name or  branch_id.name
					branch_row['account_name'] = str(account_id.code) + ' ' + str(account_id.name) 

					found = False
					for budget in self.env['crossovered.budget'].sudo().search([('date_from','<=',date_from),('date_to','>=',date_to),('company_id','=',company_id)]):
						for expenses_line in budget.revenues_line_ids:
							for budget_line in expenses_line.general_budget_id.accounts_value_ids:
								if budget_line.account_id == account_id:
									found = True
									if budget_line.approved_value > 0:
										annual_budget_value = budget_line.approved_value

					if found :
						date1 = datetime.strptime(date_from, "%Y-%m-%d")
						date2 = datetime.strptime(date_to, "%Y-%m-%d")
						days = ((date2 - date1).days + 1)
						
						months = days / 30
						if months < 1:
							months = 1
						months = int(months)

						if annual_budget_value > 0:
							estimated_budget_value = (annual_budget_value / 12) * months			

					branch_row['annual_budget_value'] = self.get_accounting_format(annual_budget_value) 
					branch_row['estimated_budget_value'] = self.get_accounting_format(estimated_budget_value)

					account_annual_budget_value += annual_budget_value
					account_estimated_budget_value += estimated_budget_value

					# self._cr.execute("select sum(l.amount) from ratification_line l inner join ratification_ratification r on r.id = l.ratification_id  where l.account_id=" + str(account.id) + " AND r.date >= '" + str(date_from) + "'  AND r.date <=  '" + str(date_to) +  "' AND r.state in ('payment_created','payment_confirmed','paid') " )
					self._cr.execute("select sum(COALESCE( credit, 0 ) ) - sum(COALESCE( debit, 0 ) )  from account_move_line where account_id="  + str(account_id.id) + " AND date >= '" + str(date_from) + "'  AND date <=  '" + str(date_to) +  "' and company_id = " + str(company_id) )

					actual_value = self.env.cr.fetchone()[0] or 0.0
					if account_id.is_inventory_account:
						if actual_value != 0:
							actual_value = actual_value * -1

					branch_row['actual_value'] = self.get_accounting_format(actual_value)
					account_actual_value += actual_value

					if estimated_budget_value > 0:
						remaining_value = estimated_budget_value - abs(actual_value)

					account_remaining_value += remaining_value
					branch_row['remaining_value'] = self.get_accounting_format(remaining_value)

					if actual_value > 0 and annual_budget_value > 0:
						percentage = actual_value / annual_budget_value * 100

					account_percentage += percentage
					branch_row['percentage'] = self.get_accounting_format(percentage)
					branches_rows.append( branch_row )
				


			row['annual_budget_value'] = self.get_accounting_format(account_annual_budget_value)
			row['estimated_budget_value'] = self.get_accounting_format(account_estimated_budget_value)
			row['actual_value'] = self.get_accounting_format(account_actual_value)
			row['remaining_value'] = self.get_accounting_format(account_remaining_value)
			row['percentage'] = self.get_accounting_format(account_percentage)
			row['branches_rows'] = branches_rows
			data_rows.append(row)

			total_annual_budget_value += account_annual_budget_value
			total_estimated_budget_value += account_estimated_budget_value
			total_actual_value += account_actual_value
			total_remaining_value += account_remaining_value
			# total_percentage += account_percentage
			if total_actual_value > 0 and total_annual_budget_value > 0:
				total_percentage = total_actual_value / total_annual_budget_value * 100





		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			

			'date_from': date_from,
			'date_to' : date_to, 
			
			'selected_company_names':selected_company_names,
			
			'data_rows' : data_rows,
			'company_id_logo': company_id_logo,

			'total_annual_budget_value' : self.get_accounting_format(total_annual_budget_value),
			'total_estimated_budget_value' : self.get_accounting_format(total_estimated_budget_value),
			'total_actual_value' : self.get_accounting_format(total_actual_value),
			'total_remaining_value' : self.get_accounting_format(total_remaining_value),
			'total_percentage' : self.get_accounting_format(total_percentage),			
		}


		