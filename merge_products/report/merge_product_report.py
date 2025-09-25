#-*- coding:utf-8 -*-
from odoo import models,fields,api


class MergeProductReport(models.AbstractModel):
	_name = 'report.merge_products.merge_product_tem'

	company_id = fields.Many2one('res.company', string='Company', index=True,
								 default=lambda self: self.env.user.company_id.id)
	@api.model
	def _get_report_values(self, docids, data=None):

		domain = []
		date_from = data['form']['date_from']
		if date_from:
			domain.append(('date','>=',date_from))
		date_to = data['form']['date_to']
		if date_to:
			domain.append(('date','<=',date_to))
		docs = []
		
		merge_product = self.env['merge.product'].search(domain)
		for merge in merge_product:
			for line in merge.product_line_ids:
				if merge.state in 'finish':
					docs.append({'name':merge.name,
						'date':merge.date,
						'remove_product_id':line.remove_product_id.name,
						'remove_product_categ':line.remove_product_id.categ_id.name,
						'remove_product_location': line.remove_product_id.location_id.name,
						'remove_product_qty':line.remove_product_qty,
						'new_product_id':line.new_product_id.name,
						 'new_product_categ': line.new_product_id.categ_id.name,
						'new_product_location': line.new_product_id.location_id.name,
						 'new_product_qty': line.new_product_qty,
						 'total': line.new_product_qty + line.remove_product_qty,
						})


		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from':date_from,
			'date_to': date_to,
			'company_id':self.company_id.name,
		}
