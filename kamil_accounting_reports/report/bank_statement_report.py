# -*- coding:utf-8 -*-
from odoo import models, fields, api


class PaymentReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.bank_statement_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		bank_id = data['from']['bank_id']
		company_id_logo = self.env.user.company_id.logo


		domain = []

		if date_from:
			domain.append(('date','>=',date_from))
		if date_to:
			domain.append(('date','<=',date_to))
		if bank_id:
			account = self.env['account.journal'].search([('id','=',bank_id)])
			domain.append(('account_id','=',account.default_debit_account_id.id))
		
		bank_name_id = self.env['account.journal'].search([('id','=',bank_id)])

		self._cr.execute("select sum( COALESCE( debit, 0 ) )-sum( COALESCE( credit, 0 ) ) from account_move_line where account_id="  + str(bank_name_id.default_debit_account_id.id) + " AND date < '" + str(date_from) + "'  " )
		opening_balance = self.env.cr.fetchone()[0] or 0.0

		docs = []	

		total_debit = total_credit = 0

		move = self.env['account.move.line'].search(domain, order="document_number desc")
		for line in move:

			doc_type = 'قيد'
			if line.move_id.ratification_payment_id:
				if line.move_id.ratification_payment_id.payment_type == 'Cheque':
					doc_type = 'شيك'
				if line.move_id.ratification_payment_id.payment_type == 'cash':
					doc_type = 'نقد'
				if line.move_id.ratification_payment_id.payment_type == 'bank_transfer':
					doc_type = 'تحويل بنكي'
				if line.move_id.ratification_payment_id.payment_type == 'counter_cheque':
					doc_type = 'شيك مصرفي'
			if line.move_id.collection_id:
				if line.move_id.collection_id.collection_type == 'Cheque':
					doc_type = 'شيك'
				if line.move_id.collection_id.collection_type == 'cash':
					doc_type = 'نقد'
				if line.move_id.collection_id.collection_type == 'bank_transfer':
					doc_type = 'تحويل بنكي'
				if line.move_id.collection_id.collection_type == 'counter_cheque':
					doc_type = 'شيك مصرفي'

			docs.append({
					'date':line.date,
					'doc_type': doc_type ,
					'document_number':line.document_number,
					'debit':line.debit,
					'credit':line.credit,
					'partner':line.partner_id.name,
					'description':line.name
					})
			total_debit = total_debit + line.debit
			total_credit = total_credit + line.credit
		
		if opening_balance < 0:
			total_credit = total_credit + opening_balance
		else:
			total_debit = total_debit + opening_balance

		balance = total_debit - total_credit

		docs = list(reversed(docs))

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to,
			'company_id_logo': company_id_logo,
			'bank_name' : bank_name_id.name,
			'opening_balance' : opening_balance,
			'balance' : balance,
		}


		