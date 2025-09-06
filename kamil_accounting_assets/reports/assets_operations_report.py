# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime

class AssetsReport(models.AbstractModel):
	_name = 'report.kamil_accounting_assets.assets_operations_template'


	@api.model
	def _get_report_values(self, docids, data=None):
		operation_type = data['form']['operation_type']
		dispose_type = data['form']['dispose_type']

		docs = []

		for operation in self.env['account.asset.operation'].search([('type','=',operation_type)]):
			if operation_type == 'dispose':
				if dispose_type == operation.dispose_type:

					docs.append({
						'asset_code' : operation.asset_id.code,
						'asset_name' : operation.asset_id.product_id.name,
						'admin_id' : operation.asset_id.admin_id.name ,
						'dept_id' : operation.asset_id.dept_id.name,
						'category_id' : operation.asset_id.category_id.name,
						'purchase_date' :  operation.asset_id.date,
						'value' : operation.asset_id.value,
						'value_residual' : operation.asset_id.value_residual,
						'annual_dep_ratio' : operation.asset_id.annual_dep_ratio,
						'annual_dep_value' : operation.asset_id.annual_dep_value,
						'operation_value' : operation.value,
						'operation_date' : operation.date,
					})
			else:
				docs.append({
					'asset_code' : operation.asset_id.code,
					'asset_name' : operation.asset_id.product_id.name,
					'admin_id' : operation.asset_id.admin_id.name ,
					'dept_id' : operation.asset_id.dept_id.name,
					'category_id' : operation.asset_id.category_id.name,
					'purchase_date' :  operation.asset_id.date,
					'value' : operation.asset_id.value,
					'value_residual' : operation.asset_id.value_residual,
					'annual_dep_ratio' : operation.asset_id.annual_dep_ratio,
					'annual_dep_value' : operation.asset_id.annual_dep_value,
					'operation_value' : operation.value,
					'operation_date' : operation.date,
					})





		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date': date,
			'test' : 'this is a test',
			'operation_type' : operation_type,
			'dispose_type' : dispose_type,
		}