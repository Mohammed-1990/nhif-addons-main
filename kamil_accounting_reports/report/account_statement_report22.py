
# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime


class AccountStatementReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.statement_template'


	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		revenue_account_id = data['from']['revenue_account_id']
		code = data['from']['code']
		partner_id = data['from']['partner_id']

		account_type = ''


		type = data['from']['type']

		for account in self.env['account.account'].search([('id','=',int(revenue_account_id))]):
	
			print('account[:1] = ', account.code[:1])			

			if account.code[:1] == '1':
				account_type = 'revenues'
			if account.code[:1] == '2':
				account_type = 'expenses'
			if account.code[:1] == '3':
				account_type = 'assets'
			if account.code[:1] == '4':
				account_type = 'liabilities'


		domain = []
		if date_from:
			domain.append(('date_maturity','>=',date_from))
		if date_to:
			domain.append(('date_maturity','<=',date_to))
		if partner_id:
			domain.append(('partner_id','=',partner_id))
		if revenue_account_id:
			domain.append(('account_id','=',revenue_account_id))

		docs = []	

		accounts = self.env['account.account'].search([('id','=',revenue_account_id)])
		if type == 'account_statment':
			vals = []
			planned_value = net_term = credit = debit =  0.0
			
			account_move_line = self.env['account.move.line']
			budget = self.env['crossovered.budget'].search([('state','=','validate')], limit=1)
			
			account_move = account_move_line.search(domain)

			code = int(code[:1])

			for move in account_move:
				if code == 1:
					for rec in budget.revenues_line_ids:
						for line in rec.general_budget_id.accounts_value_ids:
							if line.account_id.id == revenue_account_id:
								planned_value += line.planned_value
					credit += move.credit
					debit += move.debit
				if code == 2:
					for rec in budget.expenses_line_ids:
						for line in rec.general_budget_id.accounts_value_ids:
							if line.account_id.id == revenue_account_id:
								planned_value += line.planned_value
					credit += move.credit
					debit += move.debit
					# net_term = debit - credit
				if code == 3 or code == 4:
					date = fields.Date.to_string(datetime(fields.Date.today().year,1,1))
					self._cr.execute("select sum(debit)-sum(credit) from account_move_line where account_id="  + str(revenue_account_id) + " AND date >= '" + str(date) + "'    AND date <=  '" + str(date_from) +  "'  " )
					planned_value = abs(self.env.cr.fetchone()[0] or 0.0)
					credit += move.credit
					debit += move.debit

					# net_term = debit - credit
				# credit += move.credit
				# debit += move.debit
				vals.append({
						'name':move.account_id.code + ' ' + move.account_id.name,
						'date':move.date,
						'ref':move.move_id.document_number or move.name or move.move_id.name,
						'debit':move.debit,
						'credit':move.credit,
						'description':move.name or move.move_id.name
					})

##################################################################

			if code == 1:
				planned_value = 0
				for rec in budget.revenues_line_ids:
					for line in rec.general_budget_id.accounts_value_ids:
						if line.account_id.id == revenue_account_id:
							planned_value += line.planned_value
				vals_line = []
				credit = 0 
				credit = 0
				for move in account_move:
					credit += move.credit
					debit += move.debit
					vals_line.append({
						'name':move.account_id.code + ' ' + move.account_id.name,
						'date':move.date,
						'ref':move.move_id.document_number or move.name or move.move_id.name,
						'debit':debit,
						'credit':credit,
						'description':move.name or move.move_id.name
					})
				vals = vals_line
###################################################
			


##################################################################

			if code == 2:
				planned_value = 0
				for rec in budget.expenses_line_ids:
					for line in rec.general_budget_id.accounts_value_ids:
						if line.account_id.id == revenue_account_id:
							planned_value += line.approved_value
				vals_line = []
				credit = 0 
				credit = 0
				for move in account_move:
					credit += move.credit
					debit += move.debit
					vals_line.append({
						'name':move.account_id.code + ' ' + move.account_id.name,
						'date':move.date,
						'ref':move.move_id.document_number or move.name or move.move_id.name,
						'debit':debit,
						'credit':credit,
						'description':move.name or move.move_id.name
					})
				vals = vals_line
###################################################
			if code in [3,4]:
				date = fields.Date.to_string(datetime(fields.Date.today().year,1,1))
				self._cr.execute("select sum(debit)-sum(credit) from account_move_line where account_id="  + str(revenue_account_id) + " AND date >= '" + str(date) + "'    AND date <=  '" + str(date_from) +  "'  " )
				planned_value = abs(self.env.cr.fetchone()[0] or 0.0)
				



			if code == 1 or code == 4: 
				net_term = credit - debit
			else:
				net_term = debit - credit
			name = ''
			if partner_id:
				name = self.env['res.partner'].search([('id','=',partner_id)]).name

			docs.append({
				'account_name':accounts.name,
				'planned_value':planned_value,
				'partner':name,
				'vals': vals,
				'net_term':net_term,
				'balance' : planned_value + net_term, 
			})
		else:
			account_move_line = self.env['account.move.line']
			code = int(accounts.code[:1])
			group_list = []
			account2 = self.env['account.account'].search([('code','=like',(accounts.code + '%')),('id','!=',accounts.id)])
			for account in account2: 
				vals= []	
				credit = debit = balance =  0.0

				for line in account_move_line.search([('account_id.id','=',account.id)]):
					
					debit += line.debit
					credit += line.credit

				if code == 1 or code == 4:
					balance = credit - debit
				else:
					balance = debit - credit
				
				if balance:

					vals.append({
						'accounts_code' : account.parent_budget_item_id.code, 
						'account_name':  account.name,
						'debit':debit,
						'credit':credit,
						'balance':balance
					})

				if account.parent_budget_item_id.name not in [v['group_name'] for v in group_list]:


					group_list.append({'group_name': account.parent_budget_item_id.name,
					'vals':vals})
				else:
				
					for x in group_list:
						if x['group_name'] ==  account.parent_budget_item_id.name and balance:
							x['vals'].append({
								'accounts_code' : account.parent_budget_item_id.code, 
								'account_name': account.name,
								'debit':debit,
								'credit':credit,
								'balance':balance
							})

			group_list2 = []
			for line in group_list:
				balance = sum([v['balance'] for v in line['vals']])
				if balance:
					group_list2.append(line)
				

			docs.append({
				'group_name': accounts.name,
				'group_list':group_list2,

			})


		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to, 
			'type':type,
			'account_type' : account_type,
		}


		