# *.*  coding:utf-8 *.*
from odoo import models, fields, api

class AssetEvaluation(models.TransientModel):
	_name = 'asset.evaluation'
	_description = 'Asset Evaluation'

	evaluation = fields.Float('Evaluation', required="1")

	def action_evaluation(self):
		if self.evaluation:
			asset = self.env['account.asset.asset'].browse(self.env.context.get('active_id'))
			asset.asset_evaluation = self.evaluation
			value = 0.0
			account = self.env['account.account']
			if asset.asset_evaluation > asset.value_residual:
				value = asset.asset_evaluation - asset.value_residual
				account = asset.category_id.account_loss_id
			else:
				value = asset.value_residual - asset.asset_evaluation
				account = asset.category_id.account_profit_id
			asset.value = self.evaluation
			# asset.compute_depreciation_board()
			asset.evaluation_asset(value=value, account=account)