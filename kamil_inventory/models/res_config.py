from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils, float_compare
from datetime import datetime
from dateutil.relativedelta import relativedelta



class KamilCofigurationSetting(models.TransientModel):
	_inherit = 'res.config.settings'

	default_periodic_interval = fields.Integer(default_model='stock.inventory')



	@api.multi
	def set_values(self):
		super(KamilCofigurationSetting, self).set_values()
		periodic_record = self.env['ir.cron'].search([('name','ilike','Periodic Inventory Adjustment')],limit=1)
		next_date = datetime.today() + relativedelta(months=+(self.default_periodic_interval))
		periodic_record.update({'interval_number': self.default_periodic_interval,
								'nextcall': next_date})
