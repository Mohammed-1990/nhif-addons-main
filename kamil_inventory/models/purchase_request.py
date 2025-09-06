
from odoo import models, fields, api, _



class purchaseRequest(models.Model):
	_inherit = 'purchase.request'


	need_request_id = fields.Many2one('need.requisition')


class purchaseOrder(models.Model):
	_inherit = 'purchase.order'


	stock_location_id = fields.Many2one('stock.location', string='Stock Location', domain=[('usage','ilike','internal')])