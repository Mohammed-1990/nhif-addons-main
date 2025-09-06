#-*- coding:utf-8 -*-
from odoo import models,fields,api


class ItemCardReport(models.AbstractModel):
	_name = 'report.kamil_inventory.item_card_template'

	@api.model
	def _get_report_values(self, docids, data=None):
		company_id = data['from']['company_id']
		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		product_id = data['from']['product_id']
		domain = [
			('move_id.company_id', '=', company_id),
			('date', '>=', date_from),
			('date', '<=', date_to),
			('state', '=', 'done'),
		]
		if product_id:
			domain.append(('product_id', '=', product_id))
		location_id = data['from']['location_id']
		if location_id:
			domain.append('|')
			domain.append(('location_id', '=', location_id))
			domain.append(('location_dest_id', '=', location_id))

		docs = []
		move_ids = self.env['stock.move.line'].sudo().search(domain)
		for move in move_ids:
			Move = self.env['stock.move.line']

			if  move.location_id.usage in ['inventory','supplier']:
				domain_move_in = [
					('product_id', '=', move.product_id.id),
					('location_dest_id', '=', move.location_id.id),
					('date', '<=', move.date),
					('move_id.company_id','=',company_id),
					('state','=','done'),
					('id','<',move.id)
				]

				domain_move_out_done = [
					('product_id', '=', move.product_id.id),
					('location_id', '=', move.location_id.id),
					('date', '<=', move.date),
					('move_id.company_id','=',company_id),
					('state','=','done'),
					('id', '<', move.id)
				]

				moves_in_res_past = sum((item['qty_done']) for item in Move.search(domain_move_in))
				moves_out_res_past = sum((item['qty_done']) for item in Move.search(domain_move_out_done))
				if move.location_id.usage == 'inventory':
					qty_available = move.qty_done
					print('qty_available ',qty_available)
				else:
					qty_available = moves_in_res_past - moves_out_res_past
					print('qty_available1 ',qty_available)
					qty_available += move.qty_done
					print('qty_available2 ',qty_available)

				docs.append({
					'date':move.date,
					'product': move.product_id.name,
					'location': move.location_id.name,
					'amount_1':move.qty_done,
					'permission_no_1':move.picking_id.name or False,
					'amount_2':0.0,
					'permission_no_2':move.picking_id.name or False,
					'remaining': qty_available ,
					'partner':move.picking_id.partner_id.name or False

				})
			else:
				if  move.location_id.usage in ['customer','internal']:

					domain_move_in = [
						('product_id', '=', move.product_id.id),
						('location_dest_id', '=', move.location_id.id),
						('date', '<=', move.date),
						('move_id.company_id','=',company_id),
						('state','=','done'),
						('id','<',move.id)]

					domain_move_out_done = [
						('product_id', '=', move.product_id.id),
						('location_id', '=', move.location_id.id),
						('date', '<=', move.date),
						('move_id.company_id','=',company_id),
						('state','=','done'),
						('id','<',move.id)]

					moves_in_res_past = sum((item['qty_done']) for item in Move.search(domain_move_in))
					moves_out_res_past = sum((item['qty_done']) for item in Move.search(domain_move_out_done))
					qty_available = moves_in_res_past - moves_out_res_past

					docs.append({
						'date':move.date,
						'product':move.product_id.name,
						'location':move.location_id.name,
						'amount_1':0.0,
						'permission_no_1':move.picking_id.name or False,
						'amount_2':move.qty_done,
						'permission_no_2':move.picking_id.name or False,
						'remaining':qty_available - move.qty_done,
						'partner':move.picking_id.partner_id.name

						})


		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'product': self.env['product.product'].browse(product_id).name,
			'location':self.env['stock.location'].browse(location_id).name,
			'date_from': date_from,
			'date_to' : date_to, 
		} 
