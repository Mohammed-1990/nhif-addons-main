
# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime



class ResCompany(models.AbstractModel):
	_inherit = 'res.company'
	account_opening_move_id = fields.Many2one('account.move')



class AccountStatementReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.statement_template'


	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		revenue_account_id = data['from']['revenue_account_id']
		code = data['from']['code']
		partner_id = data['from']['partner_id']
		is_group_by_partners = data['from']['is_group_by_partners']
		report_type = data['from']['report_type']
		company_id_logo = self.env.user.company_id.logo


		account_type = ''

		type = data['from']['type']

		for account in self.env['account.account'].search([('id','=',int(revenue_account_id))]):
	
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
			domain.append(('date','>=',date_from))
		if date_to:
			domain.append(('date','<=',date_to))

		docs = []	
		balance_type = ''

		# this is an old VPN connection i added before 

		accounts = self.env['account.account'].search([('id','=',revenue_account_id)])
		if type == 'account_statment':

			if is_group_by_partners:
				vals = []
				docs = []

				account_id = self.env['account.account'].search([('id','=',revenue_account_id)])

				self._cr.execute("SELECT DISTINCT partner_id FROM account_move_line WHERE partner_id is not null and company_id = " + str(self.env.user.company_id.id) + " and account_id  = " + str(revenue_account_id) + " "  )

				all_partners = self.env.cr.fetchall()
				all_partners_ids = []
				for partner in all_partners:
					all_partners_ids.append( partner[0] )


				total_total_debit = 0 
				total_total_credit = 0
				total_balance = 0
				total_opening_balance = 0
				
				for partner_id in all_partners_ids:
					
					partner_name = ''
					opening_balance = 0
					str_opening_balance = ''
					total_debit = 0
					total_credit = 0
					balance = 0
					str_balance = 0
					partner_ids = []

					partner_ids.append( partner_id )
					for partner in self.env['res.partner'].search([('id','=',partner_id)]):
						partner_name = partner.name
						if partner.parent_id:
							partner_ids.append( partner.parent_id.id )
							partner_name = partner_name + ', ' +  partner.parent_id.name

						for child in partner.child_ids:
							partner_ids.append( child.id )
							partner_name = partner_name + child.name

					if account.code[:1] in ('1','4') : 

						if len(partner_ids) == 1: 
							self._cr.execute("SELECT sum(COALESCE( credit, 0 ))-sum(COALESCE( debit, 0 )) from account_move_line where account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  AND partner_id = " + str(partner_id))
						else:
							self._cr.execute("SELECT sum(COALESCE( credit, 0 ))-sum(COALESCE( debit, 0 )) from account_move_line where account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  AND partner_id in " + str(tuple(partner_ids) )   )

						opening_balance = self.env.cr.fetchone()[0] or 0.0

					if account.code[:1] in ('2','3') : 

						if len(partner_ids) == 1: 
							self._cr.execute("SELECT sum(COALESCE( debit, 0 ))-sum(COALESCE( credit, 0 )) from account_move_line where account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  AND partner_id = " + str(partner_id))
						else:
							self._cr.execute("SELECT sum(COALESCE( debit, 0 ))-sum(COALESCE( credit, 0 )) from account_move_line where account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  AND partner_id in " + str(tuple(partner_ids) )   )

						opening_balance = self.env.cr.fetchone()[0] or 0.0

					if opening_balance < 0:
						str_opening_balance = '(' + str('{:,.2f}'.format( abs(opening_balance) ) ) + ')'
					else:
						str_opening_balance = str('{:,.2f}'.format( opening_balance ) )

					self._cr.execute("SELECT sum(COALESCE( debit, 0 )) from account_move_line where account_id="  + str(revenue_account_id) + " AND date >= '" + str(date_from) +  "'  AND date <= '" + date_to + "' AND partner_id = " + str(partner_id))
					total_debit = self.env.cr.fetchone()[0] or 0.0

					self._cr.execute("SELECT sum(COALESCE( credit, 0 )) from account_move_line where account_id="  + str(revenue_account_id) + " AND date >= '" + str(date_from) +  "'  AND date <= '" + date_to + "' AND partner_id = " + str(partner_id))
					total_credit = self.env.cr.fetchone()[0] or 0.0

					if account.code[:1] in ('1','4') : 
						balance = (total_credit + opening_balance) - total_debit
					if account.code[:1] in ('2','3') :
						balance = (total_debit + opening_balance) - total_credit

					if balance < 0:
						str_balance = '(' + str('{:,.2f}'.format( abs(balance) ) ) + ')'
					else:
						str_balance = str('{:,.2f}'.format( balance ) )

					total_opening_balance = total_opening_balance + opening_balance
					total_total_debit = total_total_debit + total_debit 
					total_total_credit = total_total_credit + total_credit
					total_balance = total_balance + balance

					vals.append({
						'partner_name': partner_name,
						'opening_balance':str_opening_balance,
						'total_debit': total_debit,
						'total_credit': total_credit,
						'balance': str_balance,
					})

				if total_balance < 0:
					total_balance = '(' + str('{:,.2f}'.format( abs(total_balance) ) ) + ')'
				else:
					total_balance = str('{:,.2f}'.format( total_balance ) )
				
				if total_total_credit < 0:
					total_total_credit = '(' + str('{:,.2f}'.format( abs(total_total_credit) ) ) + ')'
				else:
					total_total_credit = str('{:,.2f}'.format( total_total_credit ) )
				
				if total_total_debit < 0:
					total_total_debit = '(' + str('{:,.2f}'.format( abs(total_total_debit) ) ) + ')'
				else:
					total_total_debit = str('{:,.2f}'.format( total_total_debit ) )

				if total_opening_balance < 0:
					total_opening_balance = '(' + str('{:,.2f}'.format( abs(total_opening_balance) ) ) + ')'
				else:
					total_opening_balance = str('{:,.2f}'.format( total_opening_balance ) )

				docs.append({
					'account_name': account_id.name,
					'vals': vals,
					'total_total_debit' : total_total_debit,
					'total_total_credit' : total_total_credit,
					'total_balance' : total_balance,
					'total_opening_balance' : total_opening_balance,
				})

				return {
					'doc_ids': data['ids'],
					'doc_model': data['model'],
					'docs': docs,
					'date_from': date_from,
					'date_to' : date_to, 
					'type':type,
					'account_type' : account_type,
					'is_group_by_partners' : is_group_by_partners,
				}

			vals = []
			planned_value = net_term = credit = debit =  0.0
			
			account_move_line = self.env['account.move.line']
			budget = self.env['crossovered.budget'].search([('state','=','validate')], limit=1)
			if partner_id:

				partner_ids = []
				partner_ids.append( partner_id )
				for partner in self.env['res.partner'].search([('id','=',partner_id)]):
					if partner.parent_id:
						partner_ids.append( partner.parent_id.id )

					for child in partner.child_ids:
						partner_ids.append( child.id )

				account_move = account_move_line.search([('account_id','=',revenue_account_id),('date','>=',date_from),('date','<=',date_to),('partner_id','in',partner_ids)],order='date asc')
			else:
				account_move = account_move_line.search([('account_id','=',revenue_account_id),('date','>=',date_from),('date','<=',date_to)],order='date asc')

			code = int(code[:1])
			doc_type = 'قيد'
			the_move_ids = []
			for move in account_move:
				
				doc_type = 'قيد'
				
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
	
				if code == 3 or code == 4:
					date = fields.Date.to_string(datetime(fields.Date.today().year,1,1))
					
					if partner_id:
						partner_ids = []
						partner_ids.append( partner_id )
						for partner in self.env['res.partner'].search([('id','=',partner_id)]):
							if partner.parent_id:
								partner_ids.append( partner.parent_id.id )

							for child in partner.child_ids:
								partner_ids.append( child.id )
						if len(partner_ids) == 1: 
							self._cr.execute("select sum( COALESCE( debit, 0 ) )-sum( COALESCE( credit, 0 ) ) from account_move_line where account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  AND partner_id = " + str(partner_id))
						else:
							self._cr.execute("select sum(COALESCE( debit, 0 ))-sum(COALESCE( credit, 0 )) from account_move_line where account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  AND partner_id in " + str(tuple(partner_ids) )   )

					else:
						self._cr.execute("select sum(COALESCE( COALESCE( debit , 0 ) , 0 ))-sum( COALESCE( credit, 0 ) ) from account_move_line where account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  " )

					planned_value = abs(self.env.cr.fetchone()[0] or 0.0)
					credit += move.credit
					debit += move.debit

				doc_type = 'قيد'
				if move.move_id.ratification_payment_id:
					if move.move_id.ratification_payment_id.payment_type == 'Cheque':
						doc_type = 'شيك'
					if move.move_id.ratification_payment_id.payment_type == 'cash':
						doc_type = 'نقد'
					if move.move_id.ratification_payment_id.payment_type == 'bank_transfer':
						doc_type = 'تحويل بنكي'
					if move.move_id.ratification_payment_id.payment_type == 'counter_cheque':
						doc_type = 'شيك مصرفي'
				if move.move_id.collection_id:
					if move.move_id.collection_id.collection_type == 'Cheque':
						doc_type = 'شيك'
					if move.move_id.collection_id.collection_type == 'cash':
						doc_type = 'نقد'
					if move.move_id.collection_id.collection_type == 'bank_transfer':
						doc_type = 'تحويل بنكي'
					if move.move_id.collection_id.collection_type == 'counter_cheque':
						doc_type = 'شيك مصرفي'

				vals.append({
					'name':move.account_id.code + ' ' + move.account_id.name,
					'date':move.date,
					'ref':move.move_id.document_number or move.name or move.move_id.name,
					'debit':move.debit,
					'credit':move.credit,
					'description':move.name or move.move_id.name,
					'the_partner_name' : move.partner_id.name,
					'doc_type' : doc_type,
					'move_id' : move.move_id.id,
					'move_ref' : move.move_id.ref,
				})
				
				if move.move_id.id not in the_move_ids:
					the_move_ids.append( move.move_id.id )

			lines_list = []
			if report_type == 'group_by_account' and code == 4:		
				for line_id in the_move_ids:			
					move_debit = move_credit = 0
					name = description = date = ref = doc_type = ''

					for list_line in vals:
						if list_line['move_id'] == line_id:
							move_credit = move_credit + list_line['credit']
							move_debit = move_debit + list_line['debit']
							name = list_line['move_ref']
							description = list_line['move_ref']
							date = list_line['date']
							ref = list_line['ref']
							doc_type = list_line['doc_type']

					lines_list.append({
						'name' : name,
						'date' : date,
						'ref' : ref ,
						'debit' : move_debit,
						'credit': move_credit,
						'description' : description,
						'the_partner_name' : '',
						'doc_type' : doc_type,
					})
				vals = lines_list
			
			else:
				vals = vals

##################################################################
			opening_balance_type = ''
			the_move_ids = []
			if code == 1:
				planned_value = 0
				for rec in budget.revenues_line_ids:
					for line in rec.general_budget_id.accounts_value_ids:
						if line.account_id.id == revenue_account_id:
							planned_value += line.planned_value
				vals_line = []
				debit = 0 
				credit = 0
								
				for move in account_move:
					credit += move.credit
					debit += move.debit

					doc_type = 'قيد'
					if move.move_id.ratification_payment_id:
						if move.move_id.ratification_payment_id.payment_type == 'Cheque':
							doc_type = 'شيك'
						if move.move_id.ratification_payment_id.payment_type == 'cash':
							doc_type = 'نقد'
						if move.move_id.ratification_payment_id.payment_type == 'bank_transfer':
							doc_type = 'تحويل بنكي'
						if move.move_id.ratification_payment_id.payment_type == 'counter_cheque':
							doc_type = 'شيك مصرفي'
					if move.move_id.collection_id:
						if move.move_id.collection_id.collection_type == 'Cheque':
							doc_type = 'شيك'
						if move.move_id.collection_id.collection_type == 'cash':
							doc_type = 'نقد'
						if move.move_id.collection_id.collection_type == 'bank_transfer':
							doc_type = 'تحويل بنكي'
						if move.move_id.collection_id.collection_type == 'counter_cheque':
							doc_type = 'شيك مصرفي'

					vals_line.append({
						'name':move.account_id.code + ' ' + move.account_id.name,
						'date':move.date,
						'ref':move.move_id.document_number or move.name or move.move_id.name,
						'debit':move.debit,
						'credit':move.credit,
						'description':move.name or move.move_id.name,
						'the_partner_name' : move.partner_id.name,
						'doc_type' : doc_type,
						'move_id' : move.move_id.id,
						'move_ref' : move.move_id.ref,
					})
					if move.move_id.id not in the_move_ids:
						the_move_ids.append( move.move_id.id )

				lines_list = []
				if report_type == 'group_by_account':		
					for line_id in the_move_ids:			
						move_debit = move_credit = 0
						name = description = date = ref = doc_type = ''

						for list_line in vals_line:
							if list_line['move_id'] == line_id:
								move_credit = move_credit + list_line['credit']
								move_debit = move_debit + list_line['debit']
								name = list_line['move_ref']
								description = list_line['move_ref']
								date = list_line['date']
								ref = list_line['ref']
								doc_type = list_line['doc_type']

						lines_list.append({
							'name' : name,
							'date' : date,
							'ref' : ref ,
							'debit' : move_debit,
							'credit': move_credit,
							'description' : description,
							'the_partner_name' : '',
							'doc_type' : doc_type,
						})
					vals = lines_list
				
				else:
					vals = vals_line
###################################################
			


###############################################################
			the_move_ids = []
			if code == 2:
				planned_value = 0
				for rec in budget.expenses_line_ids:
					for line in rec.general_budget_id.accounts_value_ids:
						if line.account_id.id == revenue_account_id:
							planned_value += line.approved_value
				vals_line = []
				debit = 0 
				credit = 0
				for move in account_move:
					credit += move.credit
					debit += move.debit
			
					doc_type = 'قيد'
					if move.move_id.ratification_payment_id:
						if move.move_id.ratification_payment_id.payment_type == 'Cheque':
							doc_type = 'شيك'
						if move.move_id.ratification_payment_id.payment_type == 'cash':
							doc_type = 'نقد'
						if move.move_id.ratification_payment_id.payment_type == 'bank_transfer':
							doc_type = 'تحويل بنكي'
						if move.move_id.ratification_payment_id.payment_type == 'counter_cheque':
							doc_type = 'شيك مصرفي'
					if move.move_id.collection_id:
						if move.move_id.collection_id.collection_type == 'Cheque':
							doc_type = 'شيك'
						if move.move_id.collection_id.collection_type == 'cash':
							doc_type = 'نقد'
						if move.move_id.collection_id.collection_type == 'bank_transfer':
							doc_type = 'تحويل بنكي'
						if move.move_id.collection_id.collection_type == 'counter_cheque':
							doc_type = 'شيك مصرفي'

					vals_line.append({
						'name':move.account_id.code + ' ' + move.account_id.name,
						'date':move.date,
						'ref':move.move_id.document_number or move.name or move.move_id.name,
						'debit':move.debit,
						'credit':move.credit,
						'description':move.name or move.move_id.name,
						'the_partner_name' : move.partner_id.name,	
						'doc_type' : doc_type,
						'move_id' : move.move_id.id,
						'move_ref' : move.move_id.ref,
					})
					if move.move_id.id not in the_move_ids:
						the_move_ids.append( move.move_id.id )

				# vals = vals_line				
				lines_list = []
				if report_type == 'group_by_account':		
					for line_id in the_move_ids:			
						move_debit = move_credit = 0
						name = description = date = ref = doc_type = ''

						for list_line in vals_line:
							if list_line['move_id'] == line_id:
								move_credit = move_credit + list_line['credit']
								move_debit = move_debit + list_line['debit']
								name = list_line['move_ref']
								description = list_line['move_ref']
								date = list_line['date']
								ref = list_line['ref']
								doc_type = list_line['doc_type']
						lines_list.append({
							'name' : name,
							'date' : date,
							'ref' : ref ,
							'debit' : move_debit,
							'credit': move_credit,
							'description' : description,
							'the_partner_name' : '',
							'doc_type' : doc_type,
						})
					vals = lines_list
				else:
					vals = vals_line



###################################################

###############################################################
			the_move_ids = []
			if code == 3:
				planned_value = 0
				vals_line = []
				debit = 0 
				credit = 0
				for move in account_move:
					credit += move.credit
					debit += move.debit
	
					doc_type = 'قيد'
					if move.move_id.ratification_payment_id:
						if move.move_id.ratification_payment_id.payment_type == 'Cheque':
							doc_type = 'شيك'
						if move.move_id.ratification_payment_id.payment_type == 'cash':
							doc_type = 'نقد'
						if move.move_id.ratification_payment_id.payment_type == 'bank_transfer':
							doc_type = 'تحويل بنكي'
						if move.move_id.ratification_payment_id.payment_type == 'counter_cheque':
							doc_type = 'شيك مصرفي'
					if move.move_id.collection_id:
						if move.move_id.collection_id.collection_type == 'Cheque':
							doc_type = 'شيك'
						if move.move_id.collection_id.collection_type == 'cash':
							doc_type = 'نقد'
						if move.move_id.collection_id.collection_type == 'bank_transfer':
							doc_type = 'تحويل بنكي'
						if move.move_id.collection_id.collection_type == 'counter_cheque':
							doc_type = 'شيك مصرفي'
					vals_line.append({
						'name':move.account_id.code + ' ' + move.account_id.name,
						'date':move.date,
						'ref':move.move_id.document_number or move.name or move.move_id.name,
						'debit':move.debit,
						'credit':move.credit,
						'description':move.name or move.move_id.name,
						'the_partner_name' : move.partner_id.name,
						'doc_type' : doc_type,	
						'move_id' : move.move_id.id,
						'move_ref' : move.move_id.ref,
					})
					if move.move_id.id not in the_move_ids:
						the_move_ids.append( move.move_id.id )
					
				# vals = vals_line
				lines_list = []
				if report_type == 'group_by_account':		
					for line_id in the_move_ids:			
						move_debit = move_credit = 0
						name = description = date = ref = doc_type = ''

						for list_line in vals_line:
							if list_line['move_id'] == line_id:
								move_credit = move_credit + list_line['credit']
								move_debit = move_debit + list_line['debit']
								name = list_line['move_ref']
								description = list_line['move_ref']
								date = list_line['date']
								ref = list_line['ref']
								doc_type = list_line['doc_type']
						lines_list.append({
							'name' : name,
							'date' : date,
							'ref' : ref ,
							'debit' : move_debit,
							'credit': move_credit,
							'description' : description,
							'the_partner_name' : '',
							'doc_type' : doc_type,
						})
					vals = lines_list
				else:
					vals = vals_line



###################################################
			
			net_term_type = ''
			opening_balance_type = str( '{:,.2f}'.format( abs(planned_value) ) )
			
			if code == 1:

				net_term = credit - debit
				if net_term < 0:
					balance_type = 'مدين'
					net_term_type = '(' + str( '{:,.2f}'.format( abs(net_term) ) ) + ')'
				else:
					balance_type = 'دائن'
					net_term_type = str( '{:,.2f}'.format( abs(net_term) ) ) 


			if code == 2:
				net_term = debit - credit
				if net_term < 0:
					balance_type = 'دائن'
					net_term_type = '(' + str( '{:,.2f}'.format( abs(net_term) ) ) + ')'
				else:
					balance_type = 'مدين'
					net_term_type = str(  '{:,.2f}'.format( abs(net_term) )  ) 

			
			if code == 4: 

				if partner_id:

					partner_ids = []
					partner_ids.append( partner_id )
					for partner in self.env['res.partner'].search([('id','=',partner_id)]):
						if partner.parent_id:
							partner_ids.append( partner.parent_id.id )
						for child in partner.child_ids:
							partner_ids.append( child.id )


					if len(partner_ids) == 1:
						self._cr.execute("select sum(COALESCE( credit, 0 ))-sum( COALESCE( debit , 0 ) ) from account_move_line where partner_id = " + str(partner_id) + " AND account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  " )
					else:
						self._cr.execute("select sum( COALESCE( credit, 0 ) )-sum( COALESCE( debit, 0 ) ) from account_move_line where partner_id in " + str(tuple(partner_ids) ) + " AND account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  " )
				else:
					self._cr.execute("select sum( COALESCE( credit, 0 ) )-sum( COALESCE( debit , 0 ) ) from account_move_line where account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  " )
				planned_value = self.env.cr.fetchone()[0] or 0.0


				if planned_value < 0:
					debit = debit + abs(planned_value)
					opening_balance_type = '(' + str('{:,.2f}'.format( abs(planned_value) ) ) + ')'
				else:
					credit = credit + abs(planned_value)
					opening_balance_type = str('{:,.2f}'.format( abs(planned_value) ) )
				
				net_term = credit - debit
				if net_term < 0:
					balance_type = 'مدين'
					net_term_type = '(' + str(  '{:,.2f}'.format( abs(net_term) ) ) + ')'
				else:
					balance_type = 'دائن'
					net_term_type = str( '{:,.2f}'.format( abs(net_term) ) ) 



			elif code == 3 :
				

				if partner_id:

					partner_ids = []
					partner_ids.append( partner_id )
					for partner in self.env['res.partner'].search([('id','=',partner_id)]):
						if partner.parent_id:
							partner_ids.append( partner.parent_id.id )

						for child in partner.child_ids:
							partner_ids.append( child.id )
					if len(partner_ids) == 1:
						self._cr.execute("select sum( COALESCE( debit , 0 ) )-sum( COALESCE( credit, 0 ) ) from account_move_line where partner_id = " + str(partner_id) + " AND account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  " )
					else:
						self._cr.execute("select sum( COALESCE( debit, 0 ) )-sum( COALESCE( credit, 0 ) ) from account_move_line where partner_id in " + str(tuple(partner_ids) ) + " AND account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  " )
				else:
					self._cr.execute("select sum( COALESCE( debit , 0 ) )-sum( COALESCE( credit, 0 ) ) from account_move_line where account_id="  + str(revenue_account_id) + " AND date <  '" + str(date_from) +  "'  " )
				planned_value = self.env.cr.fetchone()[0] or 0.0


				if planned_value > 0:
					debit = debit + abs(planned_value)
					opening_balance_type = str('{:,.2f}'.format( abs(planned_value) ) ) 
				else:
					credit = credit + abs(planned_value)
					opening_balance_type = '(' + str('{:,.2f}'.format( abs(planned_value) ) ) + ')'
				
				net_term = debit - credit
				if net_term < 0:
					balance_type = 'دائن'
					net_term_type = '(' + str(   '{:,.2f}'.format( abs(net_term) ) ) + ')'
				else:
					balance_type = 'مدين'
					net_term_type = str( '{:,.2f}'.format( abs(net_term) ) ) 

				# net_term = debit - credit
	

				
			
			docs.append({
				'account_name':accounts.name,
				'planned_value': abs(planned_value),
				'vals': vals,
				'net_term':abs(net_term),
				'balance' : abs(net_term), 
				'balance_type' : balance_type,
				'net_term_type' :net_term_type,
				'opening_balance_type' : opening_balance_type,
				'doc_type' : doc_type,
				'report_type' : report_type,
			})
		else:
			the_opening_balance = 0

			account_move_line = self.env['account.move.line']
			code = int(accounts.code[:1])
			group_list = []
			account2 = self.env['account.account'].search([('code','=like',(accounts.code + '%')),('id','!=',accounts.id)])
			for account in account2: 
				vals= []	
				credit = debit = balance =  0.0

				if partner_id :

					partner_ids = []
					partner_ids.append( partner_id )
					for partner in self.env['res.partner'].search([('id','=',partner_id)]):
						if partner.parent_id:
							partner_ids.append( partner.parent_id.id )

						for child in partner.child_ids:
							partner_ids.append( child.id )

					lines = account_move_line.search([('account_id.id','=',account.id),('partner_id','in',partner_ids),('date','>=',date_from),('date','<=',date_to)])

				else:
					lines = account_move_line.search([('account_id.id','=',account.id),('date','>=',date_from),('date','<=',date_to)])

				for line in lines:					
					debit += line.debit
					credit += line.credit

				if code == 1 or code == 4:
					balance = credit - debit

					if partner_id:

						partner_ids = []
						partner_ids.append( partner_id )
						for partner in self.env['res.partner'].search([('id','=',partner_id)]):
							if partner.parent_id:
								partner_ids.append( partner.parent_id.id )

							for child in partner.child_ids:
								partner_ids.append( child.id )

						if len(partner_ids) == 1:
							self._cr.execute("select sum( COALESCE( credit, 0 ) )-sum( COALESCE( debit, 0 ) ) from account_move_line where partner_id = " + str(partner_id) + " AND account_id="  + str(account.id) + " AND date <  '" + str(date_from) +  "'  " )
						else:

							self._cr.execute("select sum( COALESCE(  credit, 0 ) )-sum( COALESCE( debit, 0 ) ) from account_move_line where partner_id in " + str(tuple(partner_ids) ) + " AND account_id="  + str(account.id) + " AND date <  '" + str(date_from) +  "'  " )

					else:
						self._cr.execute("select sum( COALESCE( credit, 0 ) )-sum( COALESCE( debit, 0 ) ) from account_move_line where account_id="  + str(account.id) + " AND date <  '" + str(date_from) +  "'  " )

					opening_balance = abs(self.env.cr.fetchone()[0] or 0.0)
					balance = balance + opening_balance

					the_opening_balance = opening_balance

				else:
					balance = debit - credit

					if partner_id:					
						partner_ids = []
						partner_ids.append( partner_id )
						for partner in self.env['res.partner'].search([('id','=',partner_id)]):
							if partner.parent_id:
								partner_ids.append( partner.parent_id.id )

							for child in partner.child_ids:
								partner_ids.append( child.id )
						if len(partner_ids) == 1:
							self._cr.execute("select sum( COALESCE( debit , 0 ) )-sum( COALESCE( credit, 0 ) ) from account_move_line where partner_id = " + str(partner_id) + " AND account_id="  + str(account.id) + " AND date <  '" + str(date_from) +  "'  " )
						else:
							self._cr.execute("select sum( COALESCE( debit, 0 ) )-sum( COALESCE( credit, 0 ) ) from account_move_line where partner_id in " + str(tuple(partner_ids) ) + " AND account_id="  + str(account.id) + " AND date <  '" + str(date_from) +  "'  " )
					else:
						self._cr.execute("select sum( COALESCE( debit, 0 ) )-sum(COALESCE( credit, 0 )) from account_move_line where account_id="  + str(account.id) + " AND date <  '" + str(date_from) +  "'  " )

					opening_balance = abs(self.env.cr.fetchone()[0] or 0.0)
					balance = balance + opening_balance
					the_opening_balance = opening_balance

					#revenue and expenses are not carried
					month = datetime.strptime(date_from,'%Y-%m-%d').month
					day = datetime.strptime(date_from,'%Y-%m-%d').day
					if account.code[:1] in ('1','2') and month == 1 and day == 1:
						balance -= the_opening_balance
						the_opening_balance = 0.00

				
				if balance:
					vals.append({
						'accounts_code' : account.parent_budget_item_id.code, 
						'account_name':  account.name,
						'debit':debit,
						'credit':credit,
						'balance':balance,
						'the_opening_balance' : the_opening_balance,
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
								'balance':balance,
								'the_opening_balance' : the_opening_balance, 
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

		partner_name = False
		if partner_id:

			partner_ids = []
			partner_ids.append( partner_id )
			for partner in self.env['res.partner'].search([('id','=',partner_id)]):
				if partner.parent_id:
					partner_ids.append( partner.parent_id.id )

				for child in partner.child_ids:
					partner_ids.append( child.id )

			partner_name = ''
			for partner in self.env['res.partner'].search([('id','in',partner_ids)]):
				partner_name = partner.name + ', ' + partner_name

			# partner_name = self.env['res.partner'].search([('id','in',partner_id)])[0].name 

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to, 
			'type':type,
			'company_id_logo': company_id_logo,
			'account_type' : account_type,
			'partner_name' : partner_name,
			'is_group_by_partners' : is_group_by_partners,
		}


		