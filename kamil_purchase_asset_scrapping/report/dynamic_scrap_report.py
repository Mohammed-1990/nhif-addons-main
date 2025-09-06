# -*- coding:utf-8 -*-
from odoo import models, fields, api

class DynamicScrapReport(models.AbstractModel):
	_name = "report.kamil_purchase_asset_scrapping.dynamic_scrap_template"

	@api.model
	def _get_report_values(self, docids, data=None):
		model = self.env['scrap.request'].browse(docids)
		docs = []
		val = []
		for line in model.asset_line_ids:
			for asset in line.asset_ids:
				val.append({
					'product_name': asset.product_id.name,
					'car_name': asset.product_id.car_name,
					'car_number': asset.product_id.car_number,
					'shasea_number': asset.product_id.shasea_number,
					'palte_number': asset.product_id.palte_number,
					'car_model': asset.product_id.car_model,
					'machine': asset.product_id.machine,
					'color': asset.product_id.car_color,
					'fuel': asset.product_id.fuel,
					'origin': asset.product_id.origin,
					'estimated_value': line.estimated_value,
					'sales_value': line.sales_value,
					'partner':line.partner_id.name,
					# 'branch':line.branch_id.id,
					})
		docs.append({
			'state':model.company_id.name,
			'auction_date':model.auction_date,
			'data':val
			})
		
		return {
			'doc_ids': model.ids,
			'doc_model': 'scrap.request',
			'docs': docs,
			
		}
