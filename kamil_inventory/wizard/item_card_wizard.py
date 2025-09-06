# -*- coding:utf-8 -*-
from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class ItemCardWizard(models.TransientModel):
	_name = 'item.card.wizard'
	_description = 'Item Card Wizrd'


	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
	product_id = fields.Many2one('product.product','Product')
	location_id = fields.Many2one('stock.location','Location')
	company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id.id)


	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		data = {
			'ids': self.ids,
			'model': self._name,
			'from': {
				'date_from': self.date_from,
				'date_to' : self.date_to,
				'location_id' : self.location_id.id,
				'product_id':self.product_id.id,
				'company_id':self.company_id.id
			},
		}

		return self.env.ref('kamil_inventory.item_card_report').report_action(self, data=data)
	

		