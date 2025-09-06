# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AccountMoveReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.account_move_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		group_ids = data['from']['group_ids']
		company_id_logo = self.env.user.company_id.logo

		domain = []
		account_list = []


		if date_from:
			domain.append(('date','>=',date_from))
		if date_to:
			domain.append(('date','<=',date_to))
		
		if group_ids:
			accounts = self.env['account.account'].search([('id','in',group_ids)])
			for account in accounts:
				record = self.env['account.account'].search([('code','=like',(account.code + '%'))])
				for rec in record:
					account_list.append(rec.id)
			

		
		docs = []	
		accounts = self.env['account.move'].search(domain)
		for line in accounts:
			if group_ids:
				for rec in line.line_ids:	
					if rec.account_id.id in account_list:
						docs.append({
							'date':line.date,
							'name':line.name,
							'amount':line.amount,
							'description':line.ref
							})

			else:
				docs.append({
					'date':line.date,
					'name':line.name,
					'amount':line.amount,
					'description':line.ref
					})


		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'company_id_logo': company_id_logo,
			'date_from': date_from,
			'date_to' : date_to, 
		}


		