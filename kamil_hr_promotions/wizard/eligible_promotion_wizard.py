from odoo import models,fields,api
from datetime import date , datetime
from dateutil.relativedelta import relativedelta

class eligiblePromotion(models.TransientModel):
	_name="eligible.promotion.wizard"

	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)),track_visibility="onchange",copy=False , required=True,)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),track_visibility="onchange",copy=False , required=True,)

	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_hr_promotions.eligible_promotion_report').report_action(self, data=data)
	
	