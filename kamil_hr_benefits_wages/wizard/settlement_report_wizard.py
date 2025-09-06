from odoo import models,fields,api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class settlementReportWizard(models.TransientModel):
	_name="settlement.report.wizard"

	date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)),required=True,)
	date_to = fields.Date(default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),required=True,)
	appoiontment_type =fields.Many2many('appointment.type', required=True,)
	
	# struct_id = fields.Many2one("hr.payroll.structure", required=True)
	type = fields.Selection([('main','Main Company'),('branch','Branchs')], required=True)



	@api.multi
	def get_report(self):
		"""Call when button 'Print' button clicked.
        """
		appoiontment_type = []
		for appointment in self.appoiontment_type:
			appoiontment_type.append(appointment.id)
		data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'appoiontment_type':appoiontment_type,
                'type':self.type,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
		return self.env.ref('kamil_hr_benefits_wages.settlement_report').report_action(self, data=data)
	
	