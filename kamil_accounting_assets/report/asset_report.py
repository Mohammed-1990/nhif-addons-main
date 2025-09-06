# *.* coding:utf-8 *.*
from odoo import models, fields, api
from datetime import datetime

class AssetReport(models.AbstractModel):
	_name = 'report.kamil_accounting_assets.asset_report_template'

	@api.model
	def _get_report_values(self, docids, data=None):

		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		category = data['from']['category']

		domain = []

		if date_from:
			domain.append(('date','<=',date_from))
		if date_to:
			domain.append(('date','>=',date_to))
		if category:
			domain.append(('category_id','=',category))

		docs = []	
		asset = self.env['account.asset.asset'].search(domain)
		for line in asset:
			docs.append({
					'name':line.name,
					'balance_1_1':line.balance_1_1,
					'additions':line.additions,
					'exclusion':line.exclusion,

					'annual_dep_ratio':line.annual_dep_ratio,
					'annual_dep_value':line.annual_dep_value,
					'value':line.value,

					})
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'date_to' : date_to, 
		}


		