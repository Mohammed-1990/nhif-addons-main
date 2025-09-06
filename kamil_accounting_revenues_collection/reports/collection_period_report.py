
# -*- coding:utf-8 -*-
from odoo import models, fields, api


class CollectionPeriodReport(models.AbstractModel):
	_name = 'report.kamil_accounting_revenues_collection.collection_period_report'


	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']

		domain = []

		if date_from:
			domain.append(('date','<=',date_from))
		if date_to:
			domain.append(('date','>=',date_to))
		
		docs = []	
		collection_period = self.env['collection.collection'].search(domain)
		for line in collection_period:
			for rec in line.line_ids:
				docs.append({
						'account':line.collection_id.item,
						'estimated_collection':line.collection_id.ref,
						'acctual_collected':line.collection_id.????,
						'deviation':line.collection_id.????,
						'percentage':line.collection_id.name
						})
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to, 
		}


		