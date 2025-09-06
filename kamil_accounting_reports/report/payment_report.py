# -*- coding:utf-8 -*-
from odoo import models, fields, api


class PaymentReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.payment_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		budget_ids = data['from']['budget_ids']
		partner_ids = data['from']['partner_ids']
		company_id_logo = self.env.user.company_id.logo

		domain = [('state','!=','canceled')]

		if date_from:
			domain.append(('date','>=',date_from))
		if date_to:
			domain.append(('date','<=',date_to))
		if budget_ids:

			analytic_group_list = []
			accounts_list = []

			for analytic_account in self.env['account.analytic.account'].search([('id','in',budget_ids)]):
				for analytic_child in self.env['account.analytic.account'].search([('code','=ilike',analytic_account.code + '%' )]):
					analytic_group_list.append( analytic_child.id )
				
				for account_child in self.env['account.account'].search([('code','=ilike',analytic_account.code + '%' )]):
					accounts_list.append( account_child.id )


			budget = self.env['payment.ratification.line'].search(['|',('analytic_account_id','in',analytic_group_list),('account_id','in',accounts_list)])


			domain.append(('line_ids','in',budget.ids))
		if partner_ids:
			domain.append(('partner_id','in',partner_ids))
		
		docs = []	

		payment = self.env['ratification.payment'].search(domain)
		for line in payment:
			docs.append({
					'code':line.code,
					'date':line.date,
					'rat_code':line.ratification_id.ref,
					'type':line.payment_type,
					'document_number' : line.check_number,
					'amount':line.amount,
					'description':line.ratification_id.name
					})
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'company_id_logo': company_id_logo,
			'date_to' : date_to, 
		}


		