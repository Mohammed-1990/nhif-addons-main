# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class RatificationReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.ratification_template'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		partner_ids = data['from']['partner_ids']
		group_id = data['from']['group_id']

		is_draft = data['from']['is_draft']
		is_executed = data['from']['is_executed']
		is_approved = data['from']['is_approved']
		is_paid = data['from']['is_paid']
		is_canceled = data['from']['is_canceled']
		is_payment_created = data['from']['is_payment_created']
		is_payment_confirmed = data['from']['is_payment_confirmed']
		company_id_logo = self.env.user.company_id.logo

		domain = []

		if date_from:
			domain.append(('date','>=',date_from))
		if date_to:
			domain.append(('date','<=',date_to))
		if partner_ids:
			domain.append(('partner_id','in',partner_ids))

		states = []

		if is_draft:
			states.append( 'draft' )
		if is_executed:
			states.append( 'executed' )
		if is_approved:
			states.append( 'approved' )
		if is_paid:
			states.append( 'paid' )
		if is_canceled:
			states.append( 'canceled' )
		if is_payment_created:
			states.append( 'is_payment_created' )
		if is_payment_confirmed:
			states.append( 'is_payment_confirmed' )

		domain.append( ('state','in', states ) )

		
		docs = []	
		ratification = self.env['ratification.ratification'].search(domain)
		for ratification in self.env['ratification.ratification'].search( domain ):
			docs.append({
				'code':ratification.ref,
				'date':ratification.date,
				'partner':ratification.partner_id.name,
				'amount':ratification.amount,
				'description':ratification.name
				})

			
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'company_id_logo': company_id_logo,
			'date_to' : date_to, 
		}


		